# Routing And Gates

## Contents

- Control hierarchy
- Route selection
- Multi-person construction
- State continuity
- QC gates
- Long-sequence stress test

## Control Hierarchy

Use controls in this order:

1. Pixels: approved masters and world plates.
2. Masks/layout: exact cast geometry and protected regions.
3. Reference images: pose, costume, prop, or material examples.
4. Text: requested delta and atmosphere.
5. Seed: reproducibility only; never call it an identity lock.

## Route Selection

### World Plate

Generate an empty plate with T2I. State zero people positively and remove people before cast insertion. Do not ask the same pass to build the world and recurring cast.

### One-Person Restage

Use Krea2 Identity Edit when:

- one canonical master exists;
- face/outfit must remain the same;
- the new scene is a moderate jump;
- master and output aspect ratios match.

Use Qwen Edit when the dominant change is pose, expression, action, or precise local geometry. Include the canonical master as a separate reference when the workflow supports it.

### Wardrobe Or Prop Change

Use Krea2 Ostris or Qwen Edit on a masked region. Protect face, hair, hands, and background unless the request explicitly changes them. Re-run identity QC; do not blindly add an identity restage after a good local edit.

### Multi-Person Shot

Build in layers:

```text
empty world plate
  -> exact blocking proxy
  -> character A masked pass from master A
  -> character B masked pass from master B
  -> character C masked pass from master C
  -> low-strength edge/light harmonization
```

Freeze accepted characters while adding the next. Keep a clean plate and every intermediate layer so a failed later character does not force a full rerun.

Each character pass is two operations: generate a full-canvas candidate with Qwen plus that character's master, then copy only the approved character mask back onto the frozen previous canvas. The Qwen adapter does not consume masks itself; `composite_with_mask.py` is the protection boundary.

### Action Shot

Use a pose/layout proxy with clear left/right axis, body scale, contact point, and negative space. A text phrase such as `Goku punches Cell` is not sufficient geometry.

For contact frames, explicitly mark:

- which limb belongs to whom;
- exact contact point;
- full-body or crop requirement;
- screen direction;
- required separation before and after impact.

### Transformation

Treat the physical actor as fixed and edit only transformation layers: hair form/color, eyes, costume damage, aura, light, and debris. Use the pre-transformation accepted frame plus the canonical master. Do not generate the transformed person from T2I.

### Spirit Or Hologram

Create the physical actor and spirit as separate layers. The spirit needs its own mask, opacity/material rule, and spatial relationship. A prompt-only two-person generation cannot reliably distinguish physical and translucent bodies.

## State Continuity

For states `A -> B -> C` inside one shot:

- Approve A first.
- Build B from A plus canonical masters and a delta-only instruction.
- Build C from the nearest accepted state plus the same masters.
- Add a bridge frame when body geometry changes sharply.
- Never propagate from a rejected state.
- Keep the world plate fixed unless the camera intentionally moves.

## QC Gates

### Capability Gate

Nodes, CLIP type, weights, LoRAs, shared port, queue, and active build pass.

### Master Gate

One face, correct form, sufficient resolution, correct aspect ratio, no crop damage, approved wardrobe.

### World Gate

Correct location, no unplanned people, correct time/weather, usable negative space and camera axis.

### Content Gate

Exact cast count, identities, roles, action, props, left/right direction, visibility, and causal beat.

### Identity Gate

Visual continuity plus ArcFace where measurable. Default thresholds:

```text
usable >= 0.80
hero close-up preferred >= 0.85
```

Do not use ArcFace alone for profile faces, transformed hair, masks, prosthetic creatures, or translucent spirits.

### Handoff Gate

Dimensions normalized, no rejected files, prompts/seeds/models recorded, adjacent keyframes compatible, and LTX timeline uses only accepted images.

## Long-Sequence Stress Test

Before scaling, prove four cases:

1. `zero-cast`: an empty world remains empty.
2. `one-identity`: one person survives a scene/light/form change.
3. `two-action`: two masters remain distinct in exact contact geometry.
4. `layered-vfx`: physical and non-physical character layers remain semantically separate.

The test passes only when all four survive both still-image QC and a short LTX motion gate.

For `two-action`, passing identity and cast count is insufficient. The observed video must show readable approach, a real limb-to-target contact frame, an opponent reaction, and separation. If a continuous generation turns the beat into lateral sliding, rebuild it as short shots around the accepted contact still and cut on impact. MotionBrush/ICLoRA controls displacement; the deterministic still controls exact contact geometry.
