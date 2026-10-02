#!/usr/bin/env python3
"""Compile a continuity manifest into an explicit per-shot route plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXACT_CHANGES = {"action", "pose", "transformation", "spirit", "insert", "remove"}
LOCAL_CHANGES = {"wardrobe", "prop", "damage"}
RESTAGE_CHANGES = {"world", "background", "lighting"}


def select_route(shot: dict, scene: dict) -> str:
    cast = shot["cast"]
    changes = set(shot["change"])
    if not cast:
        return "world-plate-only" if scene.get("world_plate") else "t2i-world-plate"
    if len(cast) > 1 or shot["precision"] == "exact":
        return "sequential-masked-edit"
    if changes & EXACT_CHANGES:
        return "qwen-multiref-edit"
    if changes & LOCAL_CHANGES:
        return "krea2-ostris-edit"
    if changes <= RESTAGE_CHANGES or shot["precision"] == "identity":
        return "krea2-identity-edit"
    return "qwen-multiref-edit"


def stages_for(shot: dict, route: str, character_index: dict, scene_index: dict) -> list[dict]:
    scene = scene_index[shot["scene"]]
    stages: list[dict] = []
    if route == "t2i-world-plate":
        stages.append({"name": "world", "interface": "zimage-t2i", "adapter": "scripts/run_zimage_t2i.mjs", "input": None})
        return stages
    if route == "world-plate-only":
        stages.append({"name": "world", "interface": "approved-world-plate", "adapter": None, "input": scene["world_plate"]})
        return stages

    stages.append(
        {
            "name": "world",
            "interface": "approved-world-plate",
            "adapter": None,
            "input": scene.get("world_plate"),
        }
    )
    if route == "sequential-masked-edit":
        stages.append({"name": "blocking", "interface": "approved-layout-or-pose-proxy", "adapter": None, "input": shot.get("blocking")})
        for index, cast_id in enumerate(shot["cast"], start=1):
            master = character_index[cast_id].get("letterbox_master") or character_index[cast_id]["master"]
            stages.append(
                {
                    "name": f"character-{index}-edit",
                    "interface": "qwen-multiref-edit",
                    "adapter": "scripts/run_qwen_edit.mjs",
                    "master": master,
                    "protect_previous_layers": True,
                }
            )
            stages.append(
                {
                    "name": f"character-{index}-composite",
                    "interface": "deterministic-mask-composite",
                    "adapter": "scripts/composite_with_mask.py",
                    "mask": shot.get("masks", {}).get(cast_id),
                    "freeze_previous_layers": True,
                }
            )
        stages.append({"name": "harmonize", "interface": "qwen-low-denoise-harmonize", "adapter": "scripts/run_qwen_edit.mjs", "settings": {"denoise": 0.25, "preserve_canvas": True}})
    else:
        cast_id = shot["cast"][0]
        master = character_index[cast_id].get("letterbox_master") or character_index[cast_id]["master"]
        adapter = "scripts/run_krea2_edit.mjs" if route.startswith("krea2-") else "scripts/run_qwen_edit.mjs"
        stages.append(
            {
                "name": "edit",
                "interface": route,
                "adapter": adapter,
                "master": master,
                "previous_state": shot.get("previous_state"),
            }
        )
    return stages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    characters = {item["id"]: item for item in manifest["characters"]}
    scenes = {item["id"]: item for item in manifest["scenes"]}
    planned = []
    for shot in manifest["shots"]:
        scene = scenes[shot["scene"]]
        route = select_route(shot, scene)
        planned.append(
            {
                "id": shot["id"],
                "route": route,
                "dependencies": {
                    "scene": shot["scene"],
                    "cast": shot["cast"],
                    "previous_state": shot.get("previous_state"),
                },
                "action": shot["action"],
                "stages": stages_for(shot, route, characters, scenes),
                "gates": ["capability", "master", "world", "content", "identity", "handoff"],
                "output": shot["output"],
            }
        )

    plan = {
        "project": manifest["project"],
        "resolution": manifest["resolution"],
        "source_manifest": str(Path(args.manifest)),
        "shots": planned,
        "ltx_release_rule": "Only outputs passing every listed gate may enter ltx-handoff.",
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
