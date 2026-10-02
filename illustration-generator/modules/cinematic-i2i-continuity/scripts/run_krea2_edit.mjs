#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { atomicWrite, fileSha256, submissionFingerprint, submitPromptWithReceipt, updateSubmissionReceipt } from "./comfy_submit_lock.mjs";

function parseArgs(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith("--")) throw new Error(`Unexpected argument: ${key}`);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${key}`);
    result[key.slice(2)] = value;
    index += 1;
  }
  return result;
}

function imageSize(buffer) {
  if (buffer.subarray(1, 4).toString() === "PNG") {
    return [buffer.readUInt32BE(16), buffer.readUInt32BE(20)];
  }
  if (buffer[0] === 0xff && buffer[1] === 0xd8) {
    let offset = 2;
    while (offset < buffer.length) {
      if (buffer[offset] !== 0xff) { offset += 1; continue; }
      const marker = buffer[offset + 1];
      const length = buffer.readUInt16BE(offset + 2);
      if ([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf].includes(marker)) {
        return [buffer.readUInt16BE(offset + 7), buffer.readUInt16BE(offset + 5)];
      }
      offset += 2 + length;
    }
  }
  throw new Error("Only PNG and JPEG source dimensions are supported");
}

const args = parseArgs(process.argv.slice(2));
for (const key of ["mode", "source", "output", "prompt"]) {
  if (!args[key]) throw new Error(`--${key} is required`);
}
if (!['identity', 'ostris'].includes(args.mode)) throw new Error("--mode must be identity or ostris");

const api = (args.api || process.env.COMFY_URL || "http://127.0.0.1:8188").replace(/\/$/, "");
const source = path.resolve(args.source);
const output = path.resolve(args.output);
const sourceBuffer = fs.readFileSync(source);
const poseReference = args["pose-reference"] ? path.resolve(args["pose-reference"]) : "";
const poseReferenceBuffer = poseReference ? fs.readFileSync(poseReference) : null;
const [sourceWidth, sourceHeight] = imageSize(sourceBuffer);
const width = Number(args.width || sourceWidth);
const height = Number(args.height || sourceHeight);
const seed = Number(args.seed || 42);
const pollMs = Number(process.env.COMFY_POLL_MS || 3000);
const timeoutMs = Number(process.env.COMFY_TIMEOUT_MS || 900000);
const requestTimeoutMs = Number(process.env.COMFY_REQUEST_TIMEOUT_MS || 30000);
const steps = Number(args.steps || (args.mode === "identity" ? 8 : 10));
const cfg = Number(args.cfg || 1);
const strength = Number(args.strength || (args.mode === "identity" ? 1 : 0.8));
const mutable = String(args.mutable || "").trim();
const prepareMemory = !["0", "false", "no"].includes(String(args["prepare-memory"] || "true").toLowerCase());
const sourceAr = sourceWidth / sourceHeight;
const outputAr = width / height;
if (args.mode === "identity" && Math.abs(sourceAr - outputAr) / outputAr > 0.01) {
  throw new Error(`Identity mode refuses AR mismatch ${sourceWidth}x${sourceHeight} -> ${width}x${height}. Letterbox the master first; do not crop.`);
}
if (args.mode === "identity" && args.prompt.length > 500) {
  throw new Error("Identity prompt is too long. Keep it to the scene, camera, and lighting delta.");
}

async function jsonFetch(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    signal: options.signal || AbortSignal.timeout(requestTimeoutMs),
  });
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  return response.json();
}

async function upload(file, buffer = fs.readFileSync(file)) {
  const form = new FormData();
  const uniqueName = `${crypto.randomUUID()}${path.extname(file).toLowerCase() || ".png"}`;
  form.append("image", new Blob([buffer]), uniqueName);
  form.append("type", "input");
  form.append("overwrite", "false");
  const result = await jsonFetch(`${api}/upload/image`, { method: "POST", body: form });
  return result.subfolder ? `${result.subfolder}/${result.name}` : result.name;
}

async function releaseCachedModels() {
  if (!prepareMemory) return;
  const queue = await jsonFetch(`${api}/queue`);
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

const objectInfo = await jsonFetch(`${api}/object_info`);
const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const capabilities = JSON.parse(fs.readFileSync(path.join(skillRoot, "references", "capabilities.json"), "utf8"));
const capability = capabilities[args.mode === "identity" ? "krea2-identity" : "krea2-ostris"];
const requiredNodes = args.mode === "identity"
  ? ["Krea2EditModelPatch", "Krea2EditGroundedEncode"]
  : ["Krea2OstrisEditModelPatch", "TextEncodeKrea2OstrisEdit"];
const missingNodes = requiredNodes.filter((name) => !objectInfo[name]);
const clipTypes = objectInfo.CLIPLoader?.input?.required?.type?.[0] || [];
const unet = args.unet || "krea2_turbo_fp8.safetensors";
const clip = args.clip || "qwen3vl_4b_fp8_scaled.safetensors";
const vae = args.vae || "qwen_image_vae.safetensors";
const lora = args.lora || (args.mode === "identity" ? "krea2_identity_edit_v1.safetensors" : "krea2_lora-edit-step00005310.safetensors");
const fingerprint = submissionFingerprint({
  adapter: `krea2-edit-${args.mode}-v2`, source_sha256: fileSha256(source),
  pose_reference_sha256: poseReference ? fileSha256(poseReference) : "",
  prompt: args.prompt, mutable, width, height, seed, steps, cfg, strength, unet, clip, vae, lora,
});
const models = objectInfo.UNETLoader?.input?.required?.unet_name?.[0] || [];
const clips = objectInfo.CLIPLoader?.input?.required?.clip_name?.[0] || [];
const vaes = objectInfo.VAELoader?.input?.required?.vae_name?.[0] || [];
const loras = objectInfo.LoraLoaderModelOnly?.input?.required?.lora_name?.[0] || [];
const signatureErrors = Object.entries(capability.node_required_inputs || {}).flatMap(([node, fields]) => {
  const required = objectInfo[node]?.input?.required || {};
  return fields.filter((field) => !(field in required)).map((field) => `${node}.${field}`);
});
if (missingNodes.length || signatureErrors.length || !clipTypes.includes("krea2") || !models.includes(unet) || !clips.includes(clip) || !vaes.includes(vae) || !loras.includes(lora)) {
  throw new Error(`Krea2 capability probe failed: ${JSON.stringify({ missingNodes, signatureErrors, clipType: clipTypes.includes("krea2"), unet: models.includes(unet), clip: clips.includes(clip), vae: vaes.includes(vae), lora: loras.includes(lora) })}`);
}

const imageName = await upload(source, sourceBuffer);
const poseReferenceName = poseReference ? await upload(poseReference, poseReferenceBuffer) : "";
let workflow;

if (args.mode === "identity") {
  const preservation = mutable
    ? `Keep the same person face geometry, age, skin identity, and body proportions. Preserve every source attribute except these explicitly mutable attributes: ${mutable}.`
    : "Keep the same person face, hair, body proportions, and clothing exactly.";
  const instruction = `Create a photorealistic photo of this person in: ${args.prompt}. ${preservation} Relight the person to match the new environment.`;
  const negative = "different person, face swap, identity drift, duplicate person, multiple people, crop, watermark, text, logo";
  workflow = {
    "1": { class_type: "UNETLoader", inputs: { unet_name: unet, weight_dtype: "default" } },
    "2": { class_type: "CLIPLoader", inputs: { clip_name: clip, type: "krea2", device: "default" } },
    "3": { class_type: "VAELoader", inputs: { vae_name: vae } },
    "4": { class_type: "LoraLoaderModelOnly", inputs: { model: ["1", 0], lora_name: lora, strength_model: strength } },
    "5": { class_type: "LoadImage", inputs: { image: imageName } },
    "6": { class_type: "VAEEncode", inputs: { pixels: ["5", 0], vae: ["3", 0] } },
    "7": { class_type: "Krea2EditModelPatch", inputs: { model: ["4", 0], source_latent: ["6", 0] } },
    "8": { class_type: "Krea2EditGroundedEncode", inputs: { clip: ["2", 0], prompt: instruction, image: ["5", 0], grounding_px: Number(args["grounding-px"] || Math.max(width, height, 1024)) } },
    "9": { class_type: "Krea2EditGroundedEncode", inputs: { clip: ["2", 0], prompt: negative, image: ["5", 0], grounding_px: Number(args["grounding-px"] || Math.max(width, height, 1024)) } },
    "10": { class_type: "EmptySD3LatentImage", inputs: { width, height, batch_size: 1 } },
    "11": { class_type: "KSampler", inputs: { model: ["7", 0], seed, steps, cfg, sampler_name: "euler", scheduler: "simple", positive: ["8", 0], negative: ["9", 0], latent_image: ["10", 0], denoise: 1 } },
    "12": { class_type: "VAEDecode", inputs: { samples: ["11", 0], vae: ["3", 0] } },
    "13": { class_type: "SaveImage", inputs: { images: ["12", 0], filename_prefix: path.parse(output).name } }
  };
} else {
  workflow = {
    "1": { class_type: "LoadImage", inputs: { image: imageName } },
    "2": { class_type: "FluxKontextImageScale", inputs: { image: ["1", 0] } },
    "3": { class_type: "VAELoader", inputs: { vae_name: vae } },
    "4": { class_type: "UNETLoader", inputs: { unet_name: unet, weight_dtype: "default" } },
    "5": { class_type: "Krea2OstrisEditModelPatch", inputs: { model: ["4", 0] } },
    "6": { class_type: "LoraLoaderModelOnly", inputs: { model: ["5", 0], lora_name: lora, strength_model: strength } },
    "7": { class_type: "CLIPLoader", inputs: { clip_name: clip, type: "krea2", device: "default" } },
    "8": { class_type: "TextEncodeKrea2OstrisEdit", inputs: { clip: ["7", 0], vae: ["3", 0], image1: ["2", 0], prompt: args.prompt } },
    "9": { class_type: "FluxKontextMultiReferenceLatentMethod", inputs: { conditioning: ["8", 0], reference_latents_method: "index_timestep_zero" } },
    "10": { class_type: "TextEncodeKrea2OstrisEdit", inputs: { clip: ["7", 0], vae: ["3", 0], image1: ["2", 0], prompt: "" } },
    "11": { class_type: "FluxKontextMultiReferenceLatentMethod", inputs: { conditioning: ["10", 0], reference_latents_method: "index_timestep_zero" } },
    "12": { class_type: "EmptyLatentImage", inputs: { width, height, batch_size: 1 } },
    "13": { class_type: "KSampler", inputs: { model: ["6", 0], seed, steps, cfg, sampler_name: "euler", scheduler: "simple", positive: ["9", 0], negative: ["11", 0], latent_image: ["12", 0], denoise: 1 } },
    "14": { class_type: "VAEDecode", inputs: { samples: ["13", 0], vae: ["3", 0] } },
    "15": { class_type: "SaveImage", inputs: { images: ["14", 0], filename_prefix: path.parse(output).name } }
  };
  if (poseReferenceName) {
    workflow["16"] = { class_type: "LoadImage", inputs: { image: poseReferenceName } };
    workflow["17"] = { class_type: "FluxKontextImageScale", inputs: { image: ["16", 0] } };
    workflow["8"].inputs.image2 = ["17", 0];
  }
}

const queued = await submitPromptWithReceipt({ api, output, fingerprint, workflow, releaseCachedModels });
const promptId = queued.prompt_id;
let history;
const deadline = Date.now() + timeoutMs;
for (;;) {
  if (Date.now() >= deadline) {
    updateSubmissionReceipt(output, fingerprint, { status: "poll_timeout", timed_out_at: new Date().toISOString() });
    throw new Error(`ComfyUI timed out after ${timeoutMs}ms; receipt preserved for resume`);
  }
  await new Promise((resolve) => setTimeout(resolve, pollMs));
  const payload = await jsonFetch(`${api}/history/${promptId}`);
  if (!payload[promptId]) continue;
  if (payload[promptId].status?.status_str === "error") {
    updateSubmissionReceipt(output, fingerprint, { status: "error", error_at: new Date().toISOString() });
    throw new Error(JSON.stringify(payload[promptId].status));
  }
  if (payload[promptId].outputs) { history = payload[promptId]; break; }
}
const images = Object.values(history.outputs).flatMap((item) => item.images || []);
const image = images.at(-1);
if (!image) throw new Error("No output image");
const params = new URLSearchParams({ filename: image.filename, subfolder: image.subfolder || "", type: image.type || "output" });
const response = await fetch(`${api}/view?${params}`, {
  signal: AbortSignal.timeout(120000),
});
if (!response.ok) throw new Error(`download ${response.status} ${await response.text()}`);
atomicWrite(output, Buffer.from(await response.arrayBuffer()));
atomicWrite(`${output}.json`, `${JSON.stringify({ mode: args.mode, source, pose_reference: poseReference, output, prompt: args.prompt, mutable, prompt_id: promptId, seed, steps, cfg, strength, width, height, unet, clip, vae, lora, prepare_memory: prepareMemory }, null, 2)}\n`);
updateSubmissionReceipt(output, fingerprint, { status: "complete", output_sha256: fileSha256(output), completed_at: new Date().toISOString() });
console.log(output);
