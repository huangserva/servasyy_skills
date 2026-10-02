#!/usr/bin/env python3
"""Text-to-image via Qwen-Image 2.1 (bf16) on the local 4090 ComfyUI.

Backend: newgpu (4090) ComfyUI-qi21 instance, port 8192 (local-only 127.0.0.1,
reached over SSH). The shared 8188 port on the 4090 is owned by the machine's
supervisor-managed older ComfyUI (no Qwen-Image 2.1 nodes) — do not fight it;
this adapter uses its own dedicated port 8192.

Usage:
  python3 run_qwen21_t2i.py --prompt-file brief.txt --output out.png \
      [--aspect 1:1|3:4|16:9|9:16|4:3] [--steps 20] [--cfg 1.0] [--seed 42]

Sidecars written next to the output: <out>.prompt.txt (full prompt),
<out>.request.json (backend, models, seed, steps, prompt_id).
"""
import json, sys, time, subprocess, argparse, os
from pathlib import Path

SSH = os.environ.get("QI21_SSH", "ssh -o ConnectTimeout=10 newgpu").split()
API_PORT = int(os.environ.get("QI21_PORT", "8192"))
REMOTE_VIEW = f"http://127.0.0.1:{API_PORT}"
REMOTE_OUTPUT_DIR = os.environ.get("QI21_OUTPUT_DIR", "/home/admin01/ComfyUI-qi21/output")

UNET = "qwen_image_2.1_bf16.safetensors"
CLIP = "qwen3vl_8b_bf16.safetensors"
VAE = "qwen_image_2.1_vae_bf16.safetensors"


def remote(cmd, timeout=120):
    out = subprocess.run(SSH + [cmd], capture_output=True, text=True,
                         timeout=timeout, stdin=subprocess.DEVNULL)
    if out.returncode != 0:
        raise SystemExit(f"ssh failed: {out.stderr[-500:]}")
    return out.stdout.strip()


def build_workflow(prompt, negative, res, steps, cfg, seed):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "4": {"class_type": "TextEncodeQwenImage21",
              "inputs": {"clip": ["2", 0], "prompt": prompt,
                         "negative_prompt": negative, "resolution": res, "images": []}},
        "5": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "seed": seed, "steps": steps, "cfg": cfg,
                         "sampler_name": "er_sde", "scheduler": "simple",
                         "positive": ["4", 0], "negative": ["4", 1],
                         "latent_image": ["4", 2], "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["3", 0]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "qi21"}},
    }


def main():
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, 0)  # never let children (ssh) inherit an external stdin
    p = argparse.ArgumentParser()
    p.add_argument("--prompt-file", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--aspect", default="1:1", choices=["1:1", "3:4", "16:9", "9:16", "4:3"])
    p.add_argument("--steps", type=int, default=20)
    p.add_argument("--cfg", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--negative", default="")
    p.add_argument("--timeout", type=int, default=1800)
    a = p.parse_args()
    if a.output.exists():
        raise SystemExit(f"output exists: {a.output}")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    prompt = a.prompt_file.read_text(encoding="utf-8").strip()
    if not prompt:
        raise SystemExit("empty prompt")
    sizes = {"1:1": (1344, 1344), "3:4": (1152, 1536), "16:9": (1536, 864),
             "9:16": (864, 1536), "4:3": (1536, 1152)}
    w, h = sizes[a.aspect]
    wf = build_workflow(prompt, a.negative, max(w, h), a.steps, a.cfg, a.seed)

    remote_json = Path(f"/tmp/qi21_body_{os.getpid()}_{int(time.time())}.json")
    local_json = Path(f"/tmp/qi21_local_{os.getpid()}_{int(time.time())}.json")
    local_json.write_text(json.dumps({"prompt": wf}, ensure_ascii=False), encoding="utf-8")
    try:
        subprocess.run(SSH + [f"cat > {remote_json}"], input=local_json.read_text(encoding="utf-8"),
                       text=True, check=True, timeout=60)
        out = remote(f"curl -s -m 30 -X POST {REMOTE_VIEW}/prompt "
                     f"-H 'Content-Type: application/json' -d @{remote_json}")
    finally:
        local_json.unlink(missing_ok=True)
    resp = json.loads(out)
    if "prompt_id" not in resp:
        raise SystemExit(f"submit failed: {out[:500]}")
    pid = resp["prompt_id"]
    print(f"submitted {pid}", flush=True)

    deadline = time.time() + a.timeout
    while time.time() < deadline:
        hist_raw = remote(
            f"curl -s -m 15 '{REMOTE_VIEW}/history?max_items=10' | python3 -c "
            f"\"import json,sys; d=json.load(sys.stdin); v=d.get('{pid}',{{}}); print(json.dumps(v.get('outputs',{{}})))\""
        )
        hist = json.loads(hist_raw)
        if hist:
            for node_out in hist.values():
                for img in node_out.get("images", []):
                    if img.get("type") == "output":
                        fname = img["filename"]
                        sub = img.get("subfolder", "")
                        remote_path = f"{REMOTE_OUTPUT_DIR}/{sub}/{fname}" if sub else f"{REMOTE_OUTPUT_DIR}/{fname}"
                        a.output.write_bytes(subprocess.run(SSH + [f"cat {remote_path}"],
                                                            capture_output=True, check=True,
                                                            timeout=120,
                                                            stdin=subprocess.DEVNULL).stdout)
                        meta = {"prompt": prompt,
                                "backend": f"newgpu ComfyUI-qi21:{API_PORT} qwen_image_2.1_bf16",
                                "models": {"unet": UNET, "clip": CLIP, "vae": VAE},
                                "aspect": a.aspect, "request_px": [w, h], "seed": a.seed,
                                "steps": a.steps, "sampler": "er_sde/simple", "prompt_id": pid}
                        a.output.with_suffix(".request.json").write_text(
                            json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
                        a.output.with_suffix(".prompt.txt").write_text(prompt + "\n", encoding="utf-8")
                        print(f"saved {a.output}", flush=True)
                        return
        time.sleep(10)
    raise SystemExit("timed out waiting for result")


if __name__ == "__main__":
    main()
