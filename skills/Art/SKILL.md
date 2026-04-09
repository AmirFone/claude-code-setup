---
name: Art
description: Visual content generation, photo editing, and image enhancement. USE WHEN user wants diagrams, visualizations, comics, editorial illustrations, photo enhancement, star enhancement, image upscaling, or batch photo processing.
---

# Art Skill

Image generation and photo editing system. Supports Excalidraw hand-drawn aesthetic for original content, and photorealistic editing for existing photographs.

## Output Location

```
ALL GENERATED IMAGES GO TO ~/Downloads/ FIRST
Preview in Finder/Preview before final placement
Only copy to project directories after review
```

## Workflow Routing

Route to the appropriate workflow based on the request:

  - Technical or architecture diagram → `Workflows/TechnicalDiagrams.md`
  - Blog header or editorial illustration → `Workflows/Essay.md`
  - Comic or sequential panels → `Workflows/Comics.md`
  - Photo editing, enhancement, upscaling, batch processing → `Workflows/PhotoEditing.md`

---

## Models

| Model ID | CLI Flag | Backend | Best For |
|----------|----------|---------|----------|
| `gemini-3-pro-image-preview` | `--model nano-banana-pro` | Google Gemini API | Highest quality generation & editing |
| `gemini-3.1-flash-image-preview` | `--model nano-banana` (via Replicate) | Replicate | Fast drafts, iteration |
| `flux-1.1-pro` | `--model flux` | Replicate | Alternative aesthetic |
| `gpt-image-1` | `--model gpt-image-1` | OpenAI | OpenAI-style generation |

**Default:** `nano-banana-pro` for all production work.

### Capabilities by Model

| Capability | nano-banana-pro | nano-banana | flux | gpt-image-1 |
|-----------|----------------|-------------|------|-------------|
| Text-to-image | Yes | Yes | Yes | Yes |
| Image editing (reference) | Yes (up to 14 refs) | No | No | No |
| Photo enhancement | Yes | No | No | No |
| Max resolution | 4K (~5500px) | Aspect-based | Aspect-based | 1536px |
| Aspect ratio control | Yes | Yes | Yes | Fixed sizes |

### Size Options

| Model Type | Sizes | Notes |
|-----------|-------|-------|
| Gemini (nano-banana-pro) | `1K`, `2K`, `4K` | Also supports `--aspect-ratio` |
| Replicate (flux, nano-banana) | `1:1`, `16:9`, `3:2`, `4:3`, etc. | Aspect ratio = size |
| OpenAI (gpt-image-1) | `1024x1024`, `1536x1024`, `1024x1536` | Fixed pixel sizes |

### API Keys

| Model | Environment Variable | Loaded From |
|-------|---------------------|-------------|
| nano-banana-pro | `GOOGLE_API_KEY` | `$PAI_DIR/.env` or `~/.claude/.env` |
| flux, nano-banana | `REPLICATE_API_TOKEN` | Same |
| gpt-image-1 | `OPENAI_API_KEY` | Same |
| Background removal | `REMOVEBG_API_KEY` | Same |

---

## Core Aesthetic (for Generated Content)

**Excalidraw Hand-Drawn** - Clean, approachable technical illustrations with:
- Slightly wobbly hand-drawn lines (NOT perfect vectors)
- Simple shapes with organic imperfections
- Consistent hand-lettered typography style
- Dark mode backgrounds with bright accents

**Full aesthetic documentation:** `$PAI_DIR/skills/Art/Aesthetic.md`

---

## Color System

| Color | Hex | Usage |
|-------|-----|-------|
| Background | `#0a0a0f` | Primary dark background |
| PAI Blue | `#4a90d9` | Key elements, primary accents |
| Electric Cyan | `#22d3ee` | Flows, connections, secondary |
| Accent Purple | `#8b5cf6` | Highlights, callouts (10-15%) |
| Text White | `#e5e7eb` | Primary text, labels |
| Surface | `#1a1a2e` | Cards, panels |
| Line Work | `#94a3b8` | Hand-drawn borders |

---

## Quick Reference Commands

**Generate new image:**
```bash
bun run $PAI_DIR/skills/Art/Tools/Generate.ts \
  --model nano-banana-pro \
  --prompt "[PROMPT]" \
  --size 2K \
  --aspect-ratio 16:9 \
  --output ~/Downloads/output.png
```

**Edit/enhance existing photo:**
```bash
bun run $PAI_DIR/skills/Art/Tools/Generate.ts \
  --model nano-banana-pro \
  --prompt "[EDITING INSTRUCTIONS]" \
  --reference-image /path/to/photo.jpg \
  --size 4K \
  --aspect-ratio 3:2 \
  --output ~/Downloads/enhanced.png
```

**Multi-reference (character/style consistency):**
```bash
bun run $PAI_DIR/skills/Art/Tools/Generate.ts \
  --model nano-banana-pro \
  --prompt "[PROMPT referencing the people/objects in images]" \
  --reference-image face1.jpg --reference-image face2.jpg \
  --size 2K \
  --aspect-ratio 16:9 \
  --output ~/Downloads/output.png
```

**With style references (ALWAYS pass visual references as images, never just describe them):**
```bash
bun run $PAI_DIR/skills/Art/Tools/Generate.ts \
  --model nano-banana-pro \
  --prompt "[PROMPT specifying which image is source vs style reference]" \
  --reference-image /path/to/source-photo.jpg \
  --reference-image /path/to/style-reference.jpg \
  --size 4K \
  --aspect-ratio 2:3 \
  --output ~/Downloads/output.png
```

**API keys in:** `$PAI_DIR/.env` (single source of truth for all authentication)

---

## Examples

**Example 1: Technical diagram**
```
User: "create a diagram showing the auth flow"
→ Invokes TECHNICALDIAGRAMS workflow
→ Creates Excalidraw-style architecture visual
→ Outputs PNG with dark background, blue accents
```

**Example 2: Blog header**
```
User: "create a header for my post about AI agents"
→ Invokes ESSAY workflow
→ Generates hand-drawn illustration
→ Saves to ~/Downloads/ for preview
```

**Example 3: Comic strip**
```
User: "create a comic showing the before/after of using AI"
→ Invokes COMICS workflow
→ Creates 3-4 panel sequential narrative
→ Editorial style, not cartoonish
```

**Example 4: Photo enhancement**
```
User: "enhance the stars in my night sky photos"
→ Invokes PHOTOEDITING workflow
→ Downscales originals for API input
→ Passes each as reference-image with enhancement prompt
→ Outputs 4K PNGs preserving photorealism
```

**Example 5: Batch photo editing**
```
User: "make these landscape photos more vibrant"
→ Invokes PHOTOEDITING workflow
→ Groups by aspect ratio (3:2, 16:9, 4:3)
→ Processes each batch with matched aspect ratio
→ Saves enhanced versions to subfolder
```
