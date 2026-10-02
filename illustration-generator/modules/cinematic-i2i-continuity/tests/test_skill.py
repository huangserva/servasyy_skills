from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import struct
import subprocess
import tempfile
import threading
import time
import unittest
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image


SKILL = Path(__file__).resolve().parents[1]
PLAN = SKILL / "scripts" / "plan_continuity.py"
VALIDATE = SKILL / "scripts" / "validate_continuity_bundle.py"
PROBE = SKILL / "scripts" / "probe_comfy.py"
COMPOSITE = SKILL / "scripts" / "composite_with_mask.py"
COLOR_DELTA = SKILL / "scripts" / "extract_color_delta_mask.py"
CUTOUTS = SKILL / "scripts" / "composite_cutouts.py"
MASKED_RGBA = SKILL / "scripts" / "extract_masked_rgba.py"
KREA = SKILL / "scripts" / "run_krea2_edit.mjs"
KREA_T2I = SKILL / "scripts" / "run_krea2_t2i.mjs"
QWEN = SKILL / "scripts" / "run_qwen_edit.mjs"
ZIMAGE = SKILL / "scripts" / "run_zimage_t2i.mjs"
RECORD = SKILL / "scripts" / "record_qc.py"
RELEASE_LEDGER = SKILL / "scripts" / "validate_release_ledger.py"
GATES = ["capability", "master", "world", "content", "identity", "handoff"]
IDENTITY_METHOD = "hash-bound-labeled-contact-sheet-comparison"


def png(path: Path, width: int = 128, height: int = 72, color: bytes = b"\x20\x40\x60") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = b"".join(b"\x00" + (color * width) for _ in range(height))
    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity_review(state_id: str, cast: list[str]) -> dict:
    return {
        "pass": True,
        "metric_applicable": False,
        "visual_pass": True,
        "reason": "profile face reviewed against hash-bound master",
        "method": IDENTITY_METHOD,
        "reviewer": "visual-reviewer",
        "master_ids": cast,
        "contact_cell": state_id,
        "reason_code": "hash_bound_visual_master_comparison" if cast else "zero_cast_state",
    }


class FakeComfy(BaseHTTPRequestHandler):
    uploads = []
    prompts = []
    view_bytes = b""
    missing_krea = False
    queue_busy = False
    free_calls = 0
    submission_events = []
    free_delay = 0
    drop_prompt_response = False

    def do_GET(self):
        if self.path.startswith("/view"):
            body = self.view_bytes
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/history/"):
            prompt_id = self.path.rsplit("/", 1)[-1]
            payload = {prompt_id: {"status": {"status_str": "success"}, "outputs": {"save": {"images": [{"filename": "fake.png", "subfolder": "", "type": "output"}]}}}}
            return self.write_json(payload)
        object_info = {
            "Krea2EditModelPatch": {"input": {"required": {"model": [], "source_latent": []}}},
            "Krea2EditGroundedEncode": {"input": {"required": {"clip": [], "prompt": []}}},
            "Krea2OstrisEditModelPatch": {"input": {"required": {"model": []}}},
            "TextEncodeKrea2OstrisEdit": {"input": {"required": {"clip": [], "prompt": []}}},
            "CLIPLoader": {"input": {"required": {"type": [["krea2", "qwen_image"]], "clip_name": [["qwen3vl_4b_fp8_scaled.safetensors", "qwen_2.5_vl_7b_fp8_scaled.safetensors"]]}}},
            "UNETLoader": {"input": {"required": {"unet_name": [["krea2_turbo_fp8.safetensors", "krea2_turbo_fp8_scaled.safetensors", "qwen_image_edit_2511_bf16.safetensors", "qwen_image_edit_2511_fp8_lightning_4steps.safetensors"]]}}},
            "VAELoader": {"input": {"required": {"vae_name": [["qwen_image_vae.safetensors"]]}}},
            "LoraLoaderModelOnly": {"input": {"required": {"lora_name": [["krea2_identity_edit_v1.safetensors", "krea2_lora-edit-step00005310.safetensors"]]}}},
            "TextEncodeQwenImageEditPlus": {}, "FluxKontextMultiReferenceLatentMethod": {}, "ModelSamplingAuraFlow": {}, "CFGNorm": {},
            "CLIPTextEncode": {}, "ConditioningZeroOut": {},
            "ZImageLoader": {}, "ZImageSampler": {}, "LTXDirector": {}, "LTXDirectorGuide": {}, "LTXVConcatAVLatent": {}
        }
        if self.missing_krea:
            object_info.pop("Krea2EditModelPatch")
            object_info["CLIPLoader"]["input"]["required"]["type"] = [["qwen_image"]]
        if self.path == "/queue":
            type(self).submission_events.append("queue")
        payload = object_info if self.path == "/object_info" else ({"system": {"comfyui_version": "test"}, "devices": [{"name": "test-gpu"}]} if self.path == "/system_stats" else {"queue_running": [["busy"]] if self.queue_busy else [], "queue_pending": []})
        self.write_json(payload)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        if self.path == "/upload/image":
            match = re.search(br'filename="([^"]+)"', body)
            name = match.group(1).decode() if match else "missing.png"
            self.uploads.append(name)
            return self.write_json({"name": name, "subfolder": ""})
        if self.path == "/prompt":
            type(self).submission_events.append("prompt")
            type(self).prompts.append(json.loads(body))
            if type(self).drop_prompt_response:
                self.close_connection = True
                return
            return self.write_json({"prompt_id": "fake-prompt"})
        if self.path == "/free":
            type(self).submission_events.append("free")
            time.sleep(type(self).free_delay)
            type(self).free_calls += 1
            return self.write_json({"ok": True})
        self.send_error(404)

    def write_json(self, payload):
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        return


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for value in ["masters/a.png", "masters/b.png", "world/arena.png", "blocking/s01.png", "masks/a.png", "masks/b.png"]:
            png(self.root / value)
        (self.root / "qc/masters").mkdir(parents=True)
        (self.root / "qc/masters/a.json").write_text(json.dumps({"master": "masters/a.png", "sha256": sha(self.root / "masters/a.png"), "face_count": 1, "approved": True}), encoding="utf-8")
        (self.root / "qc/masters/b.json").write_text(json.dumps({"master": "masters/b.png", "sha256": sha(self.root / "masters/b.png"), "face_count": 1, "approved": True}), encoding="utf-8")
        self.manifest = {
            "project": "test",
            "resolution": [128, 72],
            "runtime": {"comfy_url": "http://fake-comfy:8188", "expected_root": "/srv/comfy-unified"},
            "characters": [
                {"id": "a", "character": "a", "form": "normal", "master": "masters/a.png", "master_size": [128, 72], "master_qc": "qc/masters/a.json", "one_face": True},
                {"id": "b", "character": "b", "form": "normal", "master": "masters/b.png", "master_size": [128, 72], "master_qc": "qc/masters/b.json", "one_face": True}
            ],
            "scenes": [{"id": "arena", "world_plate": "world/arena.png", "empty": True}],
            "shots": [{"id": "s01", "scene": "arena", "cast": ["a", "b"], "exact_count": 2, "action": "A left, B right", "change": ["action"], "precision": "exact", "blocking": "blocking/s01.png", "masks": {"a": "masks/a.png", "b": "masks/b.png"}, "output": "shots/s01/final.png"}]
        }

    def tearDown(self):
        self.temp.cleanup()

    def write_manifest(self, value=None):
        path = self.root / "manifest.json"
        path.write_text(json.dumps(value or self.manifest), encoding="utf-8")
        return path

    def plan(self, manifest=None):
        manifest_path = self.write_manifest(manifest)
        plan_path = self.root / "plan.json"
        subprocess.run(["python3", str(PLAN), str(manifest_path), "--out", str(plan_path)], check=True, capture_output=True, text=True)
        return manifest_path, plan_path

    def validate(self, manifest_path, plan_path, *extra):
        return subprocess.run(["python3", str(VALIDATE), str(manifest_path), str(plan_path), "--project-root", str(self.root), *extra], capture_output=True, text=True)

    def write_ledger_dependencies(self, index_records):
        (self.root / "plan.json").write_text("{}", encoding="utf-8")
        index = self.root / "index.json"
        index.write_text(json.dumps({"pass": True, "actual_count": len(index_records), "records": index_records}), encoding="utf-8")
        review = self.root / "review.json"
        gates = {name: True for name in ["exact_cast", "identity", "style", "action", "duplicate", "dimensions"]}
        contact = self.root / "review/contact.jpg"
        review.write_text(json.dumps({
            "pass": True,
            "reviewer": "visual-reviewer",
            "final_index_sha256": sha(index),
            "contact_sheets": [{"path": "review/contact.jpg", "sha256": sha(contact)}],
            "states": [{
                "id": item["id"],
                "accepted_sha256": item["sha256"],
                "contact_sheet_index": 0,
                "contact_cell": item["id"],
                "cast": ["a"],
                "gates": gates,
                "identity_evidence": identity_review(item["id"], ["a"]),
            } for item in index_records],
        }), encoding="utf-8")
        master_review = self.root / "master-review.json"
        master_review.write_text(json.dumps({
            "pass": True,
            "reviewer": "visual-reviewer",
            "contact_sheet": "review/contact.jpg",
            "contact_sheet_sha256": sha(contact),
            "masters": [{
                "id": "a",
                "path": "masters/a.png",
                "sha256": sha(self.root / "masters/a.png"),
                "size": [128, 72],
                "contact_cell": "a",
                "face_count": 1,
                "one_face": True,
                "approved": True,
            }],
        }), encoding="utf-8")
        return {
            "source_plan": "plan.json",
            "source_plan_sha256": sha(self.root / "plan.json"),
            "source_index": "index.json",
            "source_index_sha256": sha(index),
            "review_evidence": "review.json",
            "review_evidence_sha256": sha(review),
            "master_review": "master-review.json",
            "master_review_sha256": sha(master_review),
        }

    def test_multi_person_routes_and_preflight_passes(self):
        manifest, plan = self.plan()
        route = json.loads(plan.read_text())["shots"][0]
        self.assertEqual(route["route"], "sequential-masked-edit")
        self.assertEqual(
            [stage.get("adapter") for stage in route["stages"]][1:6],
            [None, "scripts/run_qwen_edit.mjs", "scripts/composite_with_mask.py", "scripts/run_qwen_edit.mjs", "scripts/composite_with_mask.py"],
        )
        self.assertEqual(self.validate(manifest, plan).returncode, 0)

    def test_missing_masks_is_blocking(self):
        bad = copy.deepcopy(self.manifest)
        del bad["shots"][0]["masks"]
        manifest, plan = self.plan(bad)
        result = self.validate(manifest, plan)
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing_mask", [item.get("code") for item in json.loads(result.stdout)["errors"]])

    def test_duplicate_master_and_ar_mismatch_are_blocking(self):
        bad = copy.deepcopy(self.manifest)
        bad["characters"].append(copy.deepcopy(bad["characters"][0]))
        bad["characters"][0]["master_size"] = [72, 128]
        manifest, plan = self.plan(bad)
        result = self.validate(manifest, plan)
        self.assertEqual(result.returncode, 2)
        self.assertGreaterEqual(len(json.loads(result.stdout)["errors"]), 2)

    def test_master_qc_hash_is_bound_to_actual_file(self):
        manifest, plan = self.plan()
        png(self.root / "masters/a.png", color=b"\xff\xff\x00")
        result = self.validate(manifest, plan)
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid_master_qc", [item.get("code") for item in json.loads(result.stdout)["errors"]])

    def test_world_plate_and_previous_state_are_blocking_dependencies(self):
        bad = copy.deepcopy(self.manifest)
        bad["scenes"][0].pop("world_plate")
        bad["shots"][0]["previous_state"] = "missing-state"
        manifest, plan = self.plan(bad)
        result = self.validate(manifest, plan)
        codes = [item.get("code") for item in json.loads(result.stdout)["errors"]]
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing_world_plate", codes)
        self.assertIn("invalid_previous_state", codes)

    def test_recurring_cast_cannot_be_tampered_to_t2i(self):
        manifest, plan = self.plan()
        value = json.loads(plan.read_text())
        value["shots"][0]["route"] = "t2i-world-plate"
        plan.write_text(json.dumps(value), encoding="utf-8")
        result = self.validate(manifest, plan)
        self.assertEqual(result.returncode, 2)
        self.assertIn("route_tampered", [item.get("code") for item in json.loads(result.stdout)["errors"]])

    def test_stage_adapter_tampering_is_blocking(self):
        manifest, plan = self.plan()
        value = json.loads(plan.read_text())
        value["shots"][0]["stages"][2]["adapter"] = "scripts/run_zimage_t2i.mjs"
        plan.write_text(json.dumps(value), encoding="utf-8")
        result = self.validate(manifest, plan)
        self.assertEqual(result.returncode, 2)
        self.assertIn("stages_tampered", [item.get("code") for item in json.loads(result.stdout)["errors"]])

    def test_release_requires_real_files_and_qc(self):
        manifest, plan = self.plan()
        png(self.root / "shots/s01/final.png")
        png(self.root / "ltx-handoff/s01.png")
        (self.root / "qc/capability.json").write_text(json.dumps({"pass": True, "url": "http://fake-comfy:8188", "process_root": "/srv/comfy-unified", "expected_root": "/srv/comfy-unified", "routes": {"qwen-edit": {"pass": True}, "ltx-director": {"pass": True}}}), encoding="utf-8")
        accepted_hash = sha(self.root / "shots/s01/final.png")
        (self.root / "qc/content.json").write_text(json.dumps({"pass": True, "accepted_sha256": accepted_hash, "reviewer": "test-reviewer", "contact_sheet": "world/arena.png", "contact_sheet_sha256": sha(self.root / "world/arena.png")}), encoding="utf-8")
        (self.root / "qc/identity.json").write_text(json.dumps({"pass": True, "accepted_sha256": accepted_hash, "arcface": 0.86, "master_sha256": {"a": sha(self.root / "masters/a.png"), "b": sha(self.root / "masters/b.png")}}), encoding="utf-8")
        qc_path = self.root / "qc.json"
        record = subprocess.run(["python3", str(RECORD), str(manifest), "--plan", str(plan), "--project-root", str(self.root), "--shot", "s01", "--accepted", "shots/s01/final.png", "--handoff", "ltx-handoff/s01.png", "--capability-report", "qc/capability.json", "--content-evidence", "qc/content.json", "--identity-evidence", "qc/identity.json", "--out", str(qc_path)], capture_output=True, text=True)
        self.assertEqual(record.returncode, 0, record.stderr)
        self.assertEqual(self.validate(manifest, plan, "--phase", "release", "--qc", str(qc_path)).returncode, 0)
        qc = json.loads(qc_path.read_text())
        qc["shots"]["s01"]["gates"]["content"]["pass"] = False
        qc_path.write_text(json.dumps(qc), encoding="utf-8")
        result = self.validate(manifest, plan, "--phase", "release", "--qc", str(qc_path))
        self.assertEqual(result.returncode, 2)
        self.assertIn("gate_not_passed", [item.get("code") for item in json.loads(result.stdout)["errors"]])
        qc["shots"]["s01"]["gates"]["content"]["pass"] = True
        qc["shots"]["s01"]["gates"]["identity"]["arcface"] = 0.50
        qc_path.write_text(json.dumps(qc), encoding="utf-8")
        self.assertEqual(self.validate(manifest, plan, "--phase", "release", "--qc", str(qc_path)).returncode, 2)
        qc["shots"]["s01"]["gates"]["identity"]["arcface"] = 0.86
        png(self.root / "ltx-handoff/s01.png", color=b"\xff\x00\x00")
        qc_path.write_text(json.dumps(qc), encoding="utf-8")
        result = self.validate(manifest, plan, "--phase", "release", "--qc", str(qc_path))
        self.assertEqual(result.returncode, 2)
        self.assertIn("handoff_hash_mismatch", [item.get("code") for item in json.loads(result.stdout)["errors"]])

    def test_release_ledger_covers_every_hash_bound_state(self):
        png(self.root / "accepted/s01-01.png")
        png(self.root / "handoff/s01-01.png")
        png(self.root / "review/contact.jpg")
        image_hash = sha(self.root / "accepted/s01-01.png")
        master_hash = sha(self.root / "masters/a.png")
        dependencies = self.write_ledger_dependencies([
            {"id": "s01-01", "path": "accepted/s01-01.png", "sha256": image_hash}
        ])
        ledger = {
            "project": "test",
            "resolution": [128, 72],
            **dependencies,
            "expected_states": 1,
            "masters": {
                "a": {
                    "path": "masters/a.png", "sha256": master_hash,
                    "approved": True, "one_face": True, "face_count": 1,
                    "reviewer": "visual-reviewer", "review_state": "a",
                    "contact_sheet": "review/contact.jpg",
                    "contact_sheet_sha256": sha(self.root / "review/contact.jpg"),
                }
            },
            "records": [{
                "id": "s01-01",
                "accepted": "accepted/s01-01.png",
                "accepted_sha256": image_hash,
                "handoff": "handoff/s01-01.png",
                "handoff_sha256": image_hash,
                "contact_sheet": "review/contact.jpg",
                "contact_sheet_sha256": sha(self.root / "review/contact.jpg"),
                "reviewer": "visual-reviewer",
                "review_state": "s01-01",
                "review_record_sha256": dependencies["review_evidence_sha256"],
                "cast": ["a"],
                "master_sha256": {"a": master_hash},
                "content_gates": {name: True for name in ["exact_cast", "identity", "style", "action", "duplicate", "dimensions"]},
                "identity_evidence": identity_review("s01-01", ["a"]),
                "world_plate": "world/arena.png",
                "world_plate_sha256": sha(self.root / "world/arena.png"),
            }],
        }
        ledger_path = self.root / "ledger.json"
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        result = subprocess.run([
            "python3", str(RELEASE_LEDGER), str(ledger_path),
            "--project-root", str(self.root),
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)["actual_states"], 1)
        ledger["records"][0]["identity_evidence"]["master_ids"] = []
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        tampered = subprocess.run([
            "python3", str(RELEASE_LEDGER), str(ledger_path),
            "--project-root", str(self.root),
        ], capture_output=True, text=True)
        self.assertEqual(tampered.returncode, 2)
        self.assertIn(
            "invalid_identity_review_binding",
            {item["code"] for item in json.loads(tampered.stdout)["errors"]},
        )

    def test_release_ledger_verifies_arcface_record_bytes(self):
        png(self.root / "accepted/s01-01.png")
        png(self.root / "handoff/s01-01.png")
        png(self.root / "review/contact.jpg")
        image_hash = sha(self.root / "accepted/s01-01.png")
        master_hash = sha(self.root / "masters/a.png")
        dependencies = self.write_ledger_dependencies([
            {"id": "s01-01", "path": "accepted/s01-01.png", "sha256": image_hash}
        ])
        evidence_path = self.root / "review/arcface.json"
        evidence = {
            "pass": True,
            "thresholds": {"arcface": 0.8},
            "records": [{
                "id": "s01-01",
                "accepted_sha256": image_hash,
                "cast": ["a"],
                "master_sha256": {"a": master_hash},
                "metric_applicable": True,
                "arcface": 0.91,
                "pass": True,
            }],
        }
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        identity = identity_review("s01-01", ["a"])
        identity.update({
            "metric_applicable": True,
            "arcface": 0.91,
            "reason_code": "arcface_and_visual_master_comparison",
            "arcface_evidence": {
                "path": "review/arcface.json",
                "sha256": sha(evidence_path),
                "record_id": "s01-01",
            },
        })
        review_path = self.root / "review.json"
        review = json.loads(review_path.read_text())
        review["states"][0]["identity_evidence"] = identity
        review_path.write_text(json.dumps(review), encoding="utf-8")
        dependencies["review_evidence_sha256"] = sha(review_path)
        ledger = {
            "project": "test",
            "resolution": [128, 72],
            **dependencies,
            "expected_states": 1,
            "identity_policy": {"minimum_metric_states": 1},
            "masters": {"a": {
                "path": "masters/a.png", "sha256": master_hash,
                "approved": True, "one_face": True, "face_count": 1,
                "reviewer": "visual-reviewer", "review_state": "a",
                "contact_sheet": "review/contact.jpg",
                "contact_sheet_sha256": sha(self.root / "review/contact.jpg"),
            }},
            "records": [{
                "id": "s01-01",
                "accepted": "accepted/s01-01.png",
                "accepted_sha256": image_hash,
                "handoff": "handoff/s01-01.png",
                "handoff_sha256": image_hash,
                "contact_sheet": "review/contact.jpg",
                "contact_sheet_sha256": sha(self.root / "review/contact.jpg"),
                "reviewer": "visual-reviewer",
                "review_state": "s01-01",
                "review_record_sha256": dependencies["review_evidence_sha256"],
                "cast": ["a"],
                "master_sha256": {"a": master_hash},
                "content_gates": {name: True for name in ["exact_cast", "identity", "style", "action", "duplicate", "dimensions"]},
                "identity_evidence": identity,
                "world_plate": "world/arena.png",
                "world_plate_sha256": sha(self.root / "world/arena.png"),
            }],
        }
        ledger_path = self.root / "ledger.json"
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        passed = subprocess.run([
            "python3", str(RELEASE_LEDGER), str(ledger_path),
            "--project-root", str(self.root),
        ], capture_output=True, text=True)
        self.assertEqual(passed.returncode, 0, passed.stdout)

        evidence["records"][0]["accepted_sha256"] = "0" * 64
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        new_evidence_hash = sha(evidence_path)
        identity["arcface_evidence"]["sha256"] = new_evidence_hash
        review["states"][0]["identity_evidence"] = identity
        review_path.write_text(json.dumps(review), encoding="utf-8")
        ledger["review_evidence_sha256"] = sha(review_path)
        ledger["records"][0]["review_record_sha256"] = sha(review_path)
        ledger["records"][0]["identity_evidence"] = identity
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        tampered = subprocess.run([
            "python3", str(RELEASE_LEDGER), str(ledger_path),
            "--project-root", str(self.root),
        ], capture_output=True, text=True)
        self.assertEqual(tampered.returncode, 2)
        self.assertIn(
            "arcface_record_binding_mismatch",
            {item["code"] for item in json.loads(tampered.stdout)["errors"]},
        )

    def test_release_ledger_rejects_silent_duplicate_and_tampered_handoff(self):
        png(self.root / "accepted/s01-01.png")
        png(self.root / "handoff/s01-01.png", color=b"\xff\x00\x00")
        png(self.root / "review/contact.jpg")
        image_hash = sha(self.root / "accepted/s01-01.png")
        master_hash = sha(self.root / "masters/a.png")
        dependencies = self.write_ledger_dependencies([
            {"id": "s01-01", "path": "accepted/s01-01.png", "sha256": image_hash},
            {"id": "s01-02", "path": "accepted/s01-01.png", "sha256": image_hash},
        ])
        base = {
            "accepted": "accepted/s01-01.png",
            "accepted_sha256": image_hash,
            "handoff": "handoff/s01-01.png",
            "handoff_sha256": image_hash,
            "contact_sheet": "review/contact.jpg",
            "contact_sheet_sha256": sha(self.root / "review/contact.jpg"),
            "reviewer": "visual-reviewer",
            "review_state": "s01-01",
            "review_record_sha256": dependencies["review_evidence_sha256"],
            "cast": ["a"],
            "master_sha256": {"a": master_hash},
            "content_gates": {name: True for name in ["exact_cast", "identity", "style", "action", "duplicate", "dimensions"]},
            "identity_evidence": identity_review("s01-01", ["a"]),
            "world_plate": "world/arena.png",
            "world_plate_sha256": sha(self.root / "world/arena.png"),
        }
        ledger = {
            "project": "test",
            "resolution": [128, 72],
            **dependencies,
            "expected_states": 2,
            "masters": {"a": {
                "path": "masters/a.png", "sha256": master_hash,
                "approved": True, "one_face": True, "face_count": 1,
                "reviewer": "visual-reviewer", "review_state": "a",
                "contact_sheet": "review/contact.jpg",
                "contact_sheet_sha256": sha(self.root / "review/contact.jpg"),
            }},
            "records": [
                {**base, "id": "s01-01"},
                {
                    **base,
                    "id": "s01-02",
                    "review_state": "s01-02",
                    "identity_evidence": identity_review("s01-02", ["a"]),
                },
            ],
        }
        ledger_path = self.root / "ledger.json"
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        result = subprocess.run([
            "python3", str(RELEASE_LEDGER), str(ledger_path),
            "--project-root", str(self.root),
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        codes = {item["code"] for item in json.loads(result.stdout)["errors"]}
        self.assertIn("handoff_hash_mismatch", codes)
        self.assertIn("undeclared_duplicate_frame", codes)

    def test_release_ledger_binds_declared_hold_to_motion_bytes(self):
        png(self.root / "accepted/s01-01.png")
        (self.root / "accepted/s01-02.png").parent.mkdir(parents=True, exist_ok=True)
        (self.root / "accepted/s01-02.png").write_bytes(
            (self.root / "accepted/s01-01.png").read_bytes()
        )
        (self.root / "handoff").mkdir(parents=True, exist_ok=True)
        for state_id in ["s01-01", "s01-02"]:
            (self.root / f"handoff/{state_id}.png").write_bytes(
                (self.root / "accepted/s01-01.png").read_bytes()
            )
        png(self.root / "review/contact.jpg")
        image_hash = sha(self.root / "accepted/s01-01.png")
        master_hash = sha(self.root / "masters/a.png")
        dependencies = self.write_ledger_dependencies([
            {"id": "s01-01", "path": "accepted/s01-01.png", "sha256": image_hash},
            {"id": "s01-02", "path": "accepted/s01-02.png", "sha256": image_hash},
        ])
        motion_video = self.root / "motion/s01.mp4"
        motion_video.parent.mkdir(parents=True, exist_ok=True)
        motion_video.write_bytes(b"motion-video-v1")
        png(self.root / "motion/s01.jpg")
        gates = {
            "cast_and_identity": True,
            "style": True,
            "transition": True,
            "tail": True,
            "blank_frame": True,
        }
        motion_record = {
            "shot": "s01",
            "video": "motion/s01.mp4",
            "video_sha256": sha(motion_video),
            "every_frame_sheet": "motion/s01.jpg",
            "every_frame_sheet_sha256": sha(self.root / "motion/s01.jpg"),
            "reviewer": "motion-reviewer",
            "review_gates": gates,
            "review_pass": True,
        }
        motion_path = self.root / "motion/evidence.json"
        motion_path.write_text(
            json.dumps({"pass": True, "records": [motion_record]}),
            encoding="utf-8",
        )
        hold_motion = {
            "evidence": "motion/evidence.json",
            "evidence_sha256": sha(motion_path),
            **motion_record,
        }
        base = {
            "shot": "s01",
            "accepted_sha256": image_hash,
            "handoff_sha256": image_hash,
            "contact_sheet": "review/contact.jpg",
            "contact_sheet_sha256": sha(self.root / "review/contact.jpg"),
            "reviewer": "visual-reviewer",
            "review_record_sha256": dependencies["review_evidence_sha256"],
            "cast": ["a"],
            "master_sha256": {"a": master_hash},
            "content_gates": {name: True for name in ["exact_cast", "identity", "style", "action", "duplicate", "dimensions"]},
            "world_plate": "world/arena.png",
            "world_plate_sha256": sha(self.root / "world/arena.png"),
        }
        ledger = {
            "project": "test",
            "resolution": [128, 72],
            **dependencies,
            "expected_states": 2,
            "masters": {"a": {
                "path": "masters/a.png", "sha256": master_hash,
                "approved": True, "one_face": True, "face_count": 1,
                "reviewer": "visual-reviewer", "review_state": "a",
                "contact_sheet": "review/contact.jpg",
                "contact_sheet_sha256": sha(self.root / "review/contact.jpg"),
            }},
            "records": [
                {
                    **base,
                    "id": "s01-01",
                    "accepted": "accepted/s01-01.png",
                    "handoff": "handoff/s01-01.png",
                    "review_state": "s01-01",
                    "identity_evidence": identity_review("s01-01", ["a"]),
                },
                {
                    **base,
                    "id": "s01-02",
                    "accepted": "accepted/s01-02.png",
                    "handoff": "handoff/s01-02.png",
                    "review_state": "s01-02",
                    "identity_evidence": identity_review("s01-02", ["a"]),
                    "hold_of": "s01-01",
                    "hold_reason": "Performance develops inside the rendered shot.",
                    "hold_motion_evidence": hold_motion,
                },
            ],
        }
        ledger_path = self.root / "ledger.json"
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        passed = subprocess.run([
            "python3", str(RELEASE_LEDGER), str(ledger_path),
            "--project-root", str(self.root),
        ], capture_output=True, text=True)
        self.assertEqual(passed.returncode, 0, passed.stdout)

        motion_video.write_bytes(b"tampered-motion-video")
        tampered = subprocess.run([
            "python3", str(RELEASE_LEDGER), str(ledger_path),
            "--project-root", str(self.root),
        ], capture_output=True, text=True)
        self.assertEqual(tampered.returncode, 2)
        self.assertIn(
            "hold_motion_record_binding_mismatch",
            {item["code"] for item in json.loads(tampered.stdout)["errors"]},
        )

    def test_probe_contract_uses_nodes_models_and_loras(self):
        FakeComfy.missing_krea = False
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = subprocess.run(["python3", str(PROBE), "--url", f"http://127.0.0.1:{server.server_port}", "--require", "krea2-identity", "--require", "krea2-ostris", "--require", "qwen-edit"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertTrue(json.loads(result.stdout)["pass"])
        finally:
            server.shutdown()
            server.server_close()

    def test_probe_rejects_missing_node_and_clip_type(self):
        FakeComfy.missing_krea = True
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = subprocess.run(["python3", str(PROBE), "--url", f"http://127.0.0.1:{server.server_port}", "--require", "krea2-identity"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            report = json.loads(result.stdout)
            self.assertFalse(report["pass"])
            self.assertIn("Krea2EditModelPatch", report["routes"]["krea2-identity"]["missing_nodes"])
            self.assertEqual(report["routes"]["krea2-identity"]["missing_clip_type"], "krea2")
        finally:
            FakeComfy.missing_krea = False
            server.shutdown()
            server.server_close()

    def test_http_contract_for_all_image_adapters(self):
        source = self.root / "masters/a.png"
        FakeComfy.uploads = []
        FakeComfy.prompts = []
        FakeComfy.free_calls = 0
        FakeComfy.queue_busy = False
        FakeComfy.view_bytes = source.read_bytes()
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        api = f"http://127.0.0.1:{server.server_port}"
        env = {**os.environ, "COMFY_POLL_MS": "1"}
        try:
            commands = [
                ["node", str(KREA_T2I), "--api", api, "--output", str(self.root / "krea-t2i.png"), "--prompt", "neutral adult character master", "--width", "128", "--height", "72"],
                ["node", str(KREA), "--mode", "identity", "--api", api, "--source", str(source), "--output", str(self.root / "krea.png"), "--prompt", "neutral studio"],
                ["node", str(QWEN), "--api", api, "--source", str(source), "--output", str(self.root / "qwen.png"), "--prompt", "turn head slightly", "--negative", "crowd, duplicate person"],
                ["node", str(ZIMAGE), "--api", api, "--output", str(self.root / "world.png"), "--prompt", "empty valley", "--width", "128", "--height", "72"]
            ]
            for command in commands:
                result = subprocess.run(command, capture_output=True, text=True, env=env)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((self.root / "krea.png").is_file())
            self.assertTrue((self.root / "krea-t2i.png").is_file())
            self.assertTrue((self.root / "qwen.png").is_file())
            self.assertTrue((self.root / "world.png").is_file())
            self.assertEqual(len(FakeComfy.uploads), len(set(FakeComfy.uploads)))
            self.assertEqual(FakeComfy.free_calls, 4)
            qwen_prompt = next(item["prompt"] for item in FakeComfy.prompts if item["prompt"].get("10", {}).get("class_type") == "TextEncodeQwenImageEditPlus")
            self.assertEqual(qwen_prompt["10"]["inputs"]["prompt"], "crowd, duplicate person")
        finally:
            server.shutdown()
            server.server_close()

    def test_krea_memory_prepare_refuses_to_unload_active_shared_queue(self):
        source = self.root / "masters/a.png"
        FakeComfy.view_bytes = source.read_bytes()
        FakeComfy.free_calls = 0
        FakeComfy.queue_busy = True
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = subprocess.run([
                "node", str(KREA), "--mode", "identity", "--api", f"http://127.0.0.1:{server.server_port}",
                "--source", str(source), "--output", str(self.root / "busy.png"), "--prompt", "neutral studio"
            ], capture_output=True, text=True, env={**os.environ, "COMFY_POLL_MS": "1"})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing to unload shared ComfyUI models", result.stderr)
            self.assertEqual(FakeComfy.free_calls, 0)
        finally:
            FakeComfy.queue_busy = False
            server.shutdown()
            server.server_close()

    def test_shared_comfy_submission_is_serialized_across_processes(self):
        source = self.root / "masters/a.png"
        FakeComfy.view_bytes = source.read_bytes()
        FakeComfy.submission_events = []
        FakeComfy.free_delay = 0.15
        FakeComfy.queue_busy = False
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        api = f"http://127.0.0.1:{server.server_port}"
        env = {
            **os.environ,
            "COMFY_POLL_MS": "1",
            "COMFY_LOCK_POLL_MS": "5",
            "COMFY_SUBMIT_LOCK": str(self.root / "shared-8188.lock"),
        }
        commands = [
            ["node", str(KREA_T2I), "--api", api, "--output", str(self.root / f"concurrent-{index}.png"), "--prompt", "neutral portrait", "--width", "128", "--height", "72"]
            for index in range(2)
        ]
        try:
            processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env) for command in commands]
            results = [process.communicate(timeout=20) + (process.returncode,) for process in processes]
            self.assertTrue(all(returncode == 0 for _, _, returncode in results), results)
            self.assertEqual(FakeComfy.submission_events, ["queue", "free", "prompt", "queue", "free", "prompt"])
        finally:
            FakeComfy.free_delay = 0
            server.shutdown()
            server.server_close()

    def test_unknown_prompt_response_is_frozen_and_never_resubmitted(self):
        output = self.root / "unknown-response.png"
        FakeComfy.prompts = []
        FakeComfy.submission_events = []
        FakeComfy.queue_busy = False
        FakeComfy.drop_prompt_response = True
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        command = [
            "node", str(KREA_T2I), "--api", f"http://127.0.0.1:{server.server_port}",
            "--output", str(output), "--prompt", "neutral portrait", "--width", "128",
            "--height", "72", "--prepare-memory", "false",
        ]
        env = {**os.environ, "COMFY_POLL_MS": "1", "COMFY_POST_TIMEOUT_MS": "100"}
        try:
            first = subprocess.run(command, capture_output=True, text=True, env=env)
            self.assertNotEqual(first.returncode, 0)
            receipt = json.loads(Path(f"{output}.receipt.json").read_text())
            self.assertEqual(receipt["status"], "submission_unknown")
            self.assertEqual(len(FakeComfy.prompts), 1)

            FakeComfy.drop_prompt_response = False
            second = subprocess.run(command, capture_output=True, text=True, env=env)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("refusing duplicate POST", second.stderr)
            self.assertEqual(len(FakeComfy.prompts), 1)
        finally:
            FakeComfy.drop_prompt_response = False
            server.shutdown()
            server.server_close()

    def test_old_lock_is_never_deleted_by_a_waiting_process(self):
        lock = self.root / "owned-8188.lock"
        lock.mkdir()
        owner = {"token": "other-owner", "pid": 1}
        (lock / "owner.json").write_text(json.dumps(owner), encoding="utf-8")
        old = time.time() - 86400
        os.utime(lock, (old, old))
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = subprocess.run([
                "node", str(KREA_T2I), "--api", f"http://127.0.0.1:{server.server_port}",
                "--output", str(self.root / "locked.png"), "--prompt", "neutral portrait",
                "--width", "128", "--height", "72",
            ], capture_output=True, text=True, env={
                **os.environ,
                "COMFY_SUBMIT_LOCK": str(lock),
                "COMFY_LOCK_TIMEOUT_MS": "60",
                "COMFY_LOCK_POLL_MS": "5",
            })
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads((lock / "owner.json").read_text()), owner)
        finally:
            server.shutdown()
            server.server_close()

    def test_lock_owned_by_a_confirmed_dead_process_is_reclaimed(self):
        source = self.root / "masters/a.png"
        FakeComfy.view_bytes = source.read_bytes()
        FakeComfy.queue_busy = False
        lock = self.root / "dead-owner-8188.lock"
        lock.mkdir()
        dead = subprocess.Popen(["python3", "-c", "pass"])
        dead.wait(timeout=5)
        (lock / "owner.json").write_text(
            json.dumps({"token": "dead-owner", "pid": dead.pid}), encoding="utf-8"
        )
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = subprocess.run([
                "node", str(KREA_T2I), "--api", f"http://127.0.0.1:{server.server_port}",
                "--output", str(self.root / "reclaimed.png"), "--prompt", "neutral portrait",
                "--width", "128", "--height", "72", "--prepare-memory", "false",
            ], capture_output=True, text=True, env={
                **os.environ,
                "COMFY_SUBMIT_LOCK": str(lock),
                "COMFY_LOCK_TIMEOUT_MS": "1000",
                "COMFY_LOCK_POLL_MS": "5",
                "COMFY_POLL_MS": "1",
            })
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(lock.exists())
        finally:
            server.shutdown()
            server.server_close()

    def test_mask_composite_freezes_pixels_outside_mask(self):
        base = self.root / "base.png"
        layer = self.root / "layer.png"
        mask = self.root / "mask.png"
        output = self.root / "composite.png"
        Image.new("RGB", (8, 4), (255, 0, 0)).save(base)
        Image.new("RGB", (8, 4), (0, 0, 255)).save(layer)
        mask_image = Image.new("L", (8, 4), 0)
        for x in range(4, 8):
            for y in range(4):
                mask_image.putpixel((x, y), 255)
        mask_image.save(mask)
        subprocess.run(["python3", str(COMPOSITE), "--base", str(base), "--layer", str(layer), "--mask", str(mask), "--output", str(output)], check=True)
        result = Image.open(output).convert("RGB")
        self.assertEqual(result.getpixel((1, 1)), (255, 0, 0))
        self.assertEqual(result.getpixel((6, 1)), (0, 0, 255))

    def test_color_delta_mask_selects_gold_effect_not_small_skin_drift(self):
        base = self.root / "effect-base.png"
        layer = self.root / "effect-layer.png"
        mask = self.root / "effect-mask.png"
        base_image = Image.new("RGB", (6, 2), (20, 30, 40))
        layer_image = base_image.copy()
        layer_image.putpixel((1, 0), (230, 185, 75))
        base_image.putpixel((4, 0), (170, 120, 90))
        layer_image.putpixel((4, 0), (175, 123, 92))
        base_image.save(base)
        layer_image.save(layer)
        subprocess.run([
            "python3", str(COLOR_DELTA), "--base", str(base), "--layer", str(layer),
            "--output", str(mask), "--grow", "0", "--feather", "0"
        ], check=True)
        result = Image.open(mask).convert("L")
        self.assertGreater(result.getpixel((1, 0)), 200)
        self.assertEqual(result.getpixel((4, 0)), 0)

    def test_cutout_layout_places_rgba_layers_in_declared_order(self):
        base = self.root / "cutout-base.png"
        red = self.root / "red.png"
        blue = self.root / "blue.png"
        layout = self.root / "cutout-layout.json"
        output = self.root / "cutout-output.png"
        Image.new("RGB", (10, 8), (255, 255, 255)).save(base)
        Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(red)
        Image.new("RGBA", (4, 4), (0, 0, 255, 255)).save(blue)
        layout.write_text(json.dumps({
            "root": str(self.root), "base": "cutout-base.png", "shadow_blur": 0,
            "layers": [
                {"path": "red.png", "x": 1, "y": 2, "height": 4},
                {"path": "blue.png", "x": 3, "y": 2, "height": 4}
            ]
        }), encoding="utf-8")
        subprocess.run(["python3", str(CUTOUTS), "--layout", str(layout), "--output", str(output)], check=True)
        result = Image.open(output).convert("RGB")
        self.assertEqual(result.getpixel((2, 3)), (255, 0, 0))
        self.assertEqual(result.getpixel((4, 3)), (0, 0, 255))

    def test_masked_rgba_extracts_only_semantic_overlay(self):
        source = self.root / "semantic-source.png"
        mask = self.root / "semantic-mask.png"
        output = self.root / "semantic-cutout.png"
        Image.new("RGB", (8, 6), (220, 170, 60)).save(source)
        alpha = Image.new("L", (8, 6), 0)
        for x in range(2, 6):
            for y in range(1, 5):
                alpha.putpixel((x, y), 255)
        alpha.save(mask)
        subprocess.run([
            "python3", str(MASKED_RGBA), "--image", str(source), "--mask", str(mask),
            "--output", str(output), "--padding", "0"
        ], check=True)
        result = Image.open(output).convert("RGBA")
        self.assertEqual(result.size, (4, 4))
        self.assertEqual(result.getpixel((1, 1)), (220, 170, 60, 255))


if __name__ == "__main__":
    unittest.main()
