# Unicode Characters and Font Encoding (pdfLaTeX)

Reference for diagnosing and fixing two related build failures under
**pdfLaTeX**: non-ASCII characters that are "not set up", and monospace/code
text that silently renders in the wrong (proportional roman) font.

Both bite hardest in literate programs, where source bytes — test fixtures,
Unicode normalization tables, ASCII-art diagrams — are woven *verbatim* into
the `.tex` and must then be typeset by the engine.  See the
`literate-programming` skill for the weaving angle.

Search patterns: `DeclareUnicodeCharacter`, `fontenc`, `pdffonts`,
`Unicode character`, `not set up`, `beramono`, `T1`.

---

## Symptom 1: "Unicode character … not set up for use with LaTeX"

```
! LaTeX Error: Unicode character ┌ (U+250C) not set up for use with LaTeX.
! LaTeX Error: Unicode character ‛ (U+201B) not set up for use with LaTeX.
```

**Cause.** pdfLaTeX (with the LaTeX kernel's UTF-8 support) only typesets code
points that have a `\DeclareUnicodeCharacter` mapping.  Common Latin
accents, en/em dashes, and curly quotes are predefined; exotic punctuation
(reversed-9 quotes `U+201B`/`U+201F`, hyphen and dash variants
`U+2010`–`U+2015`, `≈ U+2248`) and box-drawing glyphs (`U+2500`–`U+257F`) are
not.  The error fires the first time such a byte reaches the typesetter — in a
literate program, that is wherever the woven code chunk lands (the log shows
the source line, e.g. `l.933`).

### Fix A — declare a printable mapping (preferred, minimal)

Add to the document preamble.  The replacement is normal LaTeX, so map each
code point to a sensible ASCII or math rendering:

```latex
\DeclareUnicodeCharacter{2010}{-}      % hyphen
\DeclareUnicodeCharacter{2012}{-{}-}   % figure dash (-{}- avoids a ligature)
\DeclareUnicodeCharacter{2015}{-{}-{}-}% horizontal bar
\DeclareUnicodeCharacter{201B}{'}      % single high-reversed-9 quote
\DeclareUnicodeCharacter{201F}{"}      % double high-reversed-9 quote
\DeclareUnicodeCharacter{2248}{\ensuremath{\approx}}  % almost equal to
\DeclareUnicodeCharacter{2500}{-}\DeclareUnicodeCharacter{2502}{|}  % box drawing
\DeclareUnicodeCharacter{250C}{+}\DeclareUnicodeCharacter{2510}{+}  % box corners
\DeclareUnicodeCharacter{2514}{+}\DeclareUnicodeCharacter{2518}{+}
```

This needs no extra package — `\DeclareUnicodeCharacter` is provided by the
modern LaTeX kernel even when `inputenc` is not loaded.  ASCII fallbacks also
keep box-drawing art inside the monospace code font instead of shelling out to
a special glyph font.

### Fix B — a purpose-built package

`\usepackage{pmboxdraw}` declares the whole `U+2500` box-drawing range and
draws each glyph from rules.  **Caveat:** it pulls in its own Unicode-dispatch
machinery; if the document already has subtle font issues, prefer the explicit
`\DeclareUnicodeCharacter` mappings above, which touch nothing else.

### Fix C — switch engine

XeLaTeX/LuaLaTeX read UTF-8 natively and need no declarations — but the *font*
must still contain the glyph, and switching engines is a project-wide change
(fonts, fontspec, build rules).  Reserve this for documents that genuinely
need broad Unicode, not for a handful of stray code points.

### Do NOT "fix" it by editing the source

When the offending byte lives in a code chunk, resist deleting or escaping it
in the `.nw`/`.tex` source.  The tangled program often *needs* the real byte at
runtime — a test that asserts an ASCII-art figure is filtered, a normalization
table that maps real typographic punctuation.  Fix the *presentation* in the
preamble; leave the *bytes* alone.

---

## Symptom 2: code/monospace renders in a proportional roman font

The giveaway in extracted text (`pdftotext`): an underscore comes out as `˙`
and straight quotes become curly — e.g. `COMMENT_MARKER = "X"` extracts as
`COMMENT˙MARKER = ”X”`.  That is **OT1 roman**, not typewriter: in the OT1
encoding, slot 95 (`_`) is the dotaccent glyph `˙`, and text fonts apply quote
ligatures.  cmtt (or any real monospace) would show a true underscore.

**Cause.** A monospace font that exists only in **T1** (and TS1) encoding —
notably **Bera Mono** (`beramono`, family `fvm`) — cannot be selected while the
document is still in **OT1**, because `\usepackage[T1]{fontenc}` was never
loaded.  `\ttfamily` then has no usable shape and silently falls back to the
roman family.  `\ttdefault` *looks* correct (`fvm`); the encoding is what is
missing.

### Fix — load T1 fontenc

```latex
\usepackage[T1]{fontenc}  % required so T1-only fonts (Bera Mono, …) select
```

Watch for this when a **local** preamble has the line commented out while the
project's **shared** preamble enables it — a standalone document that inputs
its own preamble can quietly miss it.  Loading `fontenc` is orthogonal to the
Unicode mappings in Symptom 1; a document with woven code typically needs both.

---

## Diagnostics (run these before guessing)

```bash
# Which engine? pdfTeX vs XeTeX/LuaTeX — decides whether Unicode is native.
grep -m1 'This is' doc/ltxobj/forcing.log        # "This is pdfTeX …"

# Count remaining Unicode errors after a fix.
grep -c 'Unicode character' doc/ltxobj/forcing.log

# Per-page font list: is the expected monospace font actually embedded?
pdffonts -f 6 -l 6 doc/forcing.pdf               # look for BeraSansMono / fvm
pdffonts doc/forcing.pdf | grep -i 'bera\|mono'  # …anywhere in the document

# Glyph→Unicode probe: extract a code line and inspect the underscore/quotes.
pdftotext -f 6 -l 6 doc/forcing.pdf - | grep MARKER
#   real "_" and straight quotes  → monospace OK
#   "˙" and curly quotes          → OT1 roman fallback (load T1 fontenc)

# Render a page to eyeball the font directly.
pdftoppm -png -r 150 -f 6 -l 6 doc/forcing.pdf /tmp/page
```

Authoritative test: `pdffonts` shows *which* fonts a page embeds, and
`pdftotext`'s glyph mapping reveals *which encoding* — together they distinguish
"wrong font selected" from "right font, missing glyph" without guesswork.

---

## Quick decision guide

| Build symptom | Likely cause | Fix |
|---|---|---|
| `Unicode character … not set up` | undeclared code point reaches pdfLaTeX | `\DeclareUnicodeCharacter` (Fix A) |
| many box-drawing errors at once | `U+2500` range in source | declare them, or `pmboxdraw` |
| code looks serif; `_`→`˙` in extract | T1-only mono font, no T1 fontenc | `\usepackage[T1]{fontenc}` |
| right font but a glyph is `□`/missing | glyph absent from font | different font, or map the char |
