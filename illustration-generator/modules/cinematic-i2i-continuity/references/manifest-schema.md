# Continuity Manifest Schema

Use JSON. Paths may be relative to the project root or explicit remote asset identifiers.

```json
{
  "project": "example-film",
  "resolution": [1280, 720],
  "runtime": {
    "comfy_url": "http://127.0.0.1:8188",
    "expected_root": "/path/to/unified/ComfyUI"
  },
  "characters": [
    {
      "id": "hero-normal",
      "character": "hero",
      "form": "normal",
      "master": "masters/hero-normal.png",
      "master_size": [1280, 720],
      "master_qc": "qc/masters/hero-normal.json",
      "one_face": true
    },
    {
      "id": "hero-powered",
      "character": "hero",
      "form": "powered",
      "master": "masters/hero-powered.png",
      "master_size": [1280, 720],
      "one_face": true
    }
  ],
  "scenes": [
    {
      "id": "storm-valley",
      "world_plate": "world-plates/storm-valley.png",
      "empty": true
    }
  ],
  "shots": [
    {
      "id": "s01-01",
      "scene": "storm-valley",
      "cast": ["hero-normal"],
      "exact_count": 1,
      "action": "hero stands at frame left and looks toward frame right",
      "change": ["pose", "lighting"],
      "precision": "exact",
      "previous_state": null,
      "output": "shots/s01-01/accepted/final.png",
      "letterbox": false
    }
  ]
}
```

Required top-level fields:

- `project`
- `resolution`: `[width, height]`
- `runtime`: exact Comfy API URL and active process root that the capability probe must verify
- `characters`
- `scenes`
- `shots`

Required shot fields:

- `id`
- `scene`
- `cast`: character-form IDs, not prose names
- `exact_count`
- `action`
- `change`: any of `world`, `background`, `lighting`, `pose`, `expression`, `action`, `wardrobe`, `prop`, `damage`, `transformation`, `spirit`, `remove`, `insert`
- `precision`: `loose`, `identity`, or `exact`
- `output`

Optional shot fields:

- `previous_state`: accepted frame ID for a state chain
- `blocking`: path to pose/layout proxy
- `masks`: map from character-form ID to mask path
- `letterbox`: true only when the source has already been padded rather than cropped
- `notes`

Rules:

- `exact_count` must equal `cast.length` unless `notes` explains tiny silhouettes or non-person layers.
- Every cast ID must resolve to one canonical master.
- Multi-person or `precision=exact` shots route through blocking/masks.
- `previous_state` may reference only an earlier shot state.
- Do not declare `center_crop`; the validator rejects it.

If a master aspect ratio differs from the project output, add a real padded asset to the character record:

```json
{
  "master": "masters/hero-portrait.png",
  "master_size": [768, 1152],
  "letterbox_master": "masters/hero-portrait-letterbox-1280x720.png",
  "letterbox_size": [1280, 720],
  "one_face": true
}
```

The validator rejects a Boolean claim without the actual target-sized letterbox file.

Every canonical master also needs detector/reviewer evidence:

```json
{"master": "masters/hero-normal.png", "sha256": "<actual file sha256>", "face_count": 1, "approved": true}
```

Store it at the character's `master_qc` path. The preflight reads this file and checks that it names the exact master.

## Release QC

`--phase release` requires one QC record per shot:

```json
{
  "shots": {
    "s01-01": {
      "accepted": "shots/s01-01/accepted/final.png",
      "handoff": "ltx-handoff/s01-01.png",
      "gates": {
        "capability": {"pass": true},
        "master": {"pass": true},
        "world": {"pass": true},
        "content": {"pass": true},
        "identity": {"pass": true, "arcface": 0.86},
        "handoff": {"pass": true}
      }
    }
  }
}
```

The source content and identity evidence files must bind their verdict to the exact accepted image:

```json
{"pass": true, "accepted_sha256": "<accepted image sha256>", "reviewer": "agent-id", "contact_sheet": "qc/contact.jpg", "contact_sheet_sha256": "<contact sheet sha256>"}
```

Identity evidence also binds every canonical master:

```json
{"pass": true, "accepted_sha256": "<accepted image sha256>", "arcface": 0.86, "master_sha256": {"hero-normal": "<master sha256>"}}
```

When ArcFace is invalid for a profile, prosthetic creature, transformed face, or spirit, use:

```json
{"pass": true, "metric_applicable": false, "visual_pass": true}
```
