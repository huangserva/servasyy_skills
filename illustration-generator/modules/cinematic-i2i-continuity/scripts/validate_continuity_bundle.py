#!/usr/bin/env python3
"""Validate preflight and release invariants for a continuity run bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from plan_continuity import select_route, stages_for


GATES = {"capability", "master", "world", "content", "identity", "handoff"}


def local_path(root: Path, value: str | None) -> Path | None:
    if not value or value.startswith(("remote:", "/home/")):
        return None
    path = Path(value)
    return path if path.is_absolute() else root / path


def image_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 9 < len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            marker = data[offset + 1]
            length = int.from_bytes(data[offset + 2 : offset + 4], "big")
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                return int.from_bytes(data[offset + 7 : offset + 9], "big"), int.from_bytes(data[offset + 5 : offset + 7], "big")
            offset += 2 + length
    raise ValueError(f"unsupported image: {path}")


def add_missing(errors: list[dict], root: Path, scope: str, label: str, value: str | None) -> None:
    path = local_path(root, value)
    if path is not None and not path.is_file():
        errors.append({"scope": scope, "error": f"{label} not found: {value}"})


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("plan")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--phase", choices=["preflight", "release"], default="preflight")
    parser.add_argument("--qc")
    parser.add_argument("--out")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    root = Path(args.project_root)
    errors: list[dict] = []
    warnings: list[dict] = []

    for field in ["project", "resolution", "runtime", "characters", "scenes", "shots"]:
        if field not in manifest:
            errors.append({"scope": "manifest", "error": f"missing field {field}"})
    if errors:
        return finish(errors, warnings, args.out)

    target_w, target_h = manifest["resolution"]
    runtime = manifest["runtime"]
    if not runtime.get("comfy_url") or not runtime.get("expected_root"):
        errors.append({"scope": "runtime", "code": "incomplete_runtime", "error": "runtime requires comfy_url and expected_root"})
    target_ar = target_w / target_h
    characters: dict[str, dict] = {}
    character_forms: set[tuple[str, str]] = set()
    for item in manifest["characters"]:
        item_id = item.get("id")
        if not item_id or item_id in characters:
            errors.append({"scope": "characters", "error": f"missing or duplicate id: {item_id}"})
            continue
        characters[item_id] = item
        form_key = (item.get("character"), item.get("form"))
        if None in form_key or form_key in character_forms:
            errors.append({"scope": item_id, "code": "duplicate_character_form", "error": f"missing or duplicate character/form: {form_key}"})
        character_forms.add(form_key)
        if item.get("one_face") is not True:
            errors.append({"scope": item_id, "error": "master must be certified one_face=true"})
        master = item.get("master")
        if not master:
            errors.append({"scope": item_id, "error": "missing canonical master"})
            continue
        add_missing(errors, root, item_id, "master", master)
        size = item.get("master_size")
        if not size or not size[1]:
            errors.append({"scope": item_id, "error": "missing master_size"})
            continue
        master_path = local_path(root, master)
        if master_path and master_path.is_file():
            try:
                if image_size(master_path) != tuple(size):
                    errors.append({"scope": item_id, "code": "master_size_mismatch", "error": "declared master_size differs from image"})
            except ValueError as error:
                errors.append({"scope": item_id, "error": str(error)})
        master_qc = item.get("master_qc")
        master_qc_path = local_path(root, master_qc)
        if not master_qc or master_qc_path is None or not master_qc_path.is_file():
            errors.append({"scope": item_id, "code": "missing_master_qc", "error": "master_qc JSON is required"})
        else:
            evidence = json.loads(master_qc_path.read_text(encoding="utf-8"))
            actual_master_hash = digest(master_path) if master_path and master_path.is_file() else None
            if evidence.get("approved") is not True or evidence.get("face_count") != 1 or evidence.get("master") != master or (actual_master_hash and evidence.get("sha256") != actual_master_hash):
                errors.append({"scope": item_id, "code": "invalid_master_qc", "error": "master_qc must approve this exact master hash with face_count=1"})
        if abs((size[0] / size[1]) - target_ar) / target_ar > 0.01:
            letterbox = item.get("letterbox_master")
            letterbox_size = item.get("letterbox_size")
            if not letterbox or letterbox_size != [target_w, target_h]:
                errors.append({"scope": item_id, "error": "AR mismatch requires a prebuilt target-size letterbox_master; crop is forbidden"})
            else:
                add_missing(errors, root, item_id, "letterbox_master", letterbox)
                letterbox_path = local_path(root, letterbox)
                if letterbox_path and letterbox_path.is_file():
                    try:
                        if image_size(letterbox_path) != (target_w, target_h):
                            errors.append({"scope": item_id, "code": "letterbox_size_mismatch", "error": "letterbox image dimensions mismatch"})
                    except ValueError as error:
                        errors.append({"scope": item_id, "error": str(error)})

    scenes: dict[str, dict] = {}
    for item in manifest["scenes"]:
        item_id = item.get("id")
        if not item_id or item_id in scenes:
            errors.append({"scope": "scenes", "error": f"missing or duplicate id: {item_id}"})
            continue
        scenes[item_id] = item
        if item.get("world_plate"):
            add_missing(errors, root, item_id, "world_plate", item["world_plate"])

    shots: dict[str, dict] = {}
    earlier_shots: set[str] = set()
    for shot in manifest["shots"]:
        shot_id = shot.get("id")
        if not shot_id or shot_id in shots:
            errors.append({"scope": "shots", "error": f"missing or duplicate id: {shot_id}"})
            continue
        shots[shot_id] = shot
        for field in ["scene", "cast", "exact_count", "action", "change", "precision", "output"]:
            if field not in shot:
                errors.append({"scope": shot_id, "error": f"missing field {field}"})
        if shot.get("scene") not in scenes:
            errors.append({"scope": shot_id, "error": f"unknown scene {shot.get('scene')}"})
        elif shot.get("cast") and not scenes[shot["scene"]].get("world_plate"):
            errors.append({"scope": shot_id, "code": "missing_world_plate", "error": "shots with recurring cast require an approved world_plate"})
        previous_state = shot.get("previous_state")
        if previous_state and previous_state not in earlier_shots:
            errors.append({"scope": shot_id, "code": "invalid_previous_state", "error": f"previous_state must name an earlier manifest shot: {previous_state}"})
        cast = shot.get("cast", [])
        unknown = [cast_id for cast_id in cast if cast_id not in characters]
        if unknown:
            errors.append({"scope": shot_id, "error": f"unknown cast {unknown}"})
        if shot.get("exact_count") != len(cast) and not shot.get("notes"):
            errors.append({"scope": shot_id, "error": "exact_count differs from cast length without notes"})
        if shot.get("center_crop"):
            errors.append({"scope": shot_id, "error": "center_crop is forbidden"})
        needs_layout = len(cast) > 1 or shot.get("precision") == "exact"
        if needs_layout:
            blocking = shot.get("blocking")
            if not blocking:
                errors.append({"scope": shot_id, "error": "exact/multi-person shot requires blocking"})
            else:
                add_missing(errors, root, shot_id, "blocking", blocking)
            masks = shot.get("masks") or {}
            for cast_id in cast:
                if cast_id not in masks:
                    errors.append({"scope": shot_id, "code": "missing_mask", "error": f"missing mask for {cast_id}"})
                else:
                    add_missing(errors, root, shot_id, f"mask {cast_id}", masks[cast_id])
        earlier_shots.add(shot_id)

    plan_shots = {item.get("id"): item for item in plan.get("shots", [])}
    if set(plan_shots) != set(shots):
        errors.append({"scope": "plan", "error": "plan shot IDs do not match manifest"})
    for shot_id, item in plan_shots.items():
        shot = shots.get(shot_id, {})
        cast = shot.get("cast", [])
        route = item.get("route", "")
        expected_route = select_route(shot, scenes[shot["scene"]]) if shot.get("scene") in scenes else None
        if route != expected_route:
            errors.append({"scope": shot_id, "code": "route_tampered", "error": f"route differs from planner: {route} != {expected_route}"})
        elif item.get("stages") != stages_for(shot, expected_route, characters, scenes):
            errors.append({"scope": shot_id, "code": "stages_tampered", "error": "stages differ from planner output"})
        if cast and ("t2i" in route or route == "world-plate-only"):
            errors.append({"scope": shot_id, "code": "t2i_for_cast", "error": "recurring cast may not use a T2I/world-only final route"})
        if (len(cast) > 1 or shot.get("precision") == "exact") and route != "sequential-masked-edit":
            errors.append({"scope": shot_id, "error": "exact/multi-person shot bypasses sequential masked edit"})
        if set(item.get("gates", [])) != GATES:
            errors.append({"scope": shot_id, "error": "incomplete gate list"})

    if args.phase == "release":
        if not args.qc:
            errors.append({"scope": "release", "error": "--qc is required for release"})
        else:
            qc = json.loads(Path(args.qc).read_text(encoding="utf-8"))
            capability_report = {}
            capability_evidence = qc.get("capability_report", {})
            capability_path = local_path(root, capability_evidence.get("path"))
            if capability_path is None or not capability_path.is_file():
                errors.append({"scope": "release", "code": "missing_capability_report", "error": "QC lacks a real capability report"})
            elif digest(capability_path) != capability_evidence.get("sha256"):
                errors.append({"scope": "release", "code": "capability_report_hash_mismatch", "error": "capability report hash mismatch"})
            else:
                capability_report = json.loads(capability_path.read_text(encoding="utf-8"))
                if capability_report.get("pass") is not True:
                    errors.append({"scope": "release", "code": "capability_report_failed", "error": "capability report did not pass"})
                if capability_report.get("url") != runtime.get("comfy_url"):
                    errors.append({"scope": "release", "code": "capability_url_mismatch", "error": "capability report URL differs from manifest runtime"})
                if capability_report.get("process_root") != runtime.get("expected_root") or capability_report.get("expected_root") != runtime.get("expected_root"):
                    errors.append({"scope": "release", "code": "capability_root_mismatch", "error": "capability report did not verify the manifest runtime root"})
            qc_shots = qc.get("shots", {})
            for shot_id, shot in shots.items():
                item = qc_shots.get(shot_id)
                if not item:
                    errors.append({"scope": shot_id, "error": "missing QC record"})
                    continue
                for gate in GATES:
                    if item.get("gates", {}).get(gate, {}).get("pass") is not True:
                        errors.append({"scope": shot_id, "code": "gate_not_passed", "error": f"gate not passed: {gate}"})
                route_capabilities = {
                    "t2i-world-plate": ["zimage"],
                    "world-plate-only": [],
                    "krea2-identity-edit": ["krea2-identity"],
                    "krea2-ostris-edit": ["krea2-ostris"],
                    "qwen-multiref-edit": ["qwen-edit"],
                    "sequential-masked-edit": ["qwen-edit"],
                }
                expected_capabilities = [*route_capabilities[plan_shots[shot_id]["route"]], "ltx-director"]
                if item.get("required_capabilities") != expected_capabilities:
                    errors.append({"scope": shot_id, "code": "required_capabilities_tampered", "error": "QC capability list differs from plan route"})
                for capability in expected_capabilities:
                    if capability_report.get("routes", {}).get(capability, {}).get("pass") is not True:
                        errors.append({"scope": shot_id, "code": "required_capability_failed", "error": f"required capability did not pass: {capability}"})
                for gate_name in ["content", "identity"]:
                    gate = item.get("gates", {}).get(gate_name, {})
                    evidence_path = local_path(root, gate.get("evidence"))
                    if evidence_path is None or not evidence_path.is_file():
                        errors.append({"scope": shot_id, "code": "missing_gate_evidence", "error": f"missing {gate_name} evidence"})
                        continue
                    if digest(evidence_path) != gate.get("evidence_sha256"):
                        errors.append({"scope": shot_id, "code": "gate_evidence_hash_mismatch", "error": f"{gate_name} evidence hash mismatch"})
                        continue
                    source_evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                    if source_evidence.get("pass") is not True or gate.get("pass") != source_evidence.get("pass"):
                        errors.append({"scope": shot_id, "code": "gate_evidence_failed", "error": f"{gate_name} evidence did not pass"})
                    if gate_name == "identity":
                        if gate.get("arcface") != source_evidence.get("arcface") or gate.get("metric_applicable") != source_evidence.get("metric_applicable") or gate.get("visual_pass") != source_evidence.get("visual_pass"):
                            errors.append({"scope": shot_id, "code": "identity_evidence_mismatch", "error": "identity gate differs from source evidence"})
                    if source_evidence.get("accepted_sha256") != item.get("accepted_sha256"):
                        errors.append({"scope": shot_id, "code": "gate_evidence_wrong_image", "error": f"{gate_name} evidence is not bound to accepted image"})
                    if gate_name == "identity":
                        for cast_id in shot.get("cast", []):
                            master = characters[cast_id]["master"]
                            master_path = local_path(root, master)
                            if master_path and source_evidence.get("master_sha256", {}).get(cast_id) != digest(master_path):
                                errors.append({"scope": shot_id, "code": "identity_evidence_wrong_master", "error": f"identity evidence is not bound to master {cast_id}"})
                    if gate_name == "content":
                        contact_sheet = local_path(root, source_evidence.get("contact_sheet"))
                        if not source_evidence.get("reviewer"):
                            errors.append({"scope": shot_id, "code": "missing_content_reviewer", "error": "content evidence lacks reviewer"})
                        if contact_sheet is None or not contact_sheet.is_file():
                            errors.append({"scope": shot_id, "code": "missing_contact_sheet", "error": "content evidence contact sheet is missing"})
                        elif source_evidence.get("contact_sheet_sha256") != digest(contact_sheet):
                            errors.append({"scope": shot_id, "code": "contact_sheet_hash_mismatch", "error": "contact sheet hash mismatch"})
                accepted = item.get("accepted")
                if accepted != shot.get("output"):
                    errors.append({"scope": shot_id, "error": "accepted path differs from manifest output"})
                accepted_path = local_path(root, accepted)
                if accepted_path is None or not accepted_path.is_file():
                    errors.append({"scope": shot_id, "error": f"accepted output missing: {accepted}"})
                else:
                    if item.get("accepted_sha256") != digest(accepted_path):
                        errors.append({"scope": shot_id, "code": "accepted_hash_mismatch", "error": "accepted file hash differs from QC"})
                    try:
                        if image_size(accepted_path) != (target_w, target_h):
                            errors.append({"scope": shot_id, "error": "accepted output dimensions mismatch"})
                    except ValueError as error:
                        errors.append({"scope": shot_id, "error": str(error)})
                identity = item.get("gates", {}).get("identity", {})
                if shot.get("cast"):
                    score = identity.get("arcface")
                    if score is not None and score < 0.80:
                        errors.append({"scope": shot_id, "error": f"ArcFace below 0.80: {score}"})
                    if score is None and not (identity.get("metric_applicable") is False and identity.get("visual_pass") is True):
                        errors.append({"scope": shot_id, "error": "identity needs ArcFace or explicit non-applicable visual pass"})
                handoff = item.get("handoff")
                handoff_path = local_path(root, handoff)
                if handoff_path is None or not handoff_path.is_file():
                    errors.append({"scope": shot_id, "error": f"LTX handoff missing: {handoff}"})
                else:
                    if item.get("handoff_sha256") != digest(handoff_path):
                        errors.append({"scope": shot_id, "code": "handoff_record_hash_mismatch", "error": "handoff file hash differs from QC"})
                    try:
                        if image_size(handoff_path) != (target_w, target_h):
                            errors.append({"scope": shot_id, "error": "LTX handoff dimensions mismatch"})
                    except ValueError as error:
                        errors.append({"scope": shot_id, "error": str(error)})
                    if accepted_path and accepted_path.is_file() and digest(handoff_path) != digest(accepted_path):
                        errors.append({"scope": shot_id, "code": "handoff_hash_mismatch", "error": "LTX handoff content differs from accepted output"})

    return finish(errors, warnings, args.out)


def finish(errors: list[dict], warnings: list[dict], out: str | None) -> int:
    report = {"pass": not errors, "errors": errors, "warnings": warnings}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
