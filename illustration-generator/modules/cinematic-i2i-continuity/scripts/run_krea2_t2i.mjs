#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { atomicWrite, fileSha256, submissionFingerprint, submitPromptWithReceipt, updateSubmissionReceipt } from "./comfy_submit_lock.mjs";

function argsOf(values) {
  const args = {};
  for (let index = 0; index < values.length; index += 2) {
    if (!values[index]?.startsWith("--") || values[index + 1] === undefined) throw new Error(`Invalid argument near ${values[index]}`);
    args[values[index].slice(2)] = values[index + 1];
  }
  return args;
}

const args = argsOf(process.argv.slice(2));
for (const key of ["output", "prompt", "width", "height"]) if (!args[key]) throw new Error(`--${key} is required`);
const api = (args.api || process.env.COMFY_URL || "http://127.0.0.1:8188").replace(/\/$/, "");
const output = path.resolve(args.output);
const width = Number(args.width);
const height = Number(args.height);
const seed = Number(args.seed || 42);
const steps = Number(args.steps || 8);
const cfg = Number(args.cfg || 1);
const unet = args.unet || "krea2_turbo_fp8.safetensors";
const clip = args.clip || "qwen3vl_4b_fp8_scaled.safetensors";
const vae = args.vae || "qwen_image_vae.safetensors";
const sampler = args.sampler || "er_sde";
const scheduler = args.scheduler || "simple";
const lora = args.lora || "";
const loraStrength = Number(args["lora-strength"] || 1);
const hiresWidth = Number(args["hires-width"] || 0);
const hiresHeight = Number(args["hires-height"] || 0);
const hiresSteps = Number(args["hires-steps"] || 6);
const hiresSampler = args["hires-sampler"] || "er_sde";
const hiresScheduler = args["hires-scheduler"] || "simple";
const hiresDenoise = Number(args["hires-denoise"] || 0.6);
const hiresUpscaleMethod = args["hires-upscale-method"] || "bicubic";
const hires = hiresWidth > 0 && hiresHeight > 0;
const prepareMemory = !["0", "false", "no"].includes(String(args["prepare-memory"] || "true").toLowerCase());
const pollMs = Number(process.env.COMFY_POLL_MS || 3000);
const timeoutMs = Number(process.env.COMFY_TIMEOUT_MS || 900000);
const requestTimeoutMs = Number(process.env.COMFY_REQUEST_TIMEOUT_MS || 30000);
const fingerprint = submissionFingerprint({
  adapter: "krea2-t2i-v1", prompt: args.prompt, width, height, seed, steps, cfg,
  unet, clip, vae, sampler, scheduler, lora, lora_strength: loraStrength,
  hires_width: hiresWidth, hires_height: hiresHeight, hires_steps: hiresSteps,
  hires_sampler: hiresSampler, hires_scheduler: hiresScheduler,
  hires_denoise: hiresDenoise, hires_upscale_method: hiresUpscaleMethod,
});

async function getJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    signal: options.signal || AbortSignal.timeout(requestTimeoutMs),
  });
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  return response.json();
}

async function releaseCachedModels() {
  if (!prepareMemory) return;
  const queue = await getJson(`${api}/queue`);
  const running = queue.queue_running || [];
  const pending = queue.queue_pending || [];
  if (running.length || pending.length) throw new Error(`Refusing to unload shared ComfyUI models while queue is active: running=${running.length} pending=${pending.length}`);
  const response = await fetch(`${api}/free`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ unload_models: true, free_memory: true }),
    signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) throw new Error(`ComfyUI memory release failed: ${response.status} ${await response.text()}`);
}

const info = await getJson(`${api}/object_info`);
const clipTypes = info.CLIPLoader?.input?.required?.type?.[0] || [];
const models = info.UNETLoader?.input?.required?.unet_name?.[0] || [];
const clips = info.CLIPLoader?.input?.required?.clip_name?.[0] || [];
const vaes = info.VAELoader?.input?.required?.vae_name?.[0] || [];
const loras = info.LoraLoaderModelOnly?.input?.required?.lora_name?.[0] || [];
if (!clipTypes.includes("krea2") || !models.includes(unet) || !clips.includes(clip) || !vaes.includes(vae) || (lora && !loras.includes(lora))) {
  throw new Error(`Krea2 T2I capability probe failed: ${JSON.stringify({ clipType: clipTypes.includes("krea2"), unet: models.includes(unet), clip: clips.includes(clip), vae: vaes.includes(vae), lora: !lora || loras.includes(lora) })}`);
}

const samplerModel = lora ? ["10", 0] : ["1", 0];
const finalSamples = hires ? ["12", 0] : ["7", 0];
const workflow = {
  "1": { class_type: "UNETLoader", inputs: { unet_name: unet, weight_dtype: "default" } },
  "2": { class_type: "CLIPLoader", inputs: { clip_name: clip, type: "krea2", device: "default" } },
  "3": { class_type: "VAELoader", inputs: { vae_name: vae } },
  "4": { class_type: "CLIPTextEncode", inputs: { text: args.prompt, clip: ["2", 0] } },
  "5": { class_type: "ConditioningZeroOut", inputs: { conditioning: ["4", 0] } },
  "6": { class_type: "EmptyLatentImage", inputs: { width, height, batch_size: 1 } },
  "7": { class_type: "KSampler", inputs: { model: samplerModel, seed, steps, cfg, sampler_name: sampler, scheduler, positive: ["4", 0], negative: ["5", 0], latent_image: ["6", 0], denoise: 1 } },
  "8": { class_type: "VAEDecode", inputs: { samples: finalSamples, vae: ["3", 0] } },
  "9": { class_type: "SaveImage", inputs: { images: ["8", 0], filename_prefix: path.parse(output).name } }
};
if (lora) workflow["10"] = { class_type: "LoraLoaderModelOnly", inputs: { model: ["1", 0], lora_name: lora, strength_model: loraStrength } };
if (hires) {
  workflow["11"] = { class_type: "LatentUpscale", inputs: { samples: ["7", 0], upscale_method: hiresUpscaleMethod, width: hiresWidth, height: hiresHeight, crop: "disabled" } };
  workflow["12"] = { class_type: "KSampler", inputs: { model: samplerModel, seed, steps: hiresSteps, cfg, sampler_name: hiresSampler, scheduler: hiresScheduler, positive: ["4", 0], negative: ["5", 0], latent_image: ["11", 0], denoise: hiresDenoise } };
}
const queued = await submitPromptWithReceipt({ api, output, fingerprint, workflow, releaseCachedModels });
let history;
const deadline = Date.now() + timeoutMs;
for (;;) {
  if (Date.now() >= deadline) {
    updateSubmissionReceipt(output, fingerprint, { status: "poll_timeout", timed_out_at: new Date().toISOString() });
    throw new Error(`ComfyUI timed out after ${timeoutMs}ms; receipt preserved for resume`);
  }
  await new Promise((resolve) => setTimeout(resolve, pollMs));
  const payload = await getJson(`${api}/history/${queued.prompt_id}`);
  if (!payload[queued.prompt_id]) continue;
  if (payload[queued.prompt_id].status?.status_str === "error") {
    updateSubmissionReceipt(output, fingerprint, { status: "error", error_at: new Date().toISOString() });
    throw new Error(JSON.stringify(payload[queued.prompt_id].status));
  }
  if (payload[queued.prompt_id].outputs) { history = payload[queued.prompt_id]; break; }
}
const image = Object.values(history.outputs).flatMap((item) => item.images || []).at(-1);
if (!image) throw new Error("No output image");
const query = new URLSearchParams({ filename: image.filename, subfolder: image.subfolder || "", type: image.type || "output" });
const response = await fetch(`${api}/view?${query}`, {
  signal: AbortSignal.timeout(120000),
});
if (!response.ok) throw new Error(`download ${response.status}`);
atomicWrite(output, Buffer.from(await response.arrayBuffer()));
atomicWrite(`${output}.json`, `${JSON.stringify({ prompt: args.prompt, prompt_id: queued.prompt_id, seed, steps, cfg, width, height, unet, clip, vae, sampler, scheduler, lora, lora_strength: loraStrength, hires_width: hiresWidth, hires_height: hiresHeight, hires_steps: hiresSteps, hires_sampler: hiresSampler, hires_scheduler: hiresScheduler, hires_denoise: hiresDenoise, hires_upscale_method: hiresUpscaleMethod, prepare_memory: prepareMemory }, null, 2)}\n`);
updateSubmissionReceipt(output, fingerprint, { status: "complete", output_sha256: fileSha256(output), completed_at: new Date().toISOString() });
console.log(output);
