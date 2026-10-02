#!/usr/bin/env python3
"""Create hash-bound QC evidence for one accepted continuity frame."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--shot", required=True)
    parser.add_argument("--accepted", required=True)
    parser.add_argument("--handoff", required=True)
    parser.add_argument("--capability-report", required=True)
    parser.add_argument("--content-evidence", required=True)
    parser.add_argument("--identity-evidence", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(args.project_root)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    shots = {item["id"]: item for item in manifest["shots"]}
    characters = {item["id"]: item for item in manifest["characters"]}
    scenes = {item["id"]: item for item in manifest["scenes"]}
    if args.shot not in shots:
        raise SystemExit(f"unknown shot: {args.shot}")
    shot = shots[args.shot]
    plan_shot = {item["id"]: item for item in plan["shots"]}[args.shot]
    accepted = resolve(root, args.accepted)
    handoff = resolve(root, args.handoff)
    capability_path = resolve(root, args.capability_report)
    content_path = resolve(root, args.content_evidence)
    identity_path = resolve(root, args.identity_evidence)
    for path in [accepted, handoff, capability_path, content_path, identity_path]:
        if not path.is_file():
            raise SystemExit(f"missing evidence: {path}")
    capability = json.loads(capability_path.read_text(encoding="utf-8"))
    content = json.loads(content_path.read_text(encoding="utf-8"))
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    if capability.get("pass") is not True:
        raise SystemExit("capability report failed")
    runtime = manifest["runtime"]
    if capability.get("url") != runtime.get("comfy_url"):
        raise SystemExit("capability report URL differs from manifest runtime")
    if capability.get("process_root") != runtime.get("expected_root") or capability.get("expected_root") != runtime.get("expected_root"):
        raise SystemExit("capability report did not verify manifest runtime root")
    route_capabilities = {
        "t2i-world-plate": ["zimage"],
        "world-plate-only": [],
        "krea2-identity-edit": ["krea2-identity"],
        "krea2-ostris-edit": ["krea2-ostris"],
        "qwen-multiref-edit": ["qwen-edit"],
        "sequential-masked-edit": ["qwen-edit"],
    }
    required_capabilities = [*route_capabilities[plan_shot["route"]], "ltx-director"]
    for name in required_capabilities:
        if capability.get("routes", {}).get(name, {}).get("pass") is not True:
            raise SystemExit(f"required capability did not pass: {name}")
    if content.get("pass") is not True or not content.get("reviewer") or not content.get("contact_sheet"):
        raise SystemExit("content evidence requires pass, reviewer and contact_sheet")
    accepted_hash = digest(accepted)
    if content.get("accepted_sha256") != accepted_hash:
        raise SystemExit("content evidence is not bound to the accepted image hash")
    contact_sheet = resolve(root, content["contact_sheet"])
    if not contact_sheet.is_file():
        raise SystemExit(f"missing contact sheet: {contact_sheet}")
    if content.get("contact_sheet_sha256") != digest(contact_sheet):
        raise SystemExit("content evidence is not bound to the contact sheet hash")
    if identity.get("pass") is not True:
        raise SystemExit("identity evidence failed")
    if identity.get("accepted_sha256") != accepted_hash:
        raise SystemExit("identity evidence is not bound to the accepted image hash")
    score = identity.get("arcface")
    if shot["cast"] and score is None and not (identity.get("metric_applicable") is False and identity.get("visual_pass") is True):
        raise SystemExit("identity evidence needs ArcFace or explicit visual-only verdict")
    if score is not None and score < 0.80:
        raise SystemExit(f"ArcFace below 0.80: {score}")
    if digest(accepted) != digest(handoff):
        raise SystemExit("handoff is not byte-identical to accepted")
    for cast_id in shot["cast"]:
        qc_path = resolve(root, characters[cast_id]["master_qc"])
        evidence = json.loads(qc_path.read_text(encoding="utf-8"))
        master_path = resolve(root, characters[cast_id]["master"])
        if evidence.get("approved") is not True or evidence.get("sha256") != digest(master_path):
            raise SystemExit(f"master QC failed for {cast_id}")
        if identity.get("master_sha256", {}).get(cast_id) != digest(master_path):
            raise SystemExit(f"identity evidence is not bound to master {cast_id}")
    world_plate = scenes[shot["scene"]].get("world_plate")
    if world_plate and not resolve(root, world_plate).is_file():
        raise SystemExit("world plate missing")

    out_path = Path(args.out)
    current = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {"shots": {}}
    current["capability_report"] = {"path": args.capability_report, "sha256": digest(capability_path)}
    current.setdefault("shots", {})[args.shot] = {
        "accepted": args.accepted,
        "accepted_sha256": accepted_hash,
        "handoff": args.handoff,
        "handoff_sha256": digest(handoff),
        "gates": {
            "capability": {"pass": True, "evidence": args.capability_report},
            "master": {"pass": True, "evidence": [characters[item]["master_qc"] for item in shot["cast"]]},
            "world": {"pass": True, "evidence": world_plate},
            "content": {**content, "evidence": args.content_evidence, "evidence_sha256": digest(content_path)},
            "identity": {**identity, "evidence": args.identity_evidence, "evidence_sha256": digest(identity_path)},
            "handoff": {"pass": True, "sha256": digest(handoff)},
        },
        "required_capabilities": required_capabilities,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
