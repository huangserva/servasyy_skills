import { createHash, randomUUID } from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const DEFAULT_LOCK = "/tmp/hippoteam-comfy-8188-submit.lock";

function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function ownerPath(lockPath) {
  return path.join(lockPath, "owner.json");
}

function processIsAlive(pid) {
  if (!Number.isInteger(pid) || pid <= 0) return null;
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    if (error?.code === "ESRCH") return false;
    if (error?.code === "EPERM") return true;
    return null;
  }
}

function reclaimDeadOwner(lockPath) {
  let owner;
  try {
    owner = JSON.parse(fs.readFileSync(ownerPath(lockPath), "utf8"));
  } catch {
    return false;
  }
  if (!owner?.token || processIsAlive(owner.pid) !== false) return false;
  const tombstone = `${lockPath}.dead-${owner.token}`;
  try {
    fs.renameSync(lockPath, tombstone);
  } catch (error) {
    if (["ENOENT", "EEXIST"].includes(error?.code)) return false;
    throw error;
  }
  let movedOwner;
  try {
    movedOwner = JSON.parse(fs.readFileSync(ownerPath(tombstone), "utf8"));
  } catch {
    movedOwner = null;
  }
  if (movedOwner?.token !== owner.token) {
    fs.renameSync(tombstone, lockPath);
    return false;
  }
  fs.rmSync(tombstone, { recursive: true, force: true });
  return true;
}

export async function withComfySubmissionLock(api, task) {
  const lockPath = process.env.COMFY_SUBMIT_LOCK || DEFAULT_LOCK;
  const timeoutMs = Number(process.env.COMFY_LOCK_TIMEOUT_MS || 120000);
  const pollMs = Number(process.env.COMFY_LOCK_POLL_MS || 100);
  const token = randomUUID();
  const deadline = Date.now() + timeoutMs;

  for (;;) {
    try {
      fs.mkdirSync(lockPath);
      fs.writeFileSync(ownerPath(lockPath), `${JSON.stringify({ token, pid: process.pid, api, acquired_at: new Date().toISOString() })}\n`);
      break;
    } catch (error) {
      if (error?.code !== "EEXIST") throw error;
      if (reclaimDeadOwner(lockPath)) continue;
      if (Date.now() >= deadline) throw new Error(`Timed out waiting for shared ComfyUI submission lock ${lockPath}`);
      await sleep(pollMs);
    }
  }

  try {
    return await task();
  } finally {
    let owner;
    try {
      owner = JSON.parse(fs.readFileSync(ownerPath(lockPath), "utf8"));
    } catch {
      owner = null;
    }
    if (owner?.token === token) fs.rmSync(lockPath, { recursive: true, force: true });
  }
}

export function atomicWrite(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.${process.pid}.${randomUUID()}.tmp`;
  fs.writeFileSync(temporary, data);
  fs.renameSync(temporary, file);
}

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonical(value[key])]));
  }
  return value;
}

export function submissionFingerprint(value) {
  return createHash("sha256").update(JSON.stringify(canonical(value))).digest("hex");
}

export function fileSha256(file) {
  return createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function readReceipt(file) {
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

export function updateSubmissionReceipt(output, fingerprint, fields) {
  const file = `${path.resolve(output)}.receipt.json`;
  const current = readReceipt(file);
  if (!current || current.fingerprint !== fingerprint) {
    throw new Error(`Submission receipt fingerprint mismatch: ${file}`);
  }
  atomicWrite(file, `${JSON.stringify({ ...current, ...fields }, null, 2)}\n`);
}

export async function submitPromptWithReceipt({
  api,
  output,
  fingerprint,
  workflow,
  releaseCachedModels,
}) {
  const file = `${path.resolve(output)}.receipt.json`;
  const resumable = () => {
    const receipt = readReceipt(file);
    if (!receipt) return null;
    if (receipt.fingerprint !== fingerprint) {
      if (
        receipt.status !== "complete" &&
        (receipt.prompt_id ||
        ["submitting", "submission_unknown", "queued", "poll_timeout"].includes(receipt.status)
        )
      ) {
        throw new Error(
          `A different fingerprint still owns ${file}; reconcile it before replacing the receipt`
        );
      }
      return null;
    }
    if (receipt.prompt_id) return { prompt_id: receipt.prompt_id, resumed: true };
    if (["submitting", "submission_unknown"].includes(receipt.status)) {
      throw new Error(
        `ComfyUI submission state is unknown; refusing duplicate POST. Reconcile or remove ${file}`
      );
    }
    return null;
  };
  const existing = resumable();
  if (existing) return existing;

  return withComfySubmissionLock(api, async () => {
    const insideLock = resumable();
    if (insideLock) return insideLock;
    await releaseCachedModels();
    const clientId = randomUUID();
    const intent = {
      version: 1,
      status: "submitting",
      fingerprint,
      client_id: clientId,
      api,
      started_at: new Date().toISOString(),
    };
    atomicWrite(file, `${JSON.stringify(intent, null, 2)}\n`);
    try {
      const response = await fetch(`${api}/prompt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: workflow, client_id: clientId }),
        signal: AbortSignal.timeout(Number(process.env.COMFY_POST_TIMEOUT_MS || 30000)),
      });
      if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
      const queued = await response.json();
      if (!queued.prompt_id) throw new Error("ComfyUI did not return prompt_id");
      atomicWrite(file, `${JSON.stringify({
        ...intent,
        status: "queued",
        prompt_id: queued.prompt_id,
        queued_at: new Date().toISOString(),
      }, null, 2)}\n`);
      return { prompt_id: queued.prompt_id, resumed: false };
    } catch (error) {
      atomicWrite(file, `${JSON.stringify({
        ...intent,
        status: "submission_unknown",
        failed_at: new Date().toISOString(),
        error: String(error?.message || error),
      }, null, 2)}\n`);
      throw new Error(
        `ComfyUI prompt response was not confirmed; receipt frozen to prevent duplicate submission: ${file}`,
        { cause: error }
      );
    }
  });
}
