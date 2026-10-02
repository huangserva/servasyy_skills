#!/usr/bin/env python3
"""Validate a hash-bound ledger for every still released to a video model."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path


CONTENT_GATES = {"exact_cast", "identity", "style", "action", "duplicate", "dimensions"}
IDENTITY_METHOD = "hash-bound-labeled-contact-sheet-comparison"
ARCFACE_REASON_CODE = "arcface_and_visual_master_comparison"
ARCFACE_THRESHOLD = 0.80


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def resolve(root: Path, value: str | None) -> Path | None:
    if not value:
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


def load_json(path: Path, errors: list[dict], scope: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append({"scope": scope, "code": "invalid_json", "error": str(error)})
        return {}
    if not isinstance(value, dict):
        errors.append({"scope": scope, "code": "invalid_json_type", "error": "expected an object"})
        return {}
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    ledger_path = Path(args.ledger)
    errors: list[dict] = []
    ledger = load_json(ledger_path, errors, "ledger")
    resolution = ledger.get("resolution")
    records = ledger.get("records")
    masters = ledger.get("masters")
    if not isinstance(resolution, list) or len(resolution) != 2:
        errors.append({"scope": "ledger", "code": "invalid_resolution"})
    if not isinstance(records, list):
        errors.append({"scope": "ledger", "code": "missing_records"})
        records = []
    if not isinstance(masters, dict):
        errors.append({"scope": "ledger", "code": "missing_masters"})
        masters = {}
    expected = ledger.get("expected_states")
    if not isinstance(expected, int) or expected <= 0 or expected != len(records):
        errors.append({"scope": "ledger", "code": "state_count_mismatch", "expected": expected, "actual": len(records)})
    identity_policy = ledger.get("identity_policy") or {}
    minimum_metric_states = identity_policy.get("minimum_metric_states", 0)
    if (
        not isinstance(minimum_metric_states, int)
        or isinstance(minimum_metric_states, bool)
        or minimum_metric_states < 0
    ):
        errors.append({"scope": "ledger", "code": "invalid_minimum_metric_states"})
        minimum_metric_states = 0

    source_plan = resolve(root, ledger.get("source_plan"))
    if source_plan is None or not source_plan.is_file():
        errors.append({"scope": "ledger", "code": "missing_source_plan"})
    elif ledger.get("source_plan_sha256") != digest(source_plan):
        errors.append({"scope": "ledger", "code": "source_plan_hash_mismatch"})

    source_index = resolve(root, ledger.get("source_index"))
    index_records: dict[str, dict] = {}
    if source_index is None or not source_index.is_file():
        errors.append({"scope": "ledger", "code": "missing_source_index"})
    elif ledger.get("source_index_sha256") != digest(source_index):
        errors.append({"scope": "ledger", "code": "source_index_hash_mismatch"})
    else:
        index = load_json(source_index, errors, "source_index")
        index_records = {item.get("id"): item for item in index.get("records", []) if isinstance(item, dict)}
        if index.get("pass") is not True or index.get("actual_count") != expected or set(index_records) != {item.get("id") for item in records if isinstance(item, dict)}:
            errors.append({"scope": "ledger", "code": "source_index_coverage_mismatch"})

    review_path = resolve(root, ledger.get("review_evidence"))
    review: dict = {}
    review_states: dict[str, dict] = {}
    if review_path is None or not review_path.is_file():
        errors.append({"scope": "ledger", "code": "missing_review_evidence"})
    elif ledger.get("review_evidence_sha256") != digest(review_path):
        errors.append({"scope": "ledger", "code": "review_evidence_hash_mismatch"})
    else:
        review = load_json(review_path, errors, "review_evidence")
        if review.get("pass") is not True or review.get("final_index_sha256") != ledger.get("source_index_sha256"):
            errors.append({"scope": "ledger", "code": "review_evidence_not_bound"})
        review_records = review.get("states")
        if not isinstance(review_records, list):
            errors.append({"scope": "ledger", "code": "missing_state_reviews"})
        else:
            review_states = {item.get("id"): item for item in review_records if isinstance(item, dict)}
            if len(review_states) != len(review_records) or set(review_states) != {item.get("id") for item in records if isinstance(item, dict)}:
                errors.append({"scope": "ledger", "code": "state_review_coverage_mismatch"})

    master_review_path = resolve(root, ledger.get("master_review"))
    master_review: dict = {}
    master_review_states: dict[str, dict] = {}
    master_review_sheet: Path | None = None
    if master_review_path is None or not master_review_path.is_file():
        errors.append({"scope": "ledger", "code": "missing_master_review"})
    elif ledger.get("master_review_sha256") != digest(master_review_path):
        errors.append({"scope": "ledger", "code": "master_review_hash_mismatch"})
    else:
        master_review = load_json(master_review_path, errors, "master_review")
        master_records = master_review.get("masters")
        if not isinstance(master_records, list):
            errors.append({"scope": "ledger", "code": "missing_master_review_records"})
        else:
            master_review_states = {
                item.get("id"): item for item in master_records if isinstance(item, dict)
            }
            if (
                master_review.get("pass") is not True
                or not master_review.get("reviewer")
                or len(master_review_states) != len(master_records)
                or set(master_review_states) != set(masters)
            ):
                errors.append({"scope": "ledger", "code": "master_review_coverage_mismatch"})
        master_review_sheet = resolve(root, master_review.get("contact_sheet"))
        if (
            master_review_sheet is None
            or not master_review_sheet.is_file()
            or master_review.get("contact_sheet_sha256") != digest(master_review_sheet)
        ):
            errors.append({"scope": "ledger", "code": "master_review_sheet_mismatch"})

    master_hashes: dict[str, str] = {}
    for master_id, item in masters.items():
        if not isinstance(item, dict):
            errors.append({"scope": master_id, "code": "invalid_master_record"})
            continue
        path = resolve(root, item.get("path"))
        if path is None or not path.is_file():
            errors.append({"scope": master_id, "code": "missing_master"})
            continue
        actual_hash = digest(path)
        master_hashes[master_id] = actual_hash
        reviewed = master_review_states.get(master_id) or {}
        if (
            item.get("sha256") != actual_hash
            or item.get("approved") is not True
            or item.get("one_face") is not True
            or item.get("face_count") != 1
            or item.get("reviewer") != master_review.get("reviewer")
            or item.get("review_state") != master_id
            or item.get("contact_sheet") != master_review.get("contact_sheet")
            or item.get("contact_sheet_sha256") != master_review.get("contact_sheet_sha256")
            or reviewed.get("path") != item.get("path")
            or reviewed.get("sha256") != actual_hash
            or reviewed.get("approved") is not True
            or reviewed.get("one_face") is not True
            or reviewed.get("face_count") != 1
            or reviewed.get("contact_cell") != master_id
        ):
            errors.append({"scope": master_id, "code": "invalid_master_evidence"})

    ids: set[str] = set()
    earlier: set[str] = set()
    by_image_hash: defaultdict[str, list[str]] = defaultdict(list)
    arcface_cache: dict[Path, tuple[dict, dict[str, dict]]] = {}
    motion_cache: dict[Path, dict[str, dict]] = {}
    metric_identity_states = 0

    def verify_arcface_reference(
        state_id: str,
        identity: dict,
        accepted_hash: str,
        cast: list[str],
        bound: dict,
        applicable: bool,
    ) -> dict:
        evidence_ref = identity.get("arcface_evidence")
        if not isinstance(evidence_ref, dict):
            errors.append({"scope": state_id, "code": "missing_arcface_evidence"})
            return {}
        evidence_path = resolve(root, evidence_ref.get("path"))
        if evidence_path is None or not evidence_path.is_file():
            errors.append({"scope": state_id, "code": "missing_arcface_evidence_file"})
            return {}
        if evidence_ref.get("sha256") != digest(evidence_path):
            errors.append({"scope": state_id, "code": "arcface_evidence_hash_mismatch"})
            return {}
        if evidence_path not in arcface_cache:
            document = load_json(evidence_path, errors, "arcface_evidence")
            evidence_records = document.get("records")
            by_id = {
                item.get("id"): item
                for item in evidence_records or []
                if isinstance(item, dict)
            }
            if (
                document.get("pass") is not True
                or not isinstance(evidence_records, list)
                or len(by_id) != len(evidence_records)
                or document.get("thresholds", {}).get("arcface") != ARCFACE_THRESHOLD
            ):
                errors.append({"scope": "arcface_evidence", "code": "invalid_arcface_document"})
            arcface_cache[evidence_path] = (document, by_id)
        _document, evidence_by_id = arcface_cache[evidence_path]
        evidence_record = evidence_by_id.get(evidence_ref.get("record_id")) or {}
        if (
            evidence_ref.get("record_id") != state_id
            or evidence_record.get("id") != state_id
            or evidence_record.get("accepted_sha256") != accepted_hash
            or evidence_record.get("cast") != cast
            or evidence_record.get("master_sha256") != bound
            or evidence_record.get("metric_applicable") is not applicable
            or evidence_record.get("pass") is not True
        ):
            errors.append({"scope": state_id, "code": "arcface_record_binding_mismatch"})
        return evidence_record

    for record in records:
        if not isinstance(record, dict):
            errors.append({"scope": "records", "code": "invalid_record"})
            continue
        state_id = record.get("id")
        if not state_id or state_id in ids:
            errors.append({"scope": state_id or "records", "code": "missing_or_duplicate_id"})
            continue
        ids.add(state_id)
        accepted = resolve(root, record.get("accepted"))
        handoff = resolve(root, record.get("handoff"))
        if accepted is None or not accepted.is_file():
            errors.append({"scope": state_id, "code": "missing_accepted"})
            earlier.add(state_id)
            continue
        accepted_hash = digest(accepted)
        by_image_hash[accepted_hash].append(state_id)
        if record.get("accepted_sha256") != accepted_hash:
            errors.append({"scope": state_id, "code": "accepted_hash_mismatch"})
        index_record = index_records.get(state_id)
        if index_record and (
            index_record.get("path") != record.get("accepted")
            or index_record.get("sha256") != accepted_hash
        ):
            errors.append({"scope": state_id, "code": "source_index_record_mismatch"})
        if handoff is None or not handoff.is_file():
            errors.append({"scope": state_id, "code": "missing_handoff"})
        else:
            handoff_hash = digest(handoff)
            if record.get("handoff_sha256") != handoff_hash or handoff_hash != accepted_hash:
                errors.append({"scope": state_id, "code": "handoff_hash_mismatch"})
        try:
            if resolution and image_size(accepted) != tuple(resolution):
                errors.append({"scope": state_id, "code": "dimension_mismatch"})
        except ValueError as error:
            errors.append({"scope": state_id, "code": "invalid_image", "error": str(error)})

        sheet = resolve(root, record.get("contact_sheet"))
        if sheet is None or not sheet.is_file():
            errors.append({"scope": state_id, "code": "missing_contact_sheet"})
        elif record.get("contact_sheet_sha256") != digest(sheet):
            errors.append({"scope": state_id, "code": "contact_sheet_hash_mismatch"})
        if not record.get("reviewer"):
            errors.append({"scope": state_id, "code": "missing_reviewer"})
        elif review and record.get("reviewer") != review.get("reviewer"):
            errors.append({"scope": state_id, "code": "reviewer_mismatch"})
        gates = record.get("content_gates") or {}
        if set(gates) != CONTENT_GATES or any(gates.get(name) is not True for name in CONTENT_GATES):
            errors.append({"scope": state_id, "code": "content_gate_failed"})

        state_review = review_states.get(state_id)
        if not state_review:
            errors.append({"scope": state_id, "code": "missing_state_review"})
        else:
            if (
                record.get("review_state") != state_id
                or record.get("review_record_sha256") != ledger.get("review_evidence_sha256")
                or state_review.get("accepted_sha256") != accepted_hash
                or state_review.get("cast") != record.get("cast")
                or state_review.get("gates") != gates
                or state_review.get("identity_evidence") != record.get("identity_evidence")
                or state_review.get("contact_cell") != state_id
            ):
                errors.append({"scope": state_id, "code": "state_review_binding_mismatch"})
            sheets = review.get("contact_sheets") or []
            sheet_index = state_review.get("contact_sheet_index")
            if not isinstance(sheet_index, int) or not 0 <= sheet_index < len(sheets):
                errors.append({"scope": state_id, "code": "state_review_sheet_mismatch"})
            else:
                reviewed_sheet = sheets[sheet_index]
                if (
                    reviewed_sheet.get("path") != record.get("contact_sheet")
                    or reviewed_sheet.get("sha256") != record.get("contact_sheet_sha256")
                ):
                    errors.append({"scope": state_id, "code": "state_review_sheet_mismatch"})

        cast = record.get("cast") or []
        bound = record.get("master_sha256") or {}
        for cast_id in cast:
            if cast_id not in master_hashes:
                errors.append({"scope": state_id, "code": "unknown_master", "master": cast_id})
            elif bound.get(cast_id) != master_hashes[cast_id]:
                errors.append({"scope": state_id, "code": "identity_master_hash_mismatch", "master": cast_id})
        identity = record.get("identity_evidence") or {}
        metric_applicable = identity.get("metric_applicable")
        if not isinstance(metric_applicable, bool):
            errors.append({"scope": state_id, "code": "invalid_metric_applicability"})
        expected_reason_code = (
            ARCFACE_REASON_CODE
            if cast and metric_applicable is True
            else ("hash_bound_visual_master_comparison" if cast else "zero_cast_state")
        )
        if (
            identity.get("pass") is not True
            or identity.get("visual_pass") is not True
            or identity.get("method") != IDENTITY_METHOD
            or identity.get("reviewer") != record.get("reviewer")
            or identity.get("master_ids") != cast
            or identity.get("contact_cell") != state_id
            or identity.get("reason_code") != expected_reason_code
            or not identity.get("reason")
        ):
            errors.append({"scope": state_id, "code": "invalid_identity_review_binding"})
        if cast and identity.get("pass") is not True:
            errors.append({"scope": state_id, "code": "identity_gate_failed"})
        score = identity.get("arcface")
        if cast and metric_applicable is True:
            metric_identity_states += 1
            if not isinstance(score, (int, float)) or isinstance(score, bool):
                errors.append({"scope": state_id, "code": "missing_arcface_score"})
            elif score < ARCFACE_THRESHOLD:
                errors.append({"scope": state_id, "code": "arcface_below_threshold"})
            evidence_record = verify_arcface_reference(
                state_id, identity, accepted_hash, cast, bound, True
            )
            if evidence_record.get("arcface") != score:
                errors.append({"scope": state_id, "code": "arcface_record_binding_mismatch"})
        elif cast:
            if score is not None:
                errors.append({"scope": state_id, "code": "unexpected_arcface_score"})
            if identity.get("arcface_evidence") is not None:
                verify_arcface_reference(
                    state_id, identity, accepted_hash, cast, bound, False
                )
            if not (metric_applicable is False and identity.get("visual_pass") is True and identity.get("reason")):
                errors.append({"scope": state_id, "code": "missing_identity_evidence"})
        elif identity.get("arcface_evidence") is not None:
            if score is not None:
                errors.append({"scope": state_id, "code": "unexpected_arcface_score"})
            verify_arcface_reference(
                state_id, identity, accepted_hash, cast, bound, False
            )
        world_plate = resolve(root, record.get("world_plate"))
        if world_plate is None or not world_plate.is_file():
            errors.append({"scope": state_id, "code": "missing_world_plate"})
        elif record.get("world_plate_sha256") != digest(world_plate):
            errors.append({"scope": state_id, "code": "world_plate_hash_mismatch"})
        source_metadata = resolve(root, record.get("source_metadata"))
        if source_metadata is not None:
            if not source_metadata.is_file():
                errors.append({"scope": state_id, "code": "missing_source_metadata"})
            elif record.get("source_metadata_sha256") != digest(source_metadata):
                errors.append({"scope": state_id, "code": "source_metadata_hash_mismatch"})
        hold_of = record.get("hold_of")
        hold_motion = record.get("hold_motion_evidence")
        if hold_of:
            if not record.get("hold_reason") or not isinstance(hold_motion, dict):
                errors.append({"scope": state_id, "code": "missing_hold_motion_evidence"})
            else:
                evidence_path = resolve(root, hold_motion.get("evidence"))
                if evidence_path is None or not evidence_path.is_file():
                    errors.append({"scope": state_id, "code": "missing_hold_motion_file"})
                elif hold_motion.get("evidence_sha256") != digest(evidence_path):
                    errors.append({"scope": state_id, "code": "hold_motion_evidence_hash_mismatch"})
                else:
                    if evidence_path not in motion_cache:
                        document = load_json(evidence_path, errors, "hold_motion_evidence")
                        motion_records = document.get("records")
                        motion_by_shot = {
                            item.get("shot"): item
                            for item in motion_records or []
                            if isinstance(item, dict)
                        }
                        if (
                            document.get("pass") is not True
                            or not isinstance(motion_records, list)
                            or len(motion_by_shot) != len(motion_records)
                        ):
                            errors.append({"scope": "hold_motion_evidence", "code": "invalid_hold_motion_document"})
                        motion_cache[evidence_path] = motion_by_shot
                    motion_record = motion_cache[evidence_path].get(hold_motion.get("shot")) or {}
                    video = resolve(root, hold_motion.get("video"))
                    sheet = resolve(root, hold_motion.get("every_frame_sheet"))
                    gates = hold_motion.get("review_gates")
                    if (
                        hold_motion.get("shot") != record.get("shot")
                        or hold_motion.get("review_pass") is not True
                        or not isinstance(gates, dict)
                        or not gates
                        or any(value is not True for value in gates.values())
                        or video is None
                        or not video.is_file()
                        or hold_motion.get("video_sha256") != digest(video)
                        or sheet is None
                        or not sheet.is_file()
                        or hold_motion.get("every_frame_sheet_sha256") != digest(sheet)
                        or motion_record.get("video") != hold_motion.get("video")
                        or motion_record.get("video_sha256") != hold_motion.get("video_sha256")
                        or motion_record.get("every_frame_sheet") != hold_motion.get("every_frame_sheet")
                        or motion_record.get("every_frame_sheet_sha256") != hold_motion.get("every_frame_sheet_sha256")
                        or motion_record.get("reviewer") != hold_motion.get("reviewer")
                        or motion_record.get("review_gates") != gates
                        or motion_record.get("review_pass") is not True
                    ):
                        errors.append({"scope": state_id, "code": "hold_motion_record_binding_mismatch"})
        elif hold_motion is not None:
            errors.append({"scope": state_id, "code": "unexpected_hold_motion_evidence"})
        earlier.add(state_id)

    records_by_id = {record.get("id"): record for record in records if isinstance(record, dict)}
    for image_hash, state_ids in by_image_hash.items():
        if len(state_ids) < 2:
            continue
        first = state_ids[0]
        seen = {first}
        for state_id in state_ids[1:]:
            record = records_by_id[state_id]
            hold_of = record.get("hold_of")
            if hold_of not in seen or not record.get("hold_reason"):
                errors.append({
                    "scope": state_id,
                    "code": "undeclared_duplicate_frame",
                    "same_hash_states": state_ids,
                    "sha256": image_hash,
                })
            seen.add(state_id)

    duplicate_states = sum(max(0, len(state_ids) - 1) for state_ids in by_image_hash.values())
    if metric_identity_states < minimum_metric_states:
        errors.append({
            "scope": "ledger",
            "code": "insufficient_metric_identity_states",
            "minimum": minimum_metric_states,
            "actual": metric_identity_states,
        })
    report = {
        "pass": not errors,
        "expected_states": expected,
        "actual_states": len(records),
        "unique_ids": len(ids),
        "unique_image_hashes": len(by_image_hash),
        "declared_hold_states": duplicate_states,
        "metric_identity_states": metric_identity_states,
        "errors": errors,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
