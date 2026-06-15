# Noweb Commands Reference

This reference provides detailed documentation for noweb commands used in literate programming.

## Table of Contents

1. [Tangling (Extracting Code)](#tangling-extracting-code)
2. [Weaving (Creating Documentation)](#weaving-creating-documentation)
3. [Syntax Highlighting with tominted](#syntax-highlighting-with-tominted)
4. [Mixed-Language Documents and autolang](#mixed-language-documents-and-autolang)
5. [Common Patterns](#common-patterns)
6. [Language-Specific Notes](#language-specific-notes)
7. [Troubleshooting](#troubleshooting)

---

## Tangling (Extracting Code)

Tangling extracts executable code from a literate program.

### Basic Usage

```bash
# Extract a specific root chunk
notangle -Rchunkname file.nw > output.ext

# With line number directives for debugging
notangle -L -Rchunkname file.nw > output.ext

# Default root is <<*>>
notangle file.nw > output.ext

# List all root chunks (not used in other chunks)
noroots file.nw
```

### Common Flags

| Flag | Description |
|------|-------------|
| `-R<name>` | Specify root chunk to extract (can be repeated) |
| `-L` | Emit line number directives (`#line` for C, etc.) |
| `-L'format'` | Custom line number format |
| `-t<n>` | Preserve tabs, with stops every n columns |
| `-filter cmd` | Filter through command before tangling |

### [[...]] Notation for LaTeX-Safe Chunk Names

When chunk names contain underscores (common in Python), LaTeX interprets them as math subscripts, causing compilation errors. Use noweb's `[[...]]` notation:

```noweb
<<[[module_name.py]]>>=
def my_function():
    pass
@
```

Extract with:

```bash
notangle -R"[[module_name.py]]" file.nw > module_name.py
```

**Why this works:**
- `[[...]]` tells noweb to escape all LaTeX special characters
- Works for underscores, hashes, ampersands, and other special characters
- Chunk name matches filename exactly (no renaming needed)

---

## Weaving (Creating Documentation)

Weaving produces documentation from a literate program.

### Basic Usage

```bash
# Standard recipe: minted-highlighted, language-aware index,
# for inclusion in a master document
noweave -n -delay -autolang -autodefs python3 -autodefs sh \
    -autodefs make -index \
    -filter 'tominted -lexer noweb_lexer.py' file.nw > file.tex

# Same, standalone: noweave emits the wrapper, and -minted makes that
# generated preamble load minted (it bundles -option minted with
# -filter tominted).  Use -minted instead of -delay/-filter here.
noweave -autolang -autodefs python3 -autodefs sh \
    -autodefs make -index -minted file.nw > file.tex
# -minted runs plain tominted; for the custom lexer in a standalone
# weave, spell it out: -option minted -filter 'tominted -lexer noweb_lexer.py'

# Classic rendering (no highlighting; identifier uses inside code
# are hyperlinked — only this mode has those links)
noweave -n -delay -autolang -autodefs python3 -autodefs sh \
    -autodefs make -index file.nw > file.tex

# Minimal cross-references only
noweave -latex -x file.nw > output.tex

# Generate HTML (tominted is LaTeX-only; never combine with -html)
noweave -html -index -autodefs lang file.nw > output.html
```

The standard recipe requires the one-time custom-lexer setup described
under [Syntax Highlighting with tominted](#syntax-highlighting-with-tominted),
and the woven document must be compiled with `-shell-escape`.

The document must also load the `minted` package.  The noweb package
loads it on request, so there is no separate `\usepackage{minted}` to
remember: write `\usepackage[minted]{noweb}` in a master document's
preamble (the inclusion case), or pass `-minted` when noweave generates
the preamble (the standalone case).

### Common Flags

| Flag | Description |
|------|-------------|
| `-latex` | Emit LaTeX (default) |
| `-html` | Emit HTML |
| `-tex` | Emit plain TeX |
| `-n` | No wrapper (no document structure) |
| `-delay` | Delay file info until after first doc chunk |
| `-x` | Add cross-references and chunk definitions |
| `-index` | Build identifier index |
| `-autodefs lang` | Auto-detect definitions in language |
| `-autolang` | Annotate chunks with their language; autodefs filters then skip foreign chunks |
| `-filter cmd` | Insert filter into the pipeline (after the autodefs filters) |
| `-t<n>` | Expand tabs to n columns |

Pipeline ordering: `-autolang` places the annotator *first* in the
pipeline no matter where the option appears on the command line, so the
annotations exist before the autodefs filters read the stream.  A plain
`-filter` always slots *after* the autodefs filters; give `tominted` as
the last filter, after `-index`.  The dbosk fork's pipeline is
unbounded, so any number of filters may be stacked (see the budget note
under the standard weave in `SKILL.md`).

### Weaving for Inclusion

When weaving for inclusion in a master document, use `-n -delay`:

```bash
noweave -n -delay -autolang -autodefs python3 -autodefs sh \
    -autodefs make -index \
    -filter 'tominted -lexer noweb_lexer.py' file.nw > file.tex
```

This produces .tex without `\documentclass`, suitable for `\input{...}`.

Fallback without the patched noweb (no `autolang`/`tominted`):

```bash
noweave -n -delay -x -t2 file.nw > file.tex
```

---

## Syntax Highlighting with tominted

The `tominted` filter makes noweave's LaTeX output typeset every code
chunk with the `minted` package, so each chunk is syntax-highlighted by
a lexer chosen *per chunk*.

### How the language is chosen

- A chunk whose name looks like a filename gets that filename's
  language: `<<[[fib.py]]>>` → Python, `<<[[Makefile]]>>` → Make.
- Chunks with non-filename names (`<<functions>>`, `<<test functions>>`)
  inherit the language of the chunks that *use* them.
- An explicit `@language` annotation in the pipeline (see
  [autolang](#mixed-language-documents-and-autolang)) overrides
  inference.
- Built-in tables cover the popular languages; filenames they miss are
  matched against Pygments' own filename patterns, so any language
  Pygments can highlight is recognized.  Chunks of unknown language
  keep the standard noweb rendering.
- Extend or override the tables with mapping arguments, each of the
  form `.ext=lexer` or `name=lexer`:
  `-filter 'tominted .jl=julia GNUmakefile=make'`.  The `autolang`
  filter accepts the same mappings.

### Requirements

- noweb built with the `tominted`/`autolang` filters (dbosk fork) and
  the Icon tools (for the autodefs filters).
- Python 3 and Pygments where the filter and LaTeX run.
- The document must load `minted` and be compiled with `-shell-escape`:
  `pdflatex -shell-escape file.tex`, or the corresponding latexmk
  option.  Load minted through the noweb package rather than by hand:
  `\usepackage[minted]{noweb}` in the preamble, or `-minted` when
  noweave generates the preamble (the skill's `preamble.tex` does the
  former).
- Add `_minted*` to `.gitignore` (see `git-workflow.md`).
- LaTeX only — never combine `tominted` with `-html`.

### Trade-off versus the classic rendering

With `tominted`, minted owns the code body: identifier *definitions*
stay in the index and chunk references inside code remain hyperlinked,
but identifier *uses* inside highlighted chunks are no longer
hyperlinked.  If those use-links matter more than highlighting, drop
the `-filter tominted ...` argument and weave the classic rendering.

### One-time custom-lexer setup (standard recipe)

Plain `tominted` shows a chunk reference *inside a Python string
literal* (e.g. a docstring chunk) as literal `<<...>>` text, because
Pygments' escape mechanism refuses to work inside string tokens.  The
bundled custom lexer `noweb_lexer.py` lifts that limitation, keeping
even in-docstring references hyperlinked — hence the standard recipe's
`-filter 'tominted -lexer noweb_lexer.py'`.

The lexer file must be readable from the directory where LaTeX runs.
It is installed in noweb's library directory, discoverable from the
`noweave` script:

```bash
NOWEB_LIB=$(sed -n 's/^LIB=//p' "$(command -v noweave)" | head -1)
cp "$NOWEB_LIB/noweb_lexer.py" .
```

Because minted treats loading custom lexer files as arbitrary code
execution, latexminted requires the file to be whitelisted by SHA-256
hash (one-time per machine, repeated whenever the lexer file changes,
e.g. after a noweb upgrade):

```bash
mkdir -p ~/.config/latexminted
printf '{"custom_lexers": {"noweb_lexer.py": "%s"}}\n' \
    "$(sha256sum noweb_lexer.py | cut -d' ' -f1)" \
    > ~/.config/latexminted/.latexminted_config
```

The `-lexer` path is interpreted relative to the directory where LaTeX
runs.

---

## Mixed-Language Documents and autolang

`noweave -autolang` runs the `autolang` filter, which annotates every
code chunk with the `@language` pipeline keyword using the same
inference rules as `tominted` (filename-like names, inheritance through
chunk uses; chunks whose language remains unknown are left
unannotated).

The autodefs filters then *skip* chunks written in languages they do
not understand.  This is what keeps a mixed-language document's index
clean: without it, `-autodefs python3` happily indexes `PYTHON = ...`
and `COUNT = ...` from a Makefile chunk, because make's variable
assignments match the Python assignment pattern.  With `-autolang`,
only the Python chunks feed the Python filter.

Notes:

- Unannotated chunks are scanned by every autodefs filter, as before —
  so a document without filename-like chunk names behaves exactly as
  it always did.
- Running `autolang` twice is harmless: already-annotated chunks are
  left alone.
- The annotations are consumed by `tominted` and ignored silently by
  the standard backends, so `-autolang` is safe even without
  `tominted`.

---

## Common Patterns

### Multiple Outputs from One File

```bash
notangle -Rprogram.c file.nw > program.c
notangle -Rprogram.h file.nw > program.h
notangle -RMakefile file.nw > Makefile
```

### Building with Make

```makefile
%.py: %.nw
    notangle -R$@ $< > $@

%.tex: %.nw
    noweave -n -delay -autolang -autodefs python3 -autodefs sh -autodefs make -index \
        -filter 'tominted -lexer noweb_lexer.py' $< > $@

%.pdf: %.tex noweb_lexer.py
    pdflatex -shell-escape $<

# tominted's custom lexer must sit where LaTeX runs
noweb_lexer.py:
    cp "$$(sed -n 's/^LIB=//p' "$$(command -v noweave)" | head -1)"/$@ $@
```

### Documentation with Tests

Interleave test code with implementation:

```noweb
Here's our sort function:
<<sort function>>=
def sort(lst):
    <<sorting implementation>>
@

Let's verify it works:
<<test code>>=
assert sort([3,1,2]) == [1,2,3]
@
```

---

## Language-Specific Notes

### C/C++

- Use `-L` flag for `#line` directives
- Put headers and implementation in same .nw file
- Extract with: `notangle -L -Rfile.cpp file.nw > file.cpp`

### Python

- No special flags needed for tangling
- Weave with `-autodefs python3` for the identifier index.  It indexes
  top-level `def` and `async def` functions, top-level classes, and
  top-level simple assignments `NAME = value`.  With
  `-filter 'autodefs.python3 -local'` it additionally indexes methods
  and nested functions.  Function-local variables, tuple unpacking,
  attribute assignments and annotated assignments are never indexed.
- Combine with `-autolang` so Makefile or other foreign chunks don't
  leak into the Python index (see
  [Mixed-Language Documents](#mixed-language-documents-and-autolang))
- Keep lines under 80 characters in .nw files
- Consider using formatters on output: `notangle -Rfile.py file.nw | black - > file.py`
- Note: Black may reformat to different line lengths

**Docstring Anti-Pattern**: Never include LaTeX commands in Python docstrings.

**Bad** - LaTeX in docstring causes warnings:
```python
def func(x):
    """See \cref{Section} for details."""  # WARNING: invalid escape
    ...
```

**Good** - Plain docstring, LaTeX in literate source:
```noweb
This function implements the algorithm from \cref{Algorithm}.

<<functions>>=
def func(x):
    """Process the input using the algorithm."""
    ...
@
```

### Haskell

- Use `-L` flag (GHC understands line pragmas)
- Note: Haskell also has native `.lhs` literate format

### Make

- Use `-t8` to preserve the tabs make needs:
  `notangle -t8 -R'[[Makefile]]' file.nw > Makefile`
  (by default notangle expands tabs to spaces, which breaks make)
- The chunk name `<<[[Makefile]]>>` also tells `autolang`/`tominted`
  to highlight the chunk as Make

### Shell Scripts

- No special flags needed
- Remember to `chmod +x` the output

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "chunk not defined" error | Check chunk name spelling with `noroots` |
| Line numbers wrong in debugger | Use `-L` flag with notangle |
| Formatting broken | Check that `<<` starts in column 1 |
| Chunks in wrong order | Remember, notangle assembles them correctly |
| Documentation not rendering | Verify `@` markers for documentation chunks |
| LaTeX errors with underscores | Use `[[...]]` notation for chunk names |

### Using noroots

The `noroots` command lists all root chunks (chunks not referenced by other chunks). Use it to:

1. Find typos in chunk names (orphaned chunks appear in output)
2. Discover all extractable targets in a file
3. Verify your main chunk is not accidentally referenced elsewhere

```bash
noroots file.nw
# Output: <<main.py>> <<test.py>> <<Makefile>>
```

If you see a chunk you expect to be used, check for spelling errors in references.
