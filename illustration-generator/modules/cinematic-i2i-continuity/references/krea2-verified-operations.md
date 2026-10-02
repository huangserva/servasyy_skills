# Krea2 Verified Operations

## Contents

- Shared 8188 preflight
- Identity Edit route
- Ostris Edit route
- Measured failure modes
- Model and LoRA inventory
- Prompt rules

## Shared 8188 Preflight

The shared 4090 uses one remote ComfyUI port: `8188`. A capability is usable only when the active process has all required nodes and options.

Expected unified build:

```text
/home/admin01/imports/rented_175_155_64_171/ComfyUI_krea2_latest
```

Required checks for Krea2:

- `CLIPLoader.type` includes `krea2`.
- Identity route nodes: `Krea2EditModelPatch`, `Krea2EditGroundedEncode`.
- General edit route nodes: `Krea2OstrisEditModelPatch`, `TextEncodeKrea2OstrisEdit`.
- UNET: `krea2_turbo_fp8.safetensors` or the scaled variant.
- CLIP: `qwen3vl_4b_fp8_scaled.safetensors` or verified BF16 equivalent.
- VAE: `qwen_image_vae.safetensors`.
- LoRA required by the selected route exists.

Weights visible in `UNETLoader` do not prove the custom node loaded. Probe `/object_info` every time the shared build may have changed.

If the probe fails, do not submit a fake Krea workflow. Coordinate a switch to the unified root; do not launch port 8190.

## Identity Edit Route

Use for one recurring person restaged into a nearby scene while preserving face, hair, proportions, and clothing.

Verified chain:

```text
UNETLoader
  -> LoraLoaderModelOnly(krea2_identity_edit_v1)
  -> Krea2EditModelPatch(source_latent)
CLIPLoader(type=krea2)
  -> Krea2EditGroundedEncode(image, short prompt)
  -> KSampler
  -> VAEDecode
```

Verified defaults:

```text
steps=8
cfg=1
sampler=euler
scheduler=simple
lora=krea2_identity_edit_v1.safetensors
lora_strength=1.0
grounding_px>=1024
output aspect ratio == master aspect ratio
```

Measured results from the local identity-lock kit:

- Portrait master -> portrait study: ArcFace `0.904`.
- Portrait master -> portrait lobby: ArcFace `0.808`.
- Landscape master -> landscape studio: ArcFace `0.811`.
- Landscape master -> distant neon Tokyo jump: ArcFace `0.737`, fail.

Interpretation: same-AR, one-face masters and moderate scene changes work. Large world jumps need intermediate restaging.

## Ostris Edit Route

Use for general semantic edits such as wardrobe, object, or localized appearance changes. Do not treat it as the primary identity-lock route.

Verified chain:

```text
UNETLoader(krea2_turbo_fp8)
  -> Krea2OstrisEditModelPatch
  -> LoraLoaderModelOnly(krea2_lora-edit-step00005310)
CLIPLoader(type=krea2)
  -> TextEncodeKrea2OstrisEdit(image1[, image2, image3])
  -> FluxKontextMultiReferenceLatentMethod(index_timestep_zero)
  -> KSampler
  -> VAEDecode
```

Known working general-edit defaults:

```text
steps=10
cfg=1
sampler=euler
scheduler=simple
edit LoRA strength=0.8 initially
```

Treat strengths above `1.0` as stress tests, not continuity defaults. Higher strength may increase the requested semantic change while also changing pose, face, body, or framing.

## Measured Failure Modes

1. **Portrait center-cropped to landscape:** removes identity evidence; use letterbox.
2. **Master contains multiple faces:** ArcFace and edit attention become ambiguous; approve a one-face master.
3. **Long prompt essay:** the model spends capacity on camera, props, wardrobe, and grade instead of identity.
4. **Large scene jump:** identity drops; use an intermediate neutral restage.
5. **Full-denoise Qwen after Krea identity success:** rewrites the person and destroys the measured gain.
6. **Different Krea edit node/LoRA family:** Ostris general edit is not equivalent to the identity-trained path.
7. **Wrong aspect ratio hidden by crop:** the output may look composed but no longer represents the master.
8. **Multi-person all-at-once edit:** faces merge, duplicate, or swap; use one masked character pass at a time.

## Model And LoRA Inventory

The shared model store has included:

```text
krea2_turbo_fp8.safetensors
krea2_turbo_fp8_scaled.safetensors
qwen3vl_4b_bf16.safetensors
qwen3vl_4b_fp8_scaled.safetensors
qwen_image_vae.safetensors
krea2_identity_edit_v1.safetensors
krea2_lora-edit-step00005310.safetensors
```

Other LoRAs may be present. Presence is not a recommendation. Record every LoRA and strength in the run bundle and compare against a no-LoRA control when its effect is uncertain.

## Prompt Rules

Identity prompt:

```text
Create a photorealistic photo of this person in: <short scene>.
Keep the same person face, hair, body proportions, and clothing exactly.
Relight the person to match the environment.
```

Do not repeat facial anatomy in prose when the master already supplies it. Use text for the requested change; use images and masks for what must remain fixed.
