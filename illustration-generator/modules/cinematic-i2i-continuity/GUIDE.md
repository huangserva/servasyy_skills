---
name: cinematic-i2i-continuity
description: Plan, execute, and quality-gate multi-stage image pipelines for recurring-character consistency across storyboards, films, MVs, comics, and LTX keyframes. Use when Codex must combine T2I world plates, Krea2 Identity Edit, Krea2 Ostris Edit, Qwen Image Edit, masks/compositing, multi-reference images, identity metrics, and downstream LTX rather than relying on independent prompt-only generations.
---

# Cinematic I2I Continuity

Build a repeatable image-production graph. Do not treat a long sequence as many unrelated prompts.

## Non-Negotiable Rules

1. Use T2I only for empty world plates, style exploration, and the first approved master.
2. Give every recurring character and form one canonical master. Identity comes from pixels, not words such as `same person`.
3. Never use independent T2I for recurring-character final frames.
4. For exact multi-person geometry, place one character per masked pass. Do not ask one prompt to invent the whole cast.
5. Keep the identity master aspect ratio. Letterbox when needed; never center-crop a portrait master into landscape.
6. Keep Krea2 Identity Edit instructions short. Do not follow a successful identity pass with full-denoise whole-person Qwen/inpaint.
7. Reject bad references upstream. LTX may animate a reference; it may not repair its cast, identity, pose, or world.
8. Share the one remote ComfyUI on port `8188`. A local SSH forwarding port is allowed; do not start a second remote ComfyUI.
9. Before switching heavy image models, release cached ComfyUI models only when the shared queue is empty. Every bundled Krea2, Qwen, and Z-Image runner uses the same cross-process submission lock around queue check, unload, and prompt submission; all refuse to unload an active queue. Waiters never auto-delete an old-looking lock. Each runner writes a fingerprinted submission intent before POST, resumes a confirmed `prompt_id`, and refuses duplicate submission when the response outcome is unknown.
10. Split identity into immutable and state-mutable attributes. Face geometry, age, and body proportions stay fixed; an explicitly scripted transformation may change hair color, aura, costume damage, or form. Never repeat an old mutable attribute in a transformation prompt.
11. Treat cast count and contact geometry as structural constraints. After one failed whole-frame retry, stop strengthening prose and route the shot through isolated character layers and deterministic compositing.
12. A final sequence gate must enumerate every still handed to LTX, bind accepted and handoff bytes, bind every canonical master and reviewed contact-sheet cell, and reject undeclared duplicate hashes. Every identity verdict names its reviewer, exact cast/master IDs, labeled cell, comparison method, and reason code. A stress-gate subset never substitutes for the full release ledger.

## Start With Capability Probes

Run the probe before planning around a model:

```bash
python3 scripts/probe_comfy.py \
  --url http://127.0.0.1:8188 \
  --ssh-target newgpu \
  --expected-root /home/admin01/imports/rented_175_155_64_171/ComfyUI_krea2_latest \
  --require krea2-identity \
  --require krea2-ostris \
  --require qwen-edit \
  --require ltx-director
```

For the shared 4090, the probe verifies the live process root through SSH. The equivalent manual check is:

```bash
ssh newgpu 'pid=$(pgrep -f "python.*main.py.*--port 8188" | head -1); readlink -f /proc/$pid/cwd'
```

The expected unified root is:

```text
/home/admin01/imports/rented_175_155_64_171/ComfyUI_krea2_latest
```

Do not infer capability from visible weights. `krea2_turbo_fp8.safetensors` without the Krea2 edit nodes or `CLIPLoader.type=krea2` is not a working edit installation. Do not restart or switch the shared service without coordinating with its other users.

Read [references/krea2-verified-operations.md](references/krea2-verified-operations.md) for exact node, model, LoRA, parameter, and failure rules.

## Build The Run Bundle

Create one bundle per project:

```text
run/
  continuity-manifest.json
  continuity-plan.json
  masters/
  world-plates/
  blocking/
  shots/<shot-id>/candidates/
  shots/<shot-id>/accepted/
  masks/
  qc/identity.json
  qc/content.json
  qc/contact.jpg
  ltx-handoff/
  summary.json
```

Write `continuity-manifest.json` from the shot table. Include every character form, master path, scene plate, exact cast, action, change scope, and previous-state dependency. See [references/manifest-schema.md](references/manifest-schema.md).

Generate the routing plan:

```bash
python3 scripts/plan_continuity.py \
  continuity-manifest.json \
  --out continuity-plan.json
```

Validate it before generation:

```bash
python3 scripts/validate_continuity_bundle.py \
  continuity-manifest.json continuity-plan.json \
  --project-root . \
  --out qc/preflight.json
```

After images have been accepted, run the non-bypassable release gate:

```bash
python3 scripts/record_qc.py continuity-manifest.json \
  --plan continuity-plan.json --project-root . --shot s01-01 \
  --accepted shots/s01-01/accepted/final.png \
  --handoff ltx-handoff/s01-01.png \
  --capability-report qc/capability.json \
  --content-evidence qc/s01-01-content.json \
  --identity-evidence qc/s01-01-identity.json \
  --out qc/gates.json

python3 scripts/validate_continuity_bundle.py \
  continuity-manifest.json continuity-plan.json \
  --project-root . --phase release --qc qc/gates.json \
  --out qc/release.json
```

Release validation reads actual QC results, accepted files, dimensions, identity evidence, and LTX handoff files. A list of gate names alone never releases a frame.

For long-form delivery, build one ledger record for every released state and validate it as a second, sequence-level gate:

```bash
python3 scripts/validate_release_ledger.py qc/release-ledger.json \
  --project-root . --out qc/release-ledger-result.json
```

Every repeated image hash after the first must declare `hold_of` and a concrete `hold_reason`. Use holds only for an intentional locked composition or match hold whose performance develops inside LTX; never use them to conceal a missing story state.

## Route Each Shot

Use the earliest controllable route that satisfies the shot:

| Need | Route |
| --- | --- |
| Empty location or world design | Z-Image/Krea2 T2I world plate |
| Same one person, new nearby scene/light | Krea2 Identity Edit |
| Wardrobe or semantic object change | Krea2 Ostris Edit, then identity QC |
| Pose, action, expression, or multi-reference change | Qwen Image Edit |
| Exact count, overlap, left/right position, spirit/body separation | Blocking composite + per-character mask/edit |
| Several states in one shot | First accepted state + canonical masters + bridge edits |
| Video motion | Accepted frames only -> LTX Director multi-reference |

Read [references/routing-and-gates.md](references/routing-and-gates.md) before routing action scenes, transformations, ensembles, or VFX layers.

## Execute In Layers

1. **World plate:** Generate or approve the empty environment. Remove all unplanned people before adding cast.
2. **Blocking:** Make a crude but exact composition proxy for cast count, scale, pose, screen direction, and occlusion.
3. **Identity passes:** Insert or restage one character at a time from the canonical master. Use a tight character mask.
4. **Local semantic passes:** Change clothing, props, damage, expression, or aura without rewriting unrelated pixels.
5. **Harmonization:** Relight edges and contact shadows at low change strength. Never use full-denoise over accepted faces.
6. **State chain:** Derive later states from the first accepted state plus the same masters. Use bridge states for large motion.

For a colored VFX insert generated by a whole-frame edit, extract only the changed effect color and composite it over the frozen accepted frame:

```bash
python3 scripts/extract_color_delta_mask.py \
  --base shots/s01/accepted/base.png \
  --layer shots/s01/candidates/spirit-pass.png \
  --include-mask masks/spirit-region.png \
  --output masks/spirit-matte.png

python3 scripts/composite_with_mask.py \
  --base shots/s01/accepted/base.png \
  --layer shots/s01/candidates/spirit-pass.png \
  --mask masks/spirit-matte.png \
  --output shots/s01/candidates/spirit-composite.png
```

This route is for separable colored effects such as a golden spirit or aura. Review the matte before acceptance; do not use it for ordinary wardrobe, skin, or identity changes.

For a semantic overlay whose mask is already approved, extract only that region as reusable RGBA:

```bash
python3 scripts/extract_masked_rgba.py \
  --image shots/s01/candidates/spirit-pass.png \
  --mask masks/spirit-region.png \
  --padding 16 \
  --output shots/s01/candidates/spirit-rgba.png
```

Use this for a spirit, isolated actor, prop, or effect layer. The mask, not the source image boundary, defines what survives.

For a single-person Krea2 pass, use:

```bash
node scripts/run_krea2_edit.mjs \
  --mode identity \
  --api http://127.0.0.1:8188 \
  --source masters/hero.png \
  --output shots/s01/candidates/identity-01.png \
  --prompt "rainy city alley, eye-level medium shot, practical amber light" \
  --width 1280 --height 720 --seed 42
```

The runner refuses aspect-ratio mismatch for identity mode. Prepare a letterboxed master first instead of bypassing the gate.

For a scripted transformation, pass only the allowed deltas through `--mutable`, for example `--mutable "hair color and style, eye color, aura, costume damage"`. The adapter still locks face geometry, age, skin identity, and body proportions. Do not use `--mutable` for ordinary continuity shots.

Use `scripts/run_qwen_edit.mjs` for Qwen multi-reference edits, `scripts/run_zimage_t2i.mjs` for empty world plates, and `scripts/composite_with_mask.py` for deterministic full-canvas layer/mask assembly. The planner records the adapter for every stage.

Use `scripts/run_krea2_t2i.mjs` only to establish a missing canonical master or a one-off neutral action plate. Do not use independent Krea T2I outputs as recurring-character shots; approve one master, then route every story frame through I2I.

`run_qwen_edit.mjs` accepts `--negative` for an actual negative-conditioning branch and `--denoise` for change scope. Use an explicit zero-cast negative list for empty worlds. For adjacent performance states, lower denoise before lengthening prompts; otherwise Qwen may preserve the cast while redesigning the entire world.

When a fight requires a precise contact point, generate one isolated full-body action plate per recurring character, remove only its neutral background, and place the resulting RGBA cutouts with `scripts/composite_cutouts.py`. The JSON layout fixes layer order, `x`, `y`, character height, mirroring, rotation, and contact shadows. Use this before a low-change harmonization pass; never ask the harmonizer to redesign the pose.

Use that deterministic route immediately for three or more readable characters, rear body locks, stacked depth, teleport contact, opposing beams, or any beat where a duplicate person changes the story. Generate the identity/action layers with Krea2 or Qwen, but let the compositor own exact count, position, occlusion, world plate, and VFX. Review scale, shadow, and screen direction before acceptance. A famous-character prompt that falls back to animation is rejected; regenerate the live-action master with neutral role and costume descriptions, then continue through I2I.

## Gate Before Scaling

Run a four-case stress gate before generating a long sequence:

1. Empty world with zero people.
2. One recurring person across a transformation or major relight.
3. Two recurring opponents in exact action geometry.
4. Layered VFX shot such as physical person plus translucent spirit.

Do not scale if any case fails. Convert each failure into a route, mask, prompt, or validation rule and rerun from the earliest failed stage.

Every accepted still must pass:

- exact cast count and identities;
- face/form/outfit continuity;
- planned camera, blocking, action, and screen direction;
- correct world plate and props;
- no duplicate body, bystander, text, collage, or accidental layer;
- aspect ratio and LTX target dimensions;
- ArcFace-to-master `>= 0.80` where a frontal face is measurable; prefer `>= 0.85` for hero close-ups.

ArcFace is evidence, not the only gate. Side faces, prosthetic creatures, transformed hair, and spirit layers still require visual review.

## Hand Off To LTX

Only copy passing frames into the final LTX handoff directory. Build Director packs from that release directory, never from candidate or legacy keyframe paths. Keep identity masters out of the LTX timeline unless they are also composition-approved keyframes. Use the `ltx-director-multiref-video` skill for timeline assembly, rendering, and observed-action QC.

For an existing render whose historic remote path name predates the final handoff directory, release only after a provenance report proves that every historic source file, accepted frame, and current handoff file has the same SHA-256. The report must also bind the remote history/prompt ID, current reproduction pack, repair route, and final raw-shot hash. A matching filename or visual resemblance is not evidence.

Before final assembly, create dense motion evidence that includes every rendered frame (thumbnail sheets are acceptable), binds each sheet to the exact shot-video hash, and records a reviewer verdict for cast, identity/style continuity, transitions, and tail frames. First/middle/last sampling alone is not a release gate.

Renderer resume data must include an input fingerprint, output SHA-256 and successful media probe. Never skip from file size alone. Persist the remote `prompt_id` before polling, resume that receipt after interruption, enforce a deadline, and download to a temporary file followed by an atomic rename. Do not blindly submit a second remote job after a post-submit timeout.

Route motion by what the model must solve:

- Use standard LTX Director multi-reference for continuous state changes, restrained performance, transformation, atmosphere, and VFX-layer continuity.
- A transformation is continuous only when the same physical identity can interpolate cleanly. If a validated test produces a duplicate during a major form, age, costume, or silhouette break, render each form as a separate same-form shot and cut on a motivated flash, occlusion, whip, or impact. Never release a cross-form interpolation with overlapping bodies.
- Treat cast-count changes, object-to-face reveals, and close-detail endings the same way after one failed interpolation: render restrained camera motion from each released state and join them with a motivated cut. Do not reuse any interval from the failed LTX render, because duplicate bodies and form reversions can survive inside an apparently clean trim.
- A deterministic state-camera route must declare every released keyframe hash as its source. Any earlier LTX history is reference-lineage evidence only, never the claimed source video for the corrected shot.
- Use MotionBrush/ICLoRA only for short, explicit screen-space displacement. On the verified workflow, render it at `1280x768` so both latent dimensions are even, then crop 16 pixels from the top and bottom for a `1280x736` master.
- Do not ask one long generation to invent approach, exact contact, impact reaction, and separation. For fast combat, cut the beat into roughly `0.5-1.5s` approach, `0.1-0.3s` contact, and `0.5-1.5s` reaction/separation shots. Anchor contact with the accepted deterministic still, cut on impact, and use flash, shake, dust, and sound design to bridge the cuts.
- If a six-second action test preserves identity but reads as sliding or posing, treat the route as failed for choreography even when cast-count QC passes. Shorten and recut; do not keep raising motion strength.
- Switching between MotionBrush/ICLoRA and standard Director requires an empty shared queue followed by model unload/reload. Reuse loaded models only between packs of the same workflow family.

Write `summary.json` with:

- route used per frame;
- source master and world plate;
- all prompts, masks, seeds, models, LoRAs, and strengths;
- identity/content gate results;
- rejected candidates and reasons;
- exact frames released to LTX.

## Stop Conditions

Stop and repair upstream when:

- a required Comfy node or model probe fails;
- a master has multiple faces or is center-cropped;
- the world plate already contains unintended cast;
- an edit changes identity while fixing pose;
- a multi-person pass duplicates or merges characters;
- a later state is derived from a rejected frame;
- LTX input frames disagree on identity, material style, or shot geography.
