# Multi-Directory Literate Programming Projects

This reference document provides detailed patterns and examples for organizing large-scale literate programming projects across multiple directories.

## Table of Contents

1. [Repository Structure Patterns](#repository-structure-patterns)
2. [Hierarchical Build Systems](#hierarchical-build-systems)
3. [Documentation Composition](#documentation-composition)
4. [Test Organization](#test-organization)
5. [Navigation Strategies](#navigation-strategies)
6. [Complete Example: The nytid Repository](#complete-example-the-nytid-repository)

---

## Repository Structure Patterns

### The Three-Directory Separation Pattern

For large projects, separate literate sources, documentation builds, and tests into distinct directories:

```
project/
├── Makefile            # Root orchestrator (compile → test → docs)
├── pyproject.toml      # Poetry packaging configuration
├── src/                # Literate source files (.nw)
│   └── package/
│       ├── Makefile
│       ├── module1.nw
│       ├── module2.nw
│       └── subpackage/
│           └── module3.nw
├── doc/                # Documentation build directory
│   ├── Makefile
│   ├── project.nw      # Document wrapper (.nw, not .tex)
│   ├── preamble.tex    # LaTeX preamble (committed to git)
│   └── project.pdf     # Generated documentation
├── tests/              # Extracted test files
│   ├── Makefile
│   └── unit/
│       ├── test_module1.py (generated)
│       └── test_module2.py (generated)
└── makefiles/          # Shared build infrastructure (submodule)
    ├── noweb.mk
    └── subdir.mk
```

### When to Use This Pattern

**Use three-directory separation when:**
- Project has 5+ .nw files
- Multiple developers need clear separation of concerns
- Documentation needs different organization than code
- Tests should be cleanly separated for CI/CD

**Use flat structure when:**
- Single-file or small projects (1-3 .nw files)
- Documentation and code naturally align
- Simpler is better for the use case

### Key Insight

The .nw files in `/src` are the single source of truth. They generate:
- **Code** → tangled back into `/src` alongside the .nw files
- **Documentation** → woven to .tex in `/src`, then included in `/doc` master document
- **Tests** → extracted to `/tests` directory

---

## Hierarchical Build Systems

### The noweb.mk + subdir.mk Pattern

For projects with nested directories, use reusable Makefiles:

**Directory structure:**
```
src/package/
├── Makefile          # This directory's build rules
├── module1.nw
├── module2.nw
└── subpackage/
    ├── Makefile      # Subdirectory's build rules
    └── module3.nw
```

**Parent Makefile** (`src/package/Makefile`):
```makefile
# Declare what to build in this directory
MODULES+=   module1.py
MODULES+=   module2.py

# Declare subdirectories to recurse into
SUBDIR+=    subpackage

# Targets that should propagate to subdirectories
SUBDIR_GOALS=   all clean distclean

# Build everything in this directory
.PHONY: all
all: ${MODULES}

# Include shared build rules
INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
include ${INCLUDE_MAKEFILES}/subdir.mk
```

**Child Makefile** (`src/package/subpackage/Makefile`):
```makefile
MODULES+=   module3.py

.PHONY: all
all: ${MODULES}

# Point to parent's makefiles directory (one level deeper)
INCLUDE_MAKEFILES=../../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
include ${INCLUDE_MAKEFILES}/subdir.mk
```

### The noweb.mk Build Rules

The `noweb.mk` file provides suffix rules for tangling and weaving:

```makefile
# Weaving: .nw → .tex (minted-highlighted, language-aware index)
NOWEAVE.tex?= noweave ${NOWEAVEFLAGS.tex} $< > $@
NOWEAVEFLAGS.tex?= ${NOWEAVEFLAGS} -n -delay -t2 -autolang \
    -autodefs python3 -autodefs sh -autodefs make -index \
    -filter 'tominted -lexer noweb_lexer.py'

.SUFFIXES: .nw .tex
.nw.tex:
    ${NOWEAVE.tex}

# Tangling: .nw → .py
NOTANGLE.py?= notangle ${NOTANGLEFLAGS.py} -R$(notdir $@) \
              $(filter %.nw,$^) > $@ && noroots $(filter %.nw,$^)
NOTANGLE.py+= && ${NOWEB_PYCODEFMT}
NOWEB_PYCODEFMT?= black $@

.SUFFIXES: .nw .py
.nw.py:
    ${NOTANGLE.py}
```

The `-lexer noweb_lexer.py` path is resolved where *LaTeX* runs (the
`doc/` directory), not where noweave runs.  The custom lexer keeps
chunk references hyperlinked even inside Python docstrings; it ships
with noweb and must be copied next to the master document and
whitelisted once per machine in latexminted's config (see
`noweb-commands.md`, "Syntax Highlighting with tominted", and
`project-initialization.md` for the one-time setup).

```makefile
# In doc/Makefile: copy tominted's custom lexer from noweb's lib dir
packagename.pdf: noweb_lexer.py
noweb_lexer.py:
	cp "$$(sed -n 's/^LIB=//p' "$$(command -v noweave)" | head -1)"/$@ $@
```

The LaTeX build must run with `-shell-escape` (minted runs Pygments);
the doc Makefiles below already do via
`latexmk -xelatex -shell-escape` / `LATEXFLAGS += -shell-escape`.

### The subdir.mk Recursion Rules

The `subdir.mk` file enables recursive builds:

```makefile
# Default goals to propagate to subdirectories
SUBDIR_GOALS?=${MAKECMDGOALS}

# For each subdirectory, call make with the current goals
${SUBDIR}::
    ${MAKE} -C $@ ${actual_goals}

# Make subdirectories dependencies of the goals
${actual_goals}: ${SUBDIR}
```

### Pattern: Python __init__.py

Python modules need `__init__.py`. Name the chunk `<<[[__init__.py]]>>` directly
and add an explicit dependency in the Makefile:

```makefile
MODULES+=	__init__.py packagename.tex

__init__.py: packagename.nw
	${NOTANGLE.py}
```

The explicit rule is needed because the `.nw` basename (`packagename`) doesn't
match the output basename (`__init__`), so the default suffix rule won't fire.
`${NOTANGLE.py}` extracts the `<<[[__init__.py]]>>` chunk by name.

**Legacy pattern (still found in nytid):** Older projects use a
`.INTERMEDIATE` + `${MV}` rename trick where `init.nw` tangles to `init.py`
and is then renamed to `__init__.py`. New projects should use the direct
`<<[[__init__.py]]>>` approach above.

### Self-Documenting Build Systems

The build system itself can be literate! Store Makefiles as `.mk.nw`:

```
makefiles/
├── Makefile          # Builds the .mk files
├── noweb.mk.nw       # Literate build rules
├── noweb.mk          # Generated
├── subdir.mk.nw      # Literate recursion rules
├── subdir.mk         # Generated
└── makefiles.pdf     # Documentation of build system
```

### Root Orchestrator Makefile

For projects with packaging (Poetry), create a root Makefile that orchestrates
the compile → test → docs workflow:

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

.PHONY: compile
compile:
	${MAKE} -C src/packagename all
	poetry build

doc/packagename.pdf:
	${MAKE} -C $(dir $@) $(notdir $@)


.PHONY: clean
clean:

.PHONY: distclean
distclean:
	${RM} -R build dist packagename.egg-info src/packagename.egg-info


INCLUDE_MAKEFILES=makefiles
include ${INCLUDE_MAKEFILES}/subdir.mk
```

**Key design:**
- `compile` tangles code then runs `poetry build` to create the wheel.
- `test` depends on `compile` so the package is installed before pytest runs.
- `version` is extracted from `pyproject.toml` for release tagging.
- `SUBDIR` + `subdir.mk` propagate `clean`/`distclean` to all subdirectories.

See `references/project-initialization.md` for the complete project setup.

---

## Documentation Composition

### Master Document Pattern

Create a master document in `/doc` that includes generated .tex from `/src`:

**Directory structure:**
```
project/
├── src/package/
│   ├── module1.nw → module1.py + module1.tex
│   ├── module2.nw → module2.py + module2.tex
│   └── subpackage/
│       └── module3.nw → module3.py + module3.tex
└── doc/
    ├── Makefile
    ├── main.tex       # Master document (source, committed to git)
    ├── preamble.tex   # Shared LaTeX preamble (source, committed to git)
    └── main.pdf       # Generated (gitignored)
```

**Key principle**: `main.tex` and `preamble.tex` are **source files** committed to git.
They are NOT generated from .nw files. Only the woven .tex files in `/src` are generated.

### The Separate Preamble Pattern

**ALWAYS use a separate preamble.tex** that the main document inputs via `\input{preamble}`.
This standard preamble is used consistently across all literate programming projects.

Copy the preamble from the `literate-programming` skill's `references/preamble.tex` file.

**Master document** (`doc/main.tex`):
```latex
\documentclass[a4paper,oneside]{memoir}
\input{preamble}

\usepackage{noweb}
\noweboptions{shift,breakcode,longxref,longchunks}

\title{Project Name}
\author{Author Name}
\date{\today}

\begin{document}
\frontmatter
\maketitle

\begin{abstract}
Brief description of the project.
\end{abstract}

\tableofcontents

\mainmatter

\part{Core Modules}
\input{../src/package/module1.tex}
\input{../src/package/module2.tex}

\part{Extensions}
\input{../src/package/subpackage/module3.tex}

\backmatter
\end{document}
```

### .nw Files as Chapters

Each .nw file should be structured as a **chapter** (not a complete document):

```noweb
\chapter{Module Name}
\label{module-name}

\section{Introduction}
...
```

**Key points:**
- Start with `\chapter{...}` and `\label{...}`
- NO `\documentclass`, `\begin{document}`, `\end{document}`
- NO `\input{preamble}` or `\maketitle`
- The main document provides the document wrapper

### Build Dependencies

The `/doc/Makefile` must declare dependencies on generated .tex files:

```makefile
# Main target
all: main.pdf

# PDF depends on all .tex files from src
main.pdf: ../src/package/module1.tex
main.pdf: ../src/package/module2.tex
main.pdf: ../src/package/subpackage/module3.tex

# Pattern rule: if .tex doesn't exist, make it in src
../src/%::
    ${MAKE} -C $(dir $@) $(notdir $@)

# Compile with LaTeX
main.pdf: main.tex preamble.tex
    latexmk -xelatex -shell-escape main.tex
```

### How It Works

1. `make all` in `/doc` requires `main.pdf`
2. `main.pdf` depends on .tex files from `/src`
3. Those .tex files don't exist yet
4. Pattern rule invokes `make` in the appropriate `/src` subdirectories
5. Subdirectory Makefiles weave .nw → .tex using noweb.mk rules
6. Once all .tex files exist, latexmk compiles the master document

### Benefits

- **Narrative control**: Organize documentation pedagogically, not by implementation order
- **Modular content**: Each .nw contributes a chapter/section
- **Automatic dependencies**: Make tracks .tex changes and rebuilds as needed
- **Separation of concerns**: Code structure vs. documentation structure

### Alternative: .nw Document Wrapper

Instead of a plain `.tex` master document, the document wrapper can be a `.nw`
file. This lets `noweb.mk` weaving rules process it alongside the source `.nw`
files.

**`doc/packagename.nw`:**
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

\title{Project Title}
\author{Author Name}

\begin{document}
\frontmatter
\maketitle

\begin{abstract}
  \input{abstract.tex}
\end{abstract}

\tableofcontents
\clearpage

\mainmatter

\input{../src/packagename/packagename.tex}

\backmatter
\printbibliography

\end{document}
```

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

The `.nw` wrapper is woven to `.tex` by `noweb.mk`, then compiled to PDF.
The `\input` pulls in the woven `.tex` from `/src`.

See `references/project-initialization.md` for the full document setup.

---

## Test Organization

### Test Extraction Pattern

Tests are defined IN the .nw files alongside implementation, but extracted to a separate `/tests` directory.

### Chunk Naming Convention

Use this specific format for test chunks:

```noweb
<<test [[modulename.py]]>>=
import pytest
from package.modulename import *

def test_feature():
    <<test code>>
@
```

The chunk name is `<<test [[modulename.py]]>>` with a **space** between
"test" and the filename. The `[[...]]` brackets make the filename LaTeX-safe
(underscores in filenames won't break documentation).

### Discovery and Extraction Makefile

The `/tests/Makefile` automatically discovers and extracts tests. This is the
full version from the forcing project, handling `[[...]]` brackets, spaces in
chunk names, and the `unit/` subdirectory:

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

### How It Works

1. `find_tests` searches all `.nw` files for `<<test [[*.py]]>>` chunks
2. Encodes spaces as `%20` to avoid Make's word-splitting in `$(foreach)`
3. Outputs triples: `unit/test_name.py:source.nw:test%20[[name.py]]`
4. `def_target` creates a rule that:
   - Creates the `unit/` directory with `mkdir -p`
   - Uses `notangle -R"test [[modulename.py]]"` to extract the chunk
   - Pipes through `cpif` (copy-if-different) to prevent unnecessary rebuilds
   - Runs `noroots` to check for unused chunks
5. `make test` first compiles the package, then runs `poetry run pytest`

### Benefits

- **Co-location**: Tests documented alongside implementation
- **Clean separation**: Tests in dedicated directory for CI/CD
- **Automatic discovery**: Adding a test chunk automatically includes it
- **No test pollution**: Source tree stays clean of test files

---

## Navigation Strategies

### Finding Source Code

**Question**: Where is function X defined?

**Answer**: Search in .nw files:
```bash
grep -r "def function_name" src/**/*.nw
```

### Reading Documentation

**Question**: Where can I read the documentation?

**Answer**: Build and view the PDF:
```bash
cd doc
make all
open main.pdf  # or xdg-open main.pdf on Linux
```

The content comes from .tex files generated from .nw in `/src`, but the presentation is organized in `/doc`.

### Running Tests

**Question**: How do I run tests?

**Answer**: Tests are in `/tests`:
```bash
cd tests
make test
```

Or use pytest directly (after extracting):
```bash
cd tests
make all    # Extract tests from .nw files
pytest
```

### Tracing Generated Code

**Question**: This generated .py file has a bug. Where's the source?

**Answer**:
1. Check for corresponding .nw file: `modulename.py` → `modulename.nw`
2. Search for the problematic code in the .nw file
3. Fix the .nw source (NOT the generated .py)
4. Regenerate: `make` in the directory

**Tip**: Generated files should be in .gitignore, so you can delete them and regenerate:
```bash
rm *.py *.tex
make all
```

### Understanding Dependencies

**Question**: What gets generated from what?

**Answer**: Check the Makefile in each directory:
```bash
cat src/package/Makefile
# Look for MODULES+= lines to see what's built
```

Or use make's dry-run:
```bash
make -n all
# Shows commands that would run
```

---

## Complete Example: The nytid Repository

This section shows a real-world example from the nytid project.

### Overall Structure

```
nytid/
├── src/nytid/           # Literate source files
│   ├── Makefile
│   ├── schedules.nw → schedules.py + schedules.tex
│   ├── http_utils.nw → http_utils.py + http_utils.tex
│   ├── courses/
│   │   ├── Makefile
│   │   ├── init.nw → __init__.py + init.tex + tests
│   │   └── registry.nw → registry.py + registry.tex
│   ├── storage/
│   │   ├── Makefile
│   │   ├── init.nw → __init__.py + init.tex
│   │   └── afs.nw → afs.py + afs.tex
│   └── cli/
│       ├── Makefile
│       ├── init.nw → __init__.py + init.tex + shell scripts
│       ├── courses.nw → courses.py + courses.tex
│       └── utils/
│           ├── Makefile
│           └── rooms.nw → rooms.py + rooms.tex
├── doc/
│   ├── Makefile
│   ├── nytid.tex        # Master document
│   ├── nytid.pdf        # Generated documentation
│   └── preamble.tex
├── tests/
│   ├── Makefile
│   ├── test_courses.py (generated from courses/init.nw)
│   ├── test_sheets.py (generated from signup/sheets.nw)
│   └── test_storage.py (generated)
└── makefiles/           # Shared build infrastructure
    ├── Makefile
    ├── noweb.mk.nw → noweb.mk + noweb.tex
    ├── subdir.mk.nw → subdir.mk + subdir.tex
    └── tex.mk.nw → tex.mk + tex.tex
```

### Example: The courses Module

**File**: `src/nytid/courses/init.nw`

This single .nw file generates:
1. `__init__.py` - Module implementation
2. `init.tex` - Chapter for documentation
3. Test chunks extracted to `tests/test_courses.py`

**Makefile** (`src/nytid/courses/Makefile`):
```makefile
SUBDIR_GOALS=   all clean distclean
SUBDIR+=        # No subdirectories here

MODULES+=       registry.py

# Special handling for __init__.py
.INTERMEDIATE: init.py
__init__.py: init.py
    ${MV} $< $@

.PHONY: all
all: __init__.py ${MODULES}

# Include shared rules (two levels up from src/nytid/courses)
INCLUDE_MAKEFILES=../../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
include ${INCLUDE_MAKEFILES}/subdir.mk
```

**Note:** nytid uses the legacy `.INTERMEDIATE` + `${MV}` rename pattern for
`__init__.py`. New projects should use the direct `<<[[__init__.py]]>>` chunk
name with an explicit dependency rule instead (see "Pattern: Python
\_\_init\_\_.py" above).

### Example: Master Documentation

**File**: `doc/nytid.tex`

```latex
\documentclass{memoir}
\input{preamble}

\begin{document}

\part{The CLI}
\input{../src/nytid/cli/init.tex}
\input{../src/nytid/cli/courses.tex}
\input{../src/nytid/cli/schedule.tex}

\part{Storage}
\input{../src/nytid/storage/init.tex}
\input{../src/nytid/storage/afs.tex}

\part{Managing Courses}
\input{../src/nytid/courses/init.tex}
\input{../src/nytid/courses/registry.tex}

\end{document}
```

**Makefile** (`doc/Makefile`):
```makefile
all: nytid.pdf

# PDF depends on all .tex from src
nytid.pdf: ../src/nytid/cli/init.tex
nytid.pdf: ../src/nytid/cli/courses.tex
nytid.pdf: ../src/nytid/storage/init.tex
nytid.pdf: ../src/nytid/courses/init.tex
# ... more dependencies

# Pattern rule to build .tex in src directories
../src/nytid::
    ${MAKE} -C $@ all

../%::
    ${MAKE} -C $(dir $@) $(notdir $@)

# Compile PDF
INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
```

### Example: Multi-Output from Single .nw

**File**: `src/nytid/cli/init.nw` generates:

1. `__init__.py` (module code)
2. `init.tex` (documentation chapter)
3. `nytid.hourly.sh` (cron script)
4. `nytid.daily.sh` (cron script)
5. `nytid.weekly.sh` (cron script)

**Makefile** (`src/nytid/cli/Makefile`):
```makefile
# Regular module
MODULES+= courses.py
MODULES+= schedule.py

# Extra outputs from init.nw
EXTRAS+= nytid.hourly.sh
EXTRAS+= nytid.daily.sh
EXTRAS+= nytid.weekly.sh

# Special handling for __init__.py
.INTERMEDIATE: init.py
__init__.py: init.py
    ${MV} $< $@

# Extra files depend on init.nw
${EXTRAS}: init.nw
    ${NOTANGLE}
    chmod +x $@

.PHONY: all
all: __init__.py ${MODULES} ${EXTRAS}
```

### Workflow Example

**Adding a new feature:**

1. Edit `src/nytid/courses/init.nw` to add feature
2. Add test chunk `<<test courses.py>>=` with test cases
3. Run `make` in `src/nytid/courses` to generate code
4. Run `make` in `tests` to extract and run tests
5. Run `make` in `doc` to rebuild documentation
6. Commit only the .nw file (generated files are in .gitignore)

**Reading the documentation:**

```bash
cd doc
make all
xdg-open nytid.pdf
```

**Running tests:**

```bash
cd tests
make test
```

### Key Takeaways

1. **Single source of truth**: All content in .nw files
2. **Multiple outputs**: Code, docs, tests, scripts from one source
3. **Clean separation**: /src (sources), /doc (docs), /tests (tests)
4. **Hierarchical builds**: Recursive Makefiles with shared rules
5. **Self-documenting**: Even the build system is literate
6. **Version control**: Only .nw files committed, generated files ignored
