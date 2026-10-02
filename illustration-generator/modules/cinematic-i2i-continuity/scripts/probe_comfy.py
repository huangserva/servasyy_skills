#!/usr/bin/env python3
"""Probe a ComfyUI instance and optional SSH process root."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_CAPABILITIES = Path(__file__).resolve().parent.parent / "references" / "capabilities.json"


def get_json(base: str, path: str) -> dict:
    with urllib.request.urlopen(base.rstrip("/") + path, timeout=20) as response:
        return json.load(response)


def combo_values(info: dict, node: str, field: str) -> list[str]:
    try:
        raw = info[node]["input"]["required"][field][0]
    except (KeyError, IndexError, TypeError):
        return []
    return raw if isinstance(raw, list) else []


def check_route(info: dict, spec: dict) -> dict:
    missing_nodes = [node for node in spec.get("nodes", []) if node not in info]
    missing_signatures = []
    for node, fields in spec.get("node_required_inputs", {}).items():
        required = info.get(node, {}).get("input", {}).get("required", {})
        for field in fields:
            if field not in required:
                missing_signatures.append(f"{node}.{field}")
    clip_types = combo_values(info, "CLIPLoader", "type")
    models = combo_values(info, "UNETLoader", "unet_name")
    clips = combo_values(info, "CLIPLoader", "clip_name")
    vaes = combo_values(info, "VAELoader", "vae_name")
    loras = combo_values(info, "LoraLoaderModelOnly", "lora_name")
    any_models = spec.get("models_any", [])
    any_clips = spec.get("clips_any", [])
    missing_any_model = bool(any_models) and not any(value in models for value in any_models)
    missing_any_clip = bool(any_clips) and not any(value in clips for value in any_clips)
    missing_vaes = [value for value in spec.get("vaes", []) if value not in vaes]
    missing_loras = [value for value in spec.get("loras", []) if value not in loras]
    clip_type = spec.get("clip_type")
    missing_clip_type = bool(clip_type) and clip_type not in clip_types
    passed = not any(
        [missing_nodes, missing_signatures, missing_any_model, missing_any_clip, missing_vaes, missing_loras, missing_clip_type]
    )
    return {
        "pass": passed,
        "missing_nodes": missing_nodes,
        "missing_signatures": missing_signatures,
        "missing_any_model": any_models if missing_any_model else [],
        "missing_any_clip": any_clips if missing_any_clip else [],
        "missing_vaes": missing_vaes,
        "missing_loras": missing_loras,
        "missing_clip_type": clip_type if missing_clip_type else None,
    }


def read_remote_root(target: str) -> str:
    command = "pid=$(pgrep -f 'python.*main.py.*--port 8188' | head -1); test -n \"$pid\"; readlink -f /proc/$pid/cwd"
    result = subprocess.run(["ssh", target, command], capture_output=True, text=True, timeout=20, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "cannot read remote ComfyUI root")
    return result.stdout.strip().splitlines()[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8188")
    parser.add_argument("--capabilities", default=str(DEFAULT_CAPABILITIES))
    parser.add_argument("--require", action="append", default=[])
    parser.add_argument("--ssh-target")
    parser.add_argument("--expected-root")
    parser.add_argument("--out")
    args = parser.parse_args()
    capabilities = json.loads(Path(args.capabilities).read_text(encoding="utf-8"))
    unknown = [name for name in args.require if name not in capabilities]
    if unknown:
        print(json.dumps({"pass": False, "error": f"unknown capabilities: {unknown}"}, indent=2))
        return 2

    try:
        info = get_json(args.url, "/object_info")
        system = get_json(args.url, "/system_stats")
        queue = get_json(args.url, "/queue")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        report = {"pass": False, "url": args.url, "error": str(error)}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    required = args.require or sorted(capabilities)
    routes = {name: check_route(info, capabilities[name]) for name in required}
    root = None
    root_error = None
    root_pass = True
    if args.ssh_target:
        try:
            root = read_remote_root(args.ssh_target)
            root_pass = not args.expected_root or root == args.expected_root
        except (RuntimeError, subprocess.TimeoutExpired) as error:
            root_error = str(error)
            root_pass = False
    elif args.expected_root:
        root_error = "--expected-root requires --ssh-target"
        root_pass = False

    devices = system.get("devices", [])
    report = {
        "pass": all(item["pass"] for item in routes.values()) and root_pass,
        "url": args.url,
        "routes": routes,
        "process_root": root,
        "expected_root": args.expected_root,
        "root_error": root_error,
        "queue_running": len(queue.get("queue_running", [])),
        "queue_pending": len(queue.get("queue_pending", [])),
        "devices": [item.get("name") for item in devices],
        "comfyui_version": system.get("system", {}).get("comfyui_version"),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
