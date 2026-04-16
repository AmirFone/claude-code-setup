# LaTeX Compilation Pipeline

Full procedure for assembling, compiling, enforcing page limits, visually verifying, and delivering the tailored resume PDF.

> **Scope note:** The steps below (Step 1-5) are all sub-steps of `SKILL.md` Phase 4 ("Compile, Validate & Deliver PDF"). When `SKILL.md` refers to Phases 0-4, it means the overall workflow. When this file refers to Steps 1-5, it means the ordered operations inside the compile stage only.

## Step 1: Assemble

1. Take the user's original resume LaTeX source
2. Apply every change from Part 1 (Ready-to-Paste Sections) inline
3. Produce one complete, self-contained `.tex` file --- no placeholders, no `{{}}` tokens
4. Write to disk at a working location (e.g., `/tmp/resume.tex`)

## Step 2: Compile

Run `pdflatex` twice for proper cross-references and hyperlinks:

```bash
cd /tmp && pdflatex -interaction=nonstopmode resume.tex && pdflatex -interaction=nonstopmode resume.tex
```

### Common LaTeX Pitfalls

| Character/Pattern | Problem | Fix |
|-------------------|---------|-----|
| `%`, `&`, `$`, `#`, `_` in text | Interpreted as LaTeX commands | Escape: `\%`, `\&`, `\$`, `\#`, `\_` |
| `—` (Unicode em-dash) | Breaks pdflatex | Use `---` |
| `→` (Unicode arrow) | Breaks pdflatex | Use `$\to$` |
| `~` used for approximation | LaTeX non-breaking space | Use `$\sim$` |
| `'` `'` (smart quotes) | May cause encoding errors | Use `` ` `` and `'` (LaTeX quotes) |
| `…` (Unicode ellipsis) | May break compilation | Use `\ldots` |
| `≥` `≤` | Not standard LaTeX text | Use `$\geq$`, `$\leq$` |
| Missing `\end{}` | Compilation hangs or errors | Verify every `\begin{}` has a matching `\end{}` |
| Unmatched braces | Silent errors or wrong formatting | Count braces in each section |

### If Compilation Fails

1. Read the `.log` file for the error line number
2. Fix the specific LaTeX error
3. Recompile and verify
4. Repeat until clean compilation

## Step 3: Enforce Single Page

Check page count immediately after compilation:

```bash
pdfinfo /tmp/resume.pdf | grep Pages
```

**If more than 1 page, apply fixes from the priority list below.** Do not skip this phase. Do not deliver a multi-page resume.

### Fix Priority (try in order, recompile + recheck after EACH individual fix):

#### Fix 1: Reduce `\titlespacing*` before-spacing

| Parameter | Safe Range | Danger Zone |
|-----------|-----------|-------------|
| Before-spacing | `5pt` down to `-2pt` | Below `-4pt`: section headers collide with content above |
| After-spacing | `3pt` down to `1pt` | Below `0pt`: first bullet merges into header |

```latex
\titlespacing*{\section}{0pt}{-2pt}{1pt}
```

**What breaks if you go too far:** Section title text overlaps with the last bullet of the previous section. The header rule/line (if any) may cut through text.

#### Fix 2: Reduce `\itemsep` in itemize lists

| Parameter | Safe Range | Danger Zone |
|-----------|-----------|-------------|
| `\itemsep` | `2pt` down to `0pt` | Negative values: bullets visually merge into a wall of text |
| `\parsep` | `2pt` down to `0pt` | Negative values: multi-line bullets overlap themselves |
| `\topsep` | `2pt` down to `0pt` | Negative values: first bullet collides with role/title line |

```latex
\setlist[itemize]{nosep, leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt}
```

**What breaks if you go too far:** Bullet text from adjacent items overlaps vertically. Descenders (g, p, y) from one line clip into ascenders (b, d, h) of the next.

#### Fix 3: Reduce margins in `\geometry`

| Parameter | Safe Range | Danger Zone |
|-----------|-----------|-------------|
| Top margin | `0.5in` down to `0.25in` | Below `0.2in`: header/name may clip at page edge, some printers cut it off |
| Bottom margin | `0.5in` down to `0.25in` | Below `0.2in`: last line may not print, PDF viewers may clip |
| Left/right margins | `0.5in` down to `0.4in` | Below `0.35in`: long bullets wrap more, actually *increasing* page length |

```latex
\geometry{top=0.3in, bottom=0.3in, left=0.45in, right=0.45in}
```

**What breaks if you go too far:** Reducing left/right margins causes long bullet lines to consume more horizontal space, but if those lines were already wrapping, tighter margins make them wrap *more* --- paradoxically adding lines. Always recheck page count after margin changes in both directions.

**Critical interaction:** Tighter left/right margins + long bullets can *increase* total page length. If page count goes UP after reducing horizontal margins, revert that change immediately and try a different fix.

#### Fix 4: Condense content (surgical cuts)

Before cutting, identify the least-impactful content:

| Cut Priority (cut first → last) | Rationale |
|----------------------------------|-----------|
| Achievements/Awards section bullets | Often supplementary to experience |
| Oldest role (3+ roles ago) bullets | Least relevant, recruiter focuses on recent 2 |
| Redundant bullets within a role | Two bullets saying similar things --- merge into one |
| Project descriptions | Only if the project doesn't map to a JD requirement |

**Merge technique:** Combine two related bullets into one that preserves both metrics:
```
BEFORE (2 lines):
- Reduced API latency by 40% through query optimization
- Improved database response times by implementing connection pooling

AFTER (1 line):
- Reduced API latency 40% and database response times via query optimization and connection pooling
```

**Never cut:** Quantified impact metrics, keywords that were specifically injected for the JD, the most recent role's bullets.

#### Fix 5: Last resort --- reduce font size

| Size | Effect |
|------|--------|
| `10pt` → `9pt` | Usually sufficient, still readable |
| `9pt` → `8pt` | Tight but acceptable for dense resumes |
| Below `8pt` | **Do not go here.** Unreadable, signals desperation to the reviewer |

Only after all other fixes are exhausted.

### Shrink Loop Protocol

```
REPEAT:
  1. Apply ONE fix (smallest safe change)
  2. Recompile (pdflatex twice)
  3. Check page count
  4. IF 1 page → proceed to Step 4 (Visual QA)
  5. IF still >1 page → apply next fix
  6. IF a fix INCREASED page count → revert it, skip to next fix
UNTIL: 1 page achieved
```

**Never stack multiple fixes before recompiling.** Each change can interact with others in unexpected ways. One change at a time, verify, then decide next step.

## Step 4: Visual QA

**This phase is mandatory after ANY spacing/margin changes.** Shrinking to fit one page frequently introduces visual defects that aren't detectable from the LaTeX source alone.

### Render the PDF

Convert to image for visual inspection:

```bash
pdftoppm -r 200 -png /tmp/resume.pdf /tmp/resume_preview
```

If `pdftoppm` is not available, use Python:

```python
from pdf2image import convert_from_path
images = convert_from_path('/tmp/resume.pdf', dpi=200)
images[0].save('/tmp/resume_preview.png', 'PNG')
```

Then read/view the rendered PNG.

### Visual QA Checklist

Inspect the rendered image for ALL of the following. Check each one explicitly.

#### Overlap & Collision Checks (highest priority after shrinking)

| Check | What To Look For | Common Cause |
|-------|------------------|--------------|
| **Section header collision** | Section title text overlapping with last bullet of previous section | `\titlespacing*` before-spacing too negative |
| **Bullet-to-bullet overlap** | Text from one bullet bleeding into the next vertically | `\itemsep` or `\parsep` at 0 or negative |
| **Header-to-bullet collision** | First bullet of a role crashing into the role title/company line | `\topsep` too small or negative |
| **Descender/ascender clipping** | Letters like g, p, y from one line touching b, d, h of the line below | Line spacing (`\baselineskip`) reduced too aggressively |
| **Margin clipping** | Text or content cut off at page edges | Margins below safe minimums |
| **Rule/line interference** | Horizontal rules or section dividers cutting through text | Rule positioned relative to spacing that was changed |

#### Layout & Balance Checks

| Check | What To Look For |
|-------|------------------|
| **Right-margin overflow** | Any text running past the right edge --- especially long URLs, company names, or date ranges |
| **Date alignment** | All right-aligned dates should line up vertically. Check that date column didn't shift due to margin changes. |
| **Section spacing consistency** | Gaps between sections should be uniform. After shrinking, one section might be tighter than others if `\titlespacing*` was applied unevenly. |
| **Visual balance** | Content should fill the page evenly. Not crammed at top with whitespace at bottom (common when content was cut unevenly). |
| **Orphaned content** | A section header at the very bottom with its content gone --- happens when bullets were cut from the last section |

#### Formatting Integrity Checks

| Check | What To Look For |
|-------|------------------|
| **Bold/italic preservation** | Verify that `\textbf{}` and `\textit{}` still render correctly --- brace mismatches from edits can silently break these |
| **Hyperlink rendering** | `\href{}` links should show as styled text, not raw URLs |
| **Bullet character rendering** | Bullet points should be consistent (all dots, all dashes, etc.), not mixed or missing |
| **Character encoding** | No black boxes, question marks, or garbled text (from Unicode characters that survived escaping) |
| **Font consistency** | No sudden size or weight changes mid-section |

### QA Failure Recovery

If visual inspection reveals problems:

1. **Identify which fix caused the defect** (usually the most recent spacing change)
2. **Revert that specific change** --- go back to the value before the defect appeared
3. **Try a different fix** from the priority list instead
4. **Recompile and re-inspect** --- repeat until the PDF is both single-page AND visually clean

**If single-page and visual cleanliness are in conflict** (can't fit on one page without introducing overlap):
- Prioritize content cuts (Fix 4) over aggressive spacing reduction
- Cutting one weak bullet is always better than making the entire resume look cramped
- Ask the user which content to cut if unsure

**The PDF is not ready to deliver until it passes ALL visual QA checks.** Never skip this phase, even if the page count is correct.

## Step 5: Deliver

1. Name the output PDF: `Firstname_Lastname_Resume_MonthYear.pdf` (e.g., `Jane_Doe_Resume_April2026.pdf`)
   - Extract the name from the resume content
   - Use current month + year as the suffix
   - Do NOT include the company name — recruiters may interpret that as a signal the resume was tailored by a tool
   - Use underscores, no spaces

2. Copy to a user-accessible location:
   ```bash
   cp /tmp/resume.pdf ~/Downloads/Firstname_Lastname_Resume_MonthYear.pdf
   ```

3. Reveal the file in Finder so the user can access it immediately. **Use `open -R` to reveal in Finder, NOT `open` (which launches Preview).** The user wants to see the folder location, not have the PDF pop open in a viewer.
   ```bash
   open -R ~/Downloads/Firstname_Lastname_Resume_MonthYear.pdf
   ```
   **Wrong:** `open ~/Downloads/resume.pdf` — opens the PDF in Preview, not what the user wants.
   **Right:** `open -R ~/Downloads/resume.pdf` — opens Finder to the file's folder with the file selected.

4. Inform the user of the file location and confirm it passed visual QA. Do NOT separately launch Preview or any PDF viewer.

## Troubleshooting

### pdflatex Not Found
Install via Homebrew on macOS:
```bash
brew install --cask mactex-no-gui
```
Or use `tectonic` as a lightweight alternative:
```bash
brew install tectonic
tectonic /tmp/resume.tex
```

### pdfinfo Not Found
Install poppler:
```bash
brew install poppler
```
Alternative page count method:
```python
from pypdf import PdfReader
print(len(PdfReader('/tmp/resume.pdf').pages))
```

### pdftoppm Not Found
Part of poppler (same install as above). Alternative:
```bash
sips -s format png /tmp/resume.pdf --out /tmp/resume_preview.png
```
Note: `sips` may not handle PDF-to-PNG well on all systems. Fall back to Python `pdf2image` if needed.
