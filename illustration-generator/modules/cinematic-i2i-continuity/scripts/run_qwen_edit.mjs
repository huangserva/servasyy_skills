#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { atomicWrite, fileSha256, submissionFingerprint, submitPromptWithReceipt, updateSubmissionReceipt } from "./comfy_submit_lock.mjs";

function argsOf(values) {
  const args = {};
  for (let i = 0; i < values.length; i += 2) {
    if (!values[i]?.startsWith("--") || values[i + 1] === undefined) throw new Error(`Invalid argument near ${values[i]}`);
    args[values[i].slice(2)] = values[i + 1];
  }
  return args;
}

function imageSize(buffer) {
  if (buffer.subarray(1, 4).toString() === "PNG") return [buffer.readUInt32BE(16), buffer.readUInt32BE(20)];
  if (buffer[0] === 0xff && buffer[1] === 0xd8) {
    let offset = 2;
    while (offset + 9 < buffer.length) {
      if (buffer[offset] !== 0xff) { offset += 1; continue; }
      const marker = buffer[offset + 1];
      const length = buffer.readUInt16BE(offset + 2);
      if ([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf].includes(marker)) return [buffer.readUInt16BE(offset + 7), buffer.readUInt16BE(offset + 5)];
      offset += 2 + length;
    }
  }
  throw new Error("Only PNG and JPEG dimensions are supported");
}

const args = argsOf(process.argv.slice(2));
for (const key of ["source", "output", "prompt"]) if (!args[key]) throw new Error(`--${key} is required`);
const api = (args.api || process.env.COMFY_URL || "http://127.0.0.1:8188").replace(/\/$/, "");
const unet = args.unet || "qwen_image_edit_2511_fp8_lightning_4steps.safetensors";
const steps = Number(args.steps || (unet.includes("lightning") ? 4 : 20));
const cfg = Number(args.cfg || (unet.includes("lightning") ? 1 : 4));
const denoise = Number(args.denoise || 1);
const negative = args.negative || "";
const seed = Number(args.seed || 42);
const prepareMemory = !["0", "false", "no"].includes(String(args["prepare-memory"] || "true").toLowerCase());
const pollMs = Number(process.env.COMFY_POLL_MS || 3000);
const timeoutMs = Number(process.env.COMFY_TIMEOUT_MS || 900000);
const clip = args.clip || "qwen_2.5_vl_7b_fp8_scaled.safetensors";
const vae = args.vae || "qwen_image_vae.safetensors";

async function getJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    signal: options.signal || AbortSignal.timeout(30000),
  });
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  return response.json();
}

async function upload(file) {
  const form = new FormData();
  const name = `${crypto.randomUUID()}${path.extname(file).toLowerCase() || ".png"}`;
  form.append("image", new Blob([fs.readFileSync(file)]), name);
  form.append("type", "input");
  form.append("overwrite", "false");
  const item = await getJson(`${api}/upload/image`, { method: "POST", body: form });
  return item.subfolder ? `${item.subfolder}/${item.name}` : item.name;
}

async function releaseCachedModels() {
  if (!prepareMemory) return;
  const queue = await getJson(`${api}/queue`);
  const running = queue.queue_running || [];
  const pending = queue.queue_pending || [];
  if (running.length || pending.length) {
    throw new Error(`Refusing to unload shared ComfyUI models while queue is active: running=${running.length} pending=${pending.length}`);
  }
  const response = await fetch(`${api}/free`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ unload_models: true, free_memory: true }),
    signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) throw new Error(`ComfyUI memory release failed: ${response.status} ${await response.text()}`);
}

const info = await getJson(`${api}/object_info`);
for (const node of ["TextEncodeQwenImageEditPlus", "FluxKontextMultiReferenceLatentMethod", "ModelSamplingAuraFlow", "CFGNorm"]) {
  if (!info[node]) throw new Error(`Missing Qwen Edit node: ${node}`);
}
if (!(info.UNETLoader?.input?.required?.unet_name?.[0] || []).includes(unet)) throw new Error(`Missing UNET: ${unet}`);
if (!(info.CLIPLoader?.input?.required?.clip_name?.[0] || []).includes(clip)) throw new Error(`Missing CLIP: ${clip}`);
if (!(info.VAELoader?.input?.required?.vae_name?.[0] || []).includes(vae)) throw new Error(`Missing VAE: ${vae}`);

const sourcePath = path.resolve(args.source);
const sourceDimensions = imageSize(fs.readFileSync(sourcePath));
const fingerprint = submissionFingerprint({
  adapter: "qwen-edit-v1", source_sha256: fileSha256(sourcePath),
  refs: [args.ref1, args.ref2].filter(Boolean).map((file) => fileSha256(path.resolve(file))),
  prompt: args.prompt, negative, unet, clip, vae, steps, cfg, denoise, seed,
});
const sourceName = await upload(sourcePath);
const refs = [];
for (const key of ["ref1", "ref2"]) if (args[key]) refs.push(await upload(path.resolve(args[key])));
const workflow = {
  "1": { class_type: "LoadImage", inputs: { image: sourceName } },
  "3": { class_type: "VAELoader", inputs: { vae_name: vae } },
  "4": { class_type: "UNETLoader", inputs: { unet_name: unet, weight_dtype: "default" } },
  "5": { class_type: "ModelSamplingAuraFlow", inputs: { model: ["4", 0], shift: 3.1 } },
  "6": { class_type: "CFGNorm", inputs: { model: ["5", 0], strength: 1 } },
  "7": { class_type: "CLIPLoader", inputs: { clip_name: clip, type: "qwen_image", device: "default" } },
  "8": { class_type: "TextEncodeQwenImageEditPlus", inputs: { clip: ["7", 0], vae: ["3", 0], image1: ["1", 0], prompt: args.prompt } },
  "9": { class_type: "FluxKontextMultiReferenceLatentMethod", inputs: { conditioning: ["8", 0], reference_latents_method: "index_timestep_zero" } },
  "10": { class_type: "TextEncodeQwenImageEditPlus", inputs: { clip: ["7", 0], vae: ["3", 0], image1: ["1", 0], prompt: negative } },
  "11": { class_type: "FluxKontextMultiReferenceLatentMethod", inputs: { conditioning: ["10", 0], reference_latents_method: "index_timestep_zero" } },
  "12": { class_type: "VAEEncode", inputs: { pixels: ["1", 0], vae: ["3", 0] } },
  "13": { class_type: "KSampler", inputs: { model: ["6", 0], seed, steps, cfg, sampler_name: "euler", scheduler: "simple", positive: ["9", 0], negative: ["11", 0], latent_image: ["12", 0], denoise } },
  "14": { class_type: "VAEDecode", inputs: { samples: ["13", 0], vae: ["3", 0] } },
  "15": { class_type: "SaveImage", inputs: { images: ["14", 0], filename_prefix: path.parse(args.output).name } }
};
refs.forEach((name, index) => {
  const load = String(16 + index * 2);
  const scale = String(17 + index * 2);
  workflow[load] = { class_type: "LoadImage", inputs: { image: name } };
  workflow[scale] = { class_type: "FluxKontextImageScale", inputs: { image: [load, 0] } };
  workflow["8"].inputs[`image${index + 2}`] = [scale, 0];
  workflow["10"].inputs[`image${index + 2}`] = [scale, 0];
});

const output = path.resolve(args.output);
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
const outputBuffer = Buffer.from(await response.arrayBuffer());
const outputDimensions = imageSize(outputBuffer);
if (outputDimensions[0] !== sourceDimensions[0] || outputDimensions[1] !== sourceDimensions[1]) {
  throw new Error(`Qwen output changed canvas ${sourceDimensions.join("x")} -> ${outputDimensions.join("x")}; reject before mask compositing.`);
}
atomicWrite(output, outputBuffer);
atomicWrite(`${output}.json`, `${JSON.stringify({ source: args.source, refs: [args.ref1, args.ref2].filter(Boolean), prompt: args.prompt, negative, prompt_id: queued.prompt_id, unet, clip, vae, steps, cfg, denoise, seed, prepare_memory: prepareMemory }, null, 2)}\n`);
updateSubmissionReceipt(output, fingerprint, { status: "complete", output_sha256: fileSha256(output), completed_at: new Date().toISOString() });
console.log(output);
