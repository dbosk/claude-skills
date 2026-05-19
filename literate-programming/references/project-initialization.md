# Project Initialization Guide

This reference provides a step-by-step guide for initializing a new literate
programming project with Python packaging. It is based on the canonical
`forcing` project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Canonical Directory Layout](#canonical-directory-layout)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Quick-Reference Checklist](#quick-reference-checklist)

---

## Prerequisites

### Required tools

- **git** — version control
- **noweb** — literate programming system (`notangle`, `noweave`, `noroots`,
  `cpif`)
- **make** — GNU Make for build orchestration
- **poetry** — Python packaging and dependency management
- **black** — Python code formatter (applied automatically after tangling)
- **xelatex** — LaTeX engine (via `latexmk`)
- **latexmk** — LaTeX build automation
- **biber** — BibLaTeX bibliography processor
- **pygments** — syntax highlighting (required by `minted` LaTeX package)

### Required git submodules

- `makefiles/` — shared build rules (`noweb.mk`, `tex.mk`, `subdir.mk`)
  from `https://github.com/dbosk/makefiles.git`
- `didactic/` — pedagogical LaTeX package
  from `https://github.com/dbosk/didactic.git`

---

## Canonical Directory Layout

```
project/
├── .gitignore              # Standard Python template (from GitHub)
├── .gitmodules             # makefiles + didactic submodules
├── Makefile                # Root orchestrator
├── pyproject.toml          # Poetry packaging configuration
├── README.md
├── LICENSE
├── makefiles/              # SUBMODULE: shared build rules
├── didactic/               # SUBMODULE: pedagogical LaTeX
├── src/
│   ├── .gitignore          # *.py  *.tex
│   └── packagename/
│       ├── Makefile         # Tangle + weave rules
│       └── packagename.nw   # Main literate source
├── tests/
│   ├── .gitignore          # *.py
│   ├── Makefile            # Auto-discovers test chunks
│   └── unit/               # Tangled test files land here
└── doc/
    ├── .gitignore          # Project-specific generated files + LaTeX temps
    ├── Makefile
    ├── packagename.nw      # Document wrapper (NOT .tex)
    ├── preamble.tex        # From skill references/preamble.tex
    ├── abstract.tex
    └── bibliography.bib
```

### Key design decisions

- **Directory-level `.gitignore`** files keep patterns simple and
  self-documenting. The root `.gitignore` is the standard Python template with
  no literate-specific rules.
- **The doc wrapper is a `.nw` file**, not a plain `.tex` file, so it can be
  woven by `noweb.mk` rules alongside the source `.nw` files.
- **`unit/` subdirectory** in tests keeps tangled test files separate and
  enables clean `import` paths.

---

## Step-by-Step Setup

### Step 1: Create `pyproject.toml`

```toml
[project]
name = "packagename"
version = "0.1"
description = "Brief project description"
authors = [
    {name = "Your Name"}
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
]


[tool.poetry]
packages = [{include = "packagename", from = "src"}]
include = [
  { path = "src/**/*.py", format = "wheel" },
]
exclude = [
  "src/packagename/.gitignore",
  "src/packagename/Makefile",
  "src/packagename/*.nw",
  "src/packagename/*.tex",
  "src/packagename/CLAUDE.md",
  "src/packagename/ltxobj",
]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[dependency-groups]
dev = [
    "pytest (>=9.0.2,<10.0.0)"
]
```

**Key points:**
- `packages` tells Poetry where to find the package (src layout).
- `include` ensures `.py` files make it into the wheel.
- `exclude` prevents `.nw`, `.tex`, Makefiles, and build artifacts from being
  packaged.

### Step 2: Create `src/.gitignore`

```gitignore
*.py
*.tex
```

This is all that's needed. Every `.py` and `.tex` file under `src/` is
generated from `.nw` sources and must not be committed.

### Step 3: Create `src/packagename/Makefile`

```makefile
NOTANGLEFLAGS.py=

MODULES+=	__init__.py packagename.tex

.PHONY: all
all: ${MODULES}

__init__.py: packagename.nw
	${NOTANGLE.py}


.PHONY: clean
clean:
	${RM} ${MODULES}


INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
include ${INCLUDE_MAKEFILES}/noweb.mk
```

**Why the explicit dependency:** The standard suffix rule `.nw.py` expects the
`.nw` basename to match the `.py` basename. Since `packagename.nw` tangles to
`__init__.py` (different names), we need the explicit rule
`__init__.py: packagename.nw` with `${NOTANGLE.py}`.

**What `${NOTANGLE.py}` expands to:** Something like
`notangle -R"[[__init__.py]]" packagename.nw | cpif __init__.py && black __init__.py`.
The `-R` flag extracts the chunk named `<<[[__init__.py]]>>`.

**`NOTANGLEFLAGS.py=`** clears default flags (some setups add `-L` for line
directives, which aren't valid in Python).

### Step 4: Create initial `src/packagename/packagename.nw`

```noweb
\chapter{Overview}

This literate module is the maintainer's map to the package. It introduces
the generated Python entry point, the major chunk buckets that feed it, and
where tests appear as the implementation is developed. A typical change will
touch one of four areas: imports, constants, classes, or functions, then add
or update the nearby tests that justify that change.

\begin{description}
\item[Generated module] The [[__init__.py]] chunk assembles the import,
  constant, class, and function buckets into the final module.
\item[Chunk buckets] Each bucket groups one kind of contribution so the
  narrative can explain that concern before showing its code.
\item[Test chunks] Tests stay near the implementation they verify rather than
  being collected at the end.
\end{description}

The document starts with the code skeleton below, then expands each bucket in
maintainer order: shared setup first, then core behavior, then tests.

% If the structure becomes hard to explain in prose alone, add a small
% roadmap figure here and remember to load tikz in preamble.tex.

\section{Code overview}

<<[[__init__.py]]>>=
<<imports>>

<<constants>>
<<classes>>
<<functions>>
@

Likewise, we want to test the program.
<<test [[packagename.py]]>>=
import pytest
from packagename import *

<<test setup>>
<<test functions>>
@
```

**Why this pattern works:** The overview names the stable bucket structure,
shows how the generated module is assembled, and tells the maintainer where to
look next. Expand or replace this starter text to match the real structure of
the project; do not leave it as a generic placeholder.

Keep the starter overview and the project's `README.md` aligned as the module
structure evolves; both should point maintainers to the same major parts.

**Chunk naming conventions:**
- `<<[[__init__.py]]>>` — the output filename in double brackets
  (LaTeX-safe, avoids underscore issues)
- `<<test [[packagename.py]]>>` — the test chunk uses the logical module
  name, not the output filename. The test Makefile handles the mapping to
  `unit/test_packagename.py` automatically.

### Step 5: Create `tests/.gitignore` and `tests/Makefile`

**`tests/.gitignore`:**
```gitignore
*.py
```

**`tests/Makefile`** (full auto-discovery version):

```makefile
# Makefile for test suite
#
# Tests are written in .nw files throughout the src/ tree using
# chunks named "<<test [[modulename.py]]>>". This Makefile automatically
# discovers those chunks and tangles them to tests/unit/test_*.py files.

# Auto-discover test chunks in .nw files
# Output format: "unit/test_modulename.py:sourcefile.nw:test%20[[modulename.py]]"
# We encode the single space in "test [[name.py]]" as %20 to avoid
# word-splitting issues, while preserving literal underscores in names like
# "attachment_cache".
define find_tests
( \
	find ../src -name '*.nw' | xargs grep -l '<<test \[\[.*\.py\]\]>>' | \
		while read file; do \
			chunk=$$(grep -o '<<test \[\[\([^]]*\)\.py\]\]>>' "$$file" | head -1 | \
			         sed 's/<<test \[\[\(.*\)\.py\]\]>>/\1/'); \
			chunk_safe=$$(echo "$$chunk" | sed 's/ /%20/g'); \
			echo "unit/test_$${chunk_safe}.py:$$file:test%20[[$$chunk_safe.py]]"; \
		done; \
) | sort -u
endef

# Generate build target for each discovered test
# Input: test_file:source_file:chunk_name_with_%20_for_spaces
# Convert %20 back to spaces for the actual chunk name
define def_target
$(shell echo $1 | cut -d: -f1): $(shell echo $1 | cut -d: -f2)
	@mkdir -p $$(dir $$@)
	notangle -R"$(shell echo $1 | cut -d: -f3 | sed 's/%20/ /g')" $$< | cpif $$@ && noroots $$<
endef

# Discover all tests
TESTS := $(shell $(find_tests))

# Extract just the test filenames for dependencies
TEST_MODULES := $(foreach entry,$(TESTS),$(shell echo $(entry) | cut -d: -f1))

# Main targets
.PHONY: all
all: $(TEST_MODULES)

# Generate rules for each test
$(foreach entry,$(TESTS),$(eval $(call def_target,$(entry))))

# Target to run tests after tangling
.PHONY: test
test: all compile
	poetry run pytest -v

.PHONY: compile
compile:
	$(MAKE) -C ../src/packagename all

# Clean generated test files
.PHONY: clean
clean:
	$(RM) $(TEST_MODULES)
	$(RM) -r .pytest_cache __pycache__ unit/__pycache__
	$(RM) -r htmlcov .coverage
```

**How it works:**
1. `find_tests` searches all `.nw` files for `<<test [[*.py]]>>` chunks.
2. It encodes spaces as `%20` to avoid shell word-splitting.
3. `def_target` creates a Make rule for each test, using `notangle` with the
   chunk name and piping through `cpif` (copy-if-different, prevents
   unnecessary rebuilds).
4. Tests land in `unit/` subdirectory (created by `mkdir -p`).
5. `make test` first compiles the package, then runs `poetry run pytest`.

### Step 6: Create documentation files

**`doc/.gitignore`:**
```gitignore
packagename.tex
packagename.pdf
ltxobj/
_minted*
*.aux
*.bbl
*.bcf
*.blg
*.fdb_latexmk
*.fls
*.idx
*.ilg
*.ind
*.lof
*.log
*.lot
*.nav
*.out
*.run.xml
*.snm
*.synctex.gz
*.toc
*.vrb
```

The first two lines are project-specific (the woven `.tex` and compiled
`.pdf`). The rest are standard LaTeX temporaries.

**`doc/Makefile`:**
```makefile
LATEXFLAGS += -shell-escape

.PHONY: all weave clean distclean
all: packagename.pdf

weave: packagename.tex

../src/packagename/packagename.tex: ../src/packagename/packagename.nw

%.tex: %.nw
	${MAKE} -C $(dirname $@) $(basename $@)

packagename.pdf: packagename.tex ../src/packagename/packagename.tex
packagename.pdf: bibliography.bib preamble.tex

clean:
	${RM} packagename.tex packagename.pdf

distclean:

INCLUDE_MAKEFILES = ../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
```

**`doc/packagename.nw`** (document wrapper):
```noweb
\documentclass[a4paper,oneside]{memoir}
\maxtocdepth{subsection}
\setsecnumdepth{subsection}
\nouppercaseheads

\usepackage{noweb}
\noweboptions{breakcode,longchunks,longxref}

\usepackage[hyphens]{url}
\usepackage[colorlinks]{hyperref}
\usepackage{authblk}

\input{preamble.tex}

\title{%
  Project Title
}
\author{%
  Author Name
}
\affil{%
  Institution\\
  \texttt{email@example.com}
}

\begin{document}
\frontmatter
\maketitle
\thispagestyle{empty}

\begin{abstract}
  \input{abstract.tex}
\end{abstract}

\vspace*{\fill}
\VerbatimInput{../LICENSE}
\clearpage

\tableofcontents
\clearpage

\mainmatter

\input{../src/packagename/packagename.tex}


\backmatter
\printbibliography


\end{document}
```

**Note:** This is a `.nw` file (not `.tex`) so that the `noweb.mk` weaving
rules can process it. The document `\input`s the woven `.tex` from `src/`.

**`doc/preamble.tex`:** Copy from the skill's `references/preamble.tex`.

**`doc/abstract.tex`:**
```latex
Brief description of the project.
```

**`doc/bibliography.bib`:**
```bibtex
% Add bibliography entries here
```

### Step 7: Create root Makefile

```makefile
SUBDIR_GOALS=	all clean distclean

SUBDIR+=		src/packagename
SUBDIR+=		tests
SUBDIR+=		doc

version=$(shell sed -n 's/^ *version *= *\"\([^\"]\+\)\"/\1/p' pyproject.toml)


.PHONY: all
all: compile doc/packagename.pdf test

.PHONY: test
test: compile
	${MAKE} -C tests test

.PHONY: install
install: compile
	pipx install .

.PHONY: compile
compile:
	${MAKE} -C src/packagename all
	poetry build

.PHONY: publish publish-github publish-pypi
publish: publish-github

publish-github: doc/packagename.pdf
	git push
	gh release create -t v${version} v${version} doc/packagename.pdf

doc/packagename.pdf:
	${MAKE} -C $(dir $@) $(notdir $@)

publish-pypi: compile
	poetry publish


.PHONY: clean
clean:

.PHONY: distclean
distclean:
	${RM} -R build dist packagename.egg-info src/packagename.egg-info


INCLUDE_MAKEFILES=makefiles
include ${INCLUDE_MAKEFILES}/subdir.mk
```

**How it works:**
- `make` (default) runs: compile → docs → test, in that order.
- `compile` tangles `.nw` → `.py` then runs `poetry build`.
- `test` depends on `compile` (package must be built first).
- `version` is extracted from `pyproject.toml` for release tagging.
- `SUBDIR` + `subdir.mk` enables recursive `make clean`/`make distclean`.

### Step 8: Git submodules and first build

```bash
# Initialize the repository
git init
git submodule add https://github.com/dbosk/makefiles.git makefiles
git submodule add https://github.com/dbosk/didactic.git didactic
git submodule update --recursive --init

# Install dev dependencies
poetry install

# First build
make

# Verify
make test
```

**First commit checklist:**
- [ ] `.gitignore` (standard Python template)
- [ ] `.gitmodules`
- [ ] `Makefile` (root orchestrator)
- [ ] `pyproject.toml`
- [ ] `README.md`
- [ ] `LICENSE`
- [ ] `src/.gitignore`
- [ ] `src/packagename/Makefile`
- [ ] `src/packagename/packagename.nw`
- [ ] `tests/.gitignore`
- [ ] `tests/Makefile`
- [ ] `doc/.gitignore`
- [ ] `doc/Makefile`
- [ ] `doc/packagename.nw`
- [ ] `doc/preamble.tex`
- [ ] `doc/abstract.tex`
- [ ] `doc/bibliography.bib`

**Do NOT commit:** Any `.py`, `.tex` (in `src/`), `.pdf`, or `ltxobj/`
files — these are all generated.

---

## Quick-Reference Checklist

When initializing a new project, verify:

1. **`pyproject.toml`** has `[tool.poetry]` with `packages`, `include`, and
   `exclude` configured
2. **`src/.gitignore`** contains `*.py` and `*.tex`
3. **`src/packagename/Makefile`** has explicit `__init__.py: packagename.nw`
   rule with `${NOTANGLE.py}`
4. **`src/packagename/packagename.nw`** has both `<<[[__init__.py]]>>` and
   `<<test [[packagename.py]]>>` chunks
5. **`tests/.gitignore`** contains `*.py`
6. **`tests/Makefile`** uses `%20` encoding, `cpif`, and `unit/` subdirectory
7. **`doc/.gitignore`** lists project-specific generated files + LaTeX temps
8. **`doc/packagename.nw`** is a `.nw` file (not `.tex`) wrapping the
   document
9. **`doc/preamble.tex`** is copied from skill references
10. **Root `Makefile`** orchestrates compile → test → docs with `subdir.mk`
11. **Git submodules** (`makefiles/`, `didactic/`) are initialized
12. **No generated files** are tracked by git
