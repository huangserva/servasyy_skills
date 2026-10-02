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
const args = argsOf(process.argv.slice(2));
for (const key of ["output", "prompt", "width", "height"]) if (!args[key]) throw new Error(`--${key} is required`);
const api = (args.api || process.env.COMFY_URL || "http://127.0.0.1:8188").replace(/\/$/, "");
const output = path.resolve(args.output);
const seed = Number(args.seed || 42);
const steps = Number(args.steps || 9);
const width = Number(args.width);
const height = Number(args.height);
const prepareMemory = !["0", "false", "no"].includes(String(args["prepare-memory"] || "true").toLowerCase());
const negative = args.negative || "people, person, crowd, bystander, duplicate, text, logo, watermark, collage";
const pollMs = Number(process.env.COMFY_POLL_MS || 3000);
const timeoutMs = Number(process.env.COMFY_TIMEOUT_MS || 900000);
const fingerprint = submissionFingerprint({
  adapter: "zimage-t2i-v1", prompt: args.prompt, negative, seed, steps, width, height,
  model_id: args["model-id"] || "Tongyi-MAI/Z-Image-Turbo", precision: args.precision || "bf16",
});
async function getJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    signal: options.signal || AbortSignal.timeout(30000),
  });
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  return response.json();
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
for (const node of ["ZImageLoader", "ZImageSampler"]) if (!info[node]) throw new Error(`Missing Z-Image node: ${node}`);
const workflow = {
  "1": { class_type: "ZImageLoader", inputs: { model_id: args["model-id"] || "Tongyi-MAI/Z-Image-Turbo", precision: args.precision || "bf16", compile_model: false, attention_backend: "default" } },
  "2": { class_type: "ZImageSampler", inputs: { pipe: ["1", 0], prompt: args.prompt, width, height, steps, guidance_scale: 0, seed, negative_prompt: negative, batch_size: 1, max_sequence_length: 1024, cfg_normalization: false, cfg_truncation: 1 } },
  "3": { class_type: "SaveImage", inputs: { images: ["2", 0], filename_prefix: path.parse(output).name } }
};
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
atomicWrite(`${output}.json`, `${JSON.stringify({ prompt: args.prompt, negative, prompt_id: queued.prompt_id, seed, steps, width, height, prepare_memory: prepareMemory }, null, 2)}\n`);
updateSubmissionReceipt(output, fingerprint, { status: "complete", output_sha256: fileSha256(output), completed_at: new Date().toISOString() });
console.log(output);
