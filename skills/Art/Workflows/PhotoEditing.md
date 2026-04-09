# Photo Editing & Enhancement Workflow

**Enhance, upscale, and edit real photographs using Gemini image models.**

---

## Purpose

Edit existing photographs — enhance details, boost specific elements, adjust atmosphere — while preserving the photorealistic look of the original.

**Use for:** Star/sky enhancement, color grading, detail sharpening, atmosphere adjustment, batch photo processing, astrophotography enhancement, landscape enhancement.

---

## How It Works

Pass the original photo as a `--reference-image` with an editing prompt. The model sees the image and applies the requested edits while preserving composition, colors, and realism.

This is **not** generation — it's guided editing. The output should look like a better version of the same photograph, not a new image.

### Style References (CRITICAL)

**If the user provides ANY visual references** (URLs, images, screenshots, posters, examples of the look they want), **ALWAYS pass them as additional `--reference-image` arguments** alongside the source photo. The model needs to SEE the reference to match the style — describing it in the prompt alone is not enough.

```bash
# CORRECT: Pass style references as reference images
bun run Generate.ts \
  --model nano-banana-pro \
  --prompt "Apply the vintage title style from the reference poster onto this photo..." \
  --reference-image /path/to/source-photo.jpg \
  --reference-image /path/to/style-reference-1.jpg \
  --reference-image /path/to/style-reference-2.jpg \
  --size 4K --aspect-ratio 2:3 --output output.png

# WRONG: Only describing the reference in the prompt
--prompt "Make it look like a 1950s movie poster..."  # Model has never SEEN the poster!
```

When downloading reference images from URLs, save them locally first (via WebFetch or curl), then pass the local file as `--reference-image`. Specify in the prompt which image is the source photo and which are style references.

---

## Key Constraints

| Constraint | Detail |
|-----------|--------|
| Max output resolution | 4K (~3840-5504px depending on aspect ratio) |
| Input size limit | Downscale to ~2000px before sending (API rejects large files) |
| Aspect ratios | Must match original: 3:2, 4:3, 16:9, etc. |
| Reference images | Up to 14 total per request |
| Model | `nano-banana-pro` (best quality for photo editing) |

---

## Workflow Steps

### Step 1: Assess the Photos

```bash
# Check dimensions and file sizes
for f in /path/to/photos/*.jpg; do
  sips -g pixelWidth -g pixelHeight "$f"
done
```

Map each photo to the closest supported aspect ratio:

| Original Ratio | Closest Match |
|---------------|---------------|
| 1.50 (6000x4000) | 3:2 |
| 1.77 (6000x3376) | 16:9 |
| 1.33 (6224x4672) | 4:3 |
| 1.00 | 1:1 |
| 0.67 | 2:3 |

### Step 2: Downscale for API Input

Originals are typically 6000+ px and 10-30MB — too large for the API.

```bash
mkdir -p /tmp/edit-input
for f in /path/to/photos/*.jpg; do
  sips -Z 2000 "$f" --out "/tmp/edit-input/$(basename "$f")"
done
```

### Step 3: Craft the Editing Prompt

The prompt is critical. It must:
1. Explicitly state what to enhance
2. Explicitly state what to preserve
3. Emphasize photorealism

**Prompt structure:**
```
Edit this photograph to [SPECIFIC ENHANCEMENT].
[DETAILED INSTRUCTIONS for what to change].
Keep [EVERYTHING ELSE] completely unchanged and photorealistic.
This is a real photograph — do NOT [LIST FORBIDDEN ARTIFACTS].
The result should look like [QUALITY TARGET].
```

### Prompt Examples

**Astrophotography — Star Enhancement:**
```
Edit this photograph to subtly enhance the visibility of stars in the night sky.
Increase star brightness and clarity slightly, reveal fainter stars that are
barely visible, and gently boost the contrast between stars and the dark sky.
Keep the overall scene, colors, landscape, and atmosphere completely unchanged
and photorealistic. This is a real photograph — do NOT add artificial elements,
nebula colors, or make it look AI-generated. The result should look like a
professional long-exposure astrophotograph with excellent star detail.
```

**Landscape — Golden Hour Enhancement:**
```
Edit this photograph to enhance the golden hour warmth. Slightly boost the warm
tones in the highlights and sky, deepen shadow contrast, and bring out texture
in the foreground. Keep the composition, subjects, and overall atmosphere
unchanged. This is a real photograph — do NOT add lens flares, artificial sun
rays, or saturate colors unnaturally. The result should look like a professionally
color-graded landscape photograph.
```

**Portrait — Skin and Light Enhancement:**
```
Edit this photograph to subtly enhance skin tones and directional lighting.
Soften harsh shadows slightly, bring out catchlights in the eyes, and improve
skin texture clarity. Keep the subject's features, expression, background, and
clothing completely unchanged. Do NOT smooth skin artificially or alter facial
features. The result should look like a retouched editorial portrait.
```

### Step 4: Execute

**Single image:**
```bash
bun run $PAI_DIR/skills/Art/Tools/Generate.ts \
  --model nano-banana-pro \
  --prompt "[EDITING PROMPT]" \
  --reference-image /tmp/edit-input/photo.jpg \
  --size 4K \
  --aspect-ratio 3:2 \
  --output ~/Downloads/photo_enhanced.png
```

**Batch processing:**
```bash
OUTPUT="/path/to/output"
INPUT="/tmp/edit-input"
PROMPT="[YOUR EDITING PROMPT]"

for f in "$INPUT"/*.jpg; do
  base=$(basename "$f" .jpg)
  # Determine aspect ratio per file (see Step 1)
  bun run $PAI_DIR/skills/Art/Tools/Generate.ts \
    --model nano-banana-pro \
    --prompt "$PROMPT" \
    --reference-image "$f" \
    --size 4K \
    --aspect-ratio [RATIO] \
    --output "$OUTPUT/${base}_enhanced.png"
done
```

**Batch with mixed aspect ratios** — group files by ratio and loop each group separately (see Star Enhancement example below).

### Step 5: Verify

```bash
# Check all outputs exist and have expected dimensions
for f in /path/to/output/*.png; do
  sips -g pixelWidth -g pixelHeight "$f"
done
```

Preview a few samples before delivering. Downscale for quick visual check:
```bash
sips -Z 1500 output.png --out /tmp/preview.png
```

---

## Validation

### Must Have
- [ ] Original composition preserved
- [ ] Requested enhancement visible
- [ ] Photorealistic — indistinguishable from a real edited photo
- [ ] Correct aspect ratio matching original
- [ ] High resolution output (4K+)

### Must NOT Have
- [ ] AI-generated artifacts (smooth plastic textures, impossible lighting)
- [ ] Added elements not in the original (extra objects, fake nebulae, lens flares)
- [ ] Color shifts in areas that should be unchanged
- [ ] Loss of fine detail in non-enhanced areas
- [ ] Overly processed / HDR look

### If Validation Fails

| Problem | Fix |
|---------|-----|
| Too much change, looks AI | Add "subtle", "slight", "gentle" to prompt; emphasize preservation |
| Not enough enhancement | Remove hedging words; be more specific about what to boost |
| Wrong colors / atmosphere | Add "keep colors unchanged" explicitly |
| Artifacts in landscape/foreground | Add "keep landscape/foreground completely unchanged" |
| Resolution too low | Ensure `--size 4K` is set |

---

## Complete Example: Astrophotography Batch

```bash
GENERATE="$PAI_DIR/skills/Art/Tools/Generate.ts"
OUTPUT="/path/to/Enhanced"
INPUT="/tmp/star-enhance-input"
PROMPT="Edit this photograph to subtly enhance the visibility of stars..."

mkdir -p "$OUTPUT"

# Downscale originals
for f in /path/to/originals/*.jpg; do
  sips -Z 2000 "$f" --out "$INPUT/$(basename "$f")"
done

# Group by aspect ratio and process
# 3:2 photos
for f in photo1.jpg photo2.jpg; do
  base=$(basename "$f" .jpg)
  bun run "$GENERATE" --model nano-banana-pro --prompt "$PROMPT" \
    --reference-image "$INPUT/$f" --size 4K --aspect-ratio 3:2 \
    --output "$OUTPUT/${base}_enhanced.png"
done

# 16:9 photos
for f in photo3.jpg photo4.jpg; do
  base=$(basename "$f" .jpg)
  bun run "$GENERATE" --model nano-banana-pro --prompt "$PROMPT" \
    --reference-image "$INPUT/$f" --size 4K --aspect-ratio 16:9 \
    --output "$OUTPUT/${base}_enhanced.png"
done

# 4:3 photos
for f in photo5.jpg photo6.jpg; do
  base=$(basename "$f" .jpg)
  bun run "$GENERATE" --model nano-banana-pro --prompt "$PROMPT" \
    --reference-image "$INPUT/$f" --size 4K --aspect-ratio 4:3 \
    --output "$OUTPUT/${base}_enhanced.png"
done
```

---

**The workflow: Assess -> Downscale -> Prompt -> Execute -> Verify**
