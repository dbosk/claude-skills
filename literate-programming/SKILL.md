---
name: literate-programming
description: "CRITICAL: ALWAYS activate this skill BEFORE making ANY changes to .nw files. Use proactively when: (1) creating, editing, reviewing, or improving any .nw file, (2) planning to add/modify functionality in files with .nw extension, (3) user asks about literate quality, (4) user mentions noweb, literate programming, tangling, or weaving, (5) working in directories containing .nw files, (6) creating new modules/files that will be .nw format. Trigger phrases: 'create module', 'add feature', 'update', 'modify', 'fix' + any .nw file. Never edit .nw files directly without first activating this skill to ensure literate programming principles are applied. (project, gitignored)"
---

# Literate Programming Skill

**CRITICAL: This skill MUST be activated BEFORE making any changes to .nw files!**

You are an expert in literate programming using the noweb system.

## Reference Files

This skill includes detailed references in `references/`:

| File | Content | Search patterns |
|------|---------|-----------------|
| `noweb-commands.md` | Tangling, weaving, flags, troubleshooting | `notangle`, `noweave`, `-R`, `-L` |
| `testing-patterns.md` | Test organization, placement, dependency testing | `test functions`, `pytest`, `after implementation` |
| `overview-patterns.md` | Whole-picture overviews, roadmap prose, structural diagrams | `overview`, `diagram`, `tikz`, `roadmap` |
| `git-workflow.md` | Version control, .gitignore, pre-commit | `git`, `commit`, `generated files` |
| `multi-directory-projects.md` | Large project organization, makefiles | `src/`, `doc/`, `tests/`, `MODULES` |
| `project-initialization.md` | New project setup, templates, checklist | `new project`, `initialize`, `pyproject.toml` |
| `preamble.tex` | Standard LaTeX preamble for documentation | `\usepackage`, `memoir` |

## When to Use This Skill

### Correct Workflow

1. User asks to modify a .nw file
2. **YOU ACTIVATE THIS SKILL IMMEDIATELY**
3. You plan the changes with literate programming principles
4. You make the changes following the principles
5. You regenerate code with make/notangle

### Anti-pattern (NEVER do this)

1. User asks to modify a .nw file
2. You directly edit the .nw file  ← WRONG
3. Later review finds literate quality problems
4. You have to redo everything

### Remember

- .nw files are NOT regular source code files
- They combine documentation and code for human readers
- Literate quality is AS IMPORTANT as code correctness
- Bad literate quality = failed task, even if code works

## Planning Changes

When making changes to a .nw file:

1. **Read the existing file** to understand structure and narrative
2. **Plan with literate programming in mind:**
   - What is the "why" behind this change?
   - Why does this approach work, not just why was it chosen?
   - How does this fit into the existing narrative?
   - Does the document need an early whole-picture overview before details?
   - Which overview, intro, roadmap figure, or relevant `README.md`
     summarizes this area, and does this change make it stale?
   - What new chunks are needed? What are their meaningful names?
   - Where in the pedagogical order should this be explained?
3. **Design documentation BEFORE writing code:**
   - Write prose explaining the problem and solution
   - Use subsections to structure complex explanations
   - For substantial `.nw` files, give maintainers the whole before the
     parts. If relationships are hard to hold in prose, add a structural
     figure. See `references/overview-patterns.md`.
4. **Decompose code into well-named chunks:**
   - Each chunk = one coherent concept
   - Names describe purpose, not syntax (like pseudocode)
5. **Write the code chunks**
6. **Regenerate and test**

**Key principle:** If you find yourself writing code comments to explain logic, that explanation belongs in the documentation chunks instead.

## Reviewing Literate Programs

When reviewing, evaluate:

1. **Narrative flow**: Coherent story? Pedagogical order?
2. **Variation theory**: Contrasts used? "Whole, parts, whole" structure?
   Maintainer-facing `.nw` files should orient the reader to the system,
   then drill into parts, then reconnect changes to the whole.
3. **Chunk quality**: Meaningful names? Focused on single concepts?  Bucket
   chunks named with nouns (`<<option completions>>`), not verb phrases
   (`<<wire option completions>>`)?
4. **Explanation quality**: Explains "why" not just "what"?  The
   explanation should also say why the chosen approach works.  Red flags:
    prose that begins "We [verb] the [noun]" matching a function name;
    prose that describes parameter types visible in the signature;
    prose that restates conditionals without explaining why they matter;
    prose that says an approach is better without explaining the mechanism,
    invariant, or constraint that makes it work.
5. **Test organization**: Tests after implementation, not before?
6. **Proper noweb syntax**: `[[code]]` notation in prose? Identifiers in
   chunk titles escaped with `[[...]]`? Valid chunk references?
7. **Overview quality**: For non-trivial files, does the overview identify
   the main parts, how they relate, and where the document will go next?
   Is the level appropriate for a maintainer who knows the language but not
   this codebase?
8. **Visual clarity**: When the structure is distributed, non-linear, or
   hard to track in prose, does the document add a roadmap or diagram?
9. **Overview maintenance**: When structure, flow, chunk organization,
   entry points, or likely edit locations changed, were the overview,
   local intro prose, roadmap figures, and any relevant `README.md` kept in
   sync?
10. **Co-location and consistency**: Are wiring chunks (attribute
   assignments, register/install calls, decorator-style mutation) placed
   next to the entities they mutate, not the helpers they call?  When the
   same task is solved in multiple places in the file, do they share a
   pattern — or does prose explain why a particular site diverges?

## Core Philosophy

Literate programming (Knuth) has two goals:

1. **Explain to human beings what we want a computer to do**
2. **Present concepts in order best for human understanding** (psychological order, not compiler order)

### Variation Theory

Apply `variation-theory` skill when structuring explanations:

- **Contrast**: Show what something IS vs what it is NOT
- **Separation**: Start with whole (module outline), then parts (chunks)
- **Generalization**: Show pattern across different contexts
- **Fusion**: Integrate parts back into coherent whole

When the literate document is student-facing educational LaTeX, keep
pedagogical meta-commentary such as variation/invariance labels and
sequencing rationale out of the visible narrative.  Put that reasoning in
`\ltnote{...}` via the `didactic-notes` skill.

`\ltnote{...}` is also available in an ordinary (maintainer-facing) literate
program, but scope it tightly: it is for reasoning about the **exposition**, not
the code.  A note on *why the narrative is ordered as it is* — why function A is
explained before function B, why a concept is introduced in this chapter rather
than later, why the whole precedes the parts — is commentary about the writing
and belongs in an `\ltnote`.  A design decision about the code itself (an
architecture choice, why a data structure was picked, the rationale and any
citations behind it) is *content*: it belongs in the visible body prose.  The
test: if removing the note would lose information about the program, it is body
text; if it would only lose information about how the explanation was authored,
it is an `\ltnote`.  See the `didactic-notes` skill for details.

If the `.nw` document generates slides or handouts with live questions, Mentipy
is a suitable tool for embedding those prompts in the LaTeX output.

**CRITICAL**: Show concrete examples FIRST, then state general principles. Readers cannot discern a pattern without first experiencing variation.

## Noweb File Format

### Documentation Chunks

- Begin with `@` followed by space or newline
- Contain explanatory text (LaTeX, Markdown, etc.)
- Copied verbatim by noweave

### Code Chunks

- Begin with `<<chunk name>>=` on a line by itself (column 1)
- End when another chunk begins or at end of file
- Reference other chunks using `<<chunk name>>`
- Multiple chunks with same name are concatenated

### Syntax Rules

- Quote code in documentation using `[[code]]` (escapes LaTeX special chars).
  Never manually escape characters (e.g. `\_`) inside `[[...]]` — noweb
  handles all escaping automatically.  Writing `[[\_]]` double-escapes.
- `[[...]]` works inside `\item[...]` labels (and other moving arguments),
  but separate the inner `]]` from the outer `]` with at least one
  character — typically a space.  The failure mode is **three brackets in
  a row** (`]]]`), where noweb's `]]` terminator and LaTeX's `]` argument
  terminator collide and produce a `Runaway argument? ! Paragraph ended
  before \@item was complete.` error.

  **GOOD** — `]]` is followed by a space or by other text:
  ```latex
  \item[The [[--restart]] flag] explains the idempotence rule.
  \item[ [[shell-basics $]] ] anchors on the nested shell prompt.
  ```

  **BAD** — `[[...]]` butts directly against the closing `]`:
  ```latex
  \item[The required pattern [[shell-basics $]]]   % Runaway argument
  ```

  The same rule applies to any other LaTeX macro argument that is
  delimited with brackets (`\caption[...]`, `\section[...]` short forms,
  etc.).  When in doubt, add a trailing space inside the outer brackets.
- Escape: `@<<` for literal `<<`, `@@` in column 1 for literal `@`

### Don't Write `@` Between Adjacent Code Chunks

`@` *starts* a documentation chunk; it is not a code-chunk terminator.  A code
chunk already ends the moment *any* chunk begins — including another named code
chunk.  So when one code chunk is immediately followed by another with no prose
between them, **no `@` is needed**: the second chunk closes the first on its
own.

Worse, a stray `@` (followed by a blank line) opens an *empty documentation
chunk*, which `noweave` renders as **unwanted vertical space** in the woven
PDF.

Rule of thumb: write `@` only when documentation prose follows the code.  This
is the complement of Writing Guideline 14 (prose-follows ⇒ `@`; code-follows ⇒
no `@`).

**GOOD** — the second chunk ends the first; no `@`, no empty doc chunk:
```noweb
<<constants>>=
CONST = 3.14
<<functions>>=
def area_of_circle(radius):
    return CONST * radius ** 2
@
```

**BAD** — redundant `@` opens an empty doc chunk → unwanted space in the PDF:
```noweb
<<constants>>=
CONST = 3.14
@

<<functions>>=
def area_of_circle(radius):
    return CONST * radius ** 2
@
```

### Embedding Heredocs — Keep the Delimiter Pair in the Wrapper Chunk

When a tangled script embeds a heredoc (a shell `<<EOF ... EOF`, an inline
`python3 - <<EOF`, a `cat > file <<EOF`, etc.), **put both the opening
`<<DELIM` and the closing `DELIM` in the same wrapper chunk, with a single
chunk reference for the body in between.** Define the body in its own chunk
that contains *only* the payload — never the delimiter.

This matters because noweb chunk boundaries and the heredoc are two
independent layers: noweb blindly concatenates every definition of the body
chunk, and the shell only sees the tangled text. If the closing delimiter is
written inside the body chunk (especially when the body is built from several
concatenated definitions), the heredoc terminates after the *first* piece and
everything after it tangles as code instead of data — a syntax error far from
its cause.

**GOOD** — delimiter pair together in the wrapper; body chunk holds only the
payload (and may be split across several definitions safely):
```noweb
<<write the config>>=
cat > "$file" <<'_EOF'
<<config body>>
_EOF
@

<<config body>>=
first line of payload
@

<<config body>>=
more payload, concatenated by noweb into the same heredoc
@
```

**BAD** — the closing delimiter lives in the body chunk, so a second
definition (or any following chunk) escapes the heredoc:
```noweb
<<write the config>>=
cat > "$file" <<'_EOF'
<<config body>>
@

<<config body>>=
first line of payload
_EOF
@

<<config body>>=
this never reaches the heredoc — it tangles as shell
@
```

Quote the opening delimiter (`<<'_EOF'`) when the payload must not undergo
shell expansion — for example embedded Python or JSON containing `$`. A
distinctive delimiter such as `_EOF` or `PYEOF` keeps it easy to see the pair
at a glance.

## Writing Guidelines

1. **Start with the human story** - problem, approach, design decisions
2. **Give the whole before the parts** - substantial maintainer-facing
   documents should start with an overview of the moving pieces, their
   relationships, and the route through the file
3. **Introduce concepts in pedagogical order** - not compiler order
4. **Use meaningful chunk names** - 2-5 word summary of purpose (like pseudocode).

   **Bucket chunks are named with nouns; phase chunks may be imperative.**
   A bucket chunk holds the same *kind* of content across many definitions
   and is named as a category: `<<constants>>`, `<<functions>>`,
   `<<imports>>`, `<<test functions>>`, `<<repo methods>>`,
   `<<option completions>>`.  Phase sub-chunks (Guideline 8) are different —
   they describe a step in an algorithm and read naturally as imperatives
   (`<<pick random starting point>>`, `<<collect sentences until target
   length>>`).

   **BAD** — verb-phrase bucket name:
   ```noweb
   <<wire option completions>>=
   LAYOUT_OPTION.autocompletion = _choice_completer(LAYOUT_CHOICES)
   @
   ```

   **GOOD** — noun bucket name:
   ```noweb
   <<option completions>>=
   LAYOUT_OPTION.autocompletion = _choice_completer(LAYOUT_CHOICES)
   @
   ```
5. **Escape all identifiers in chunk names** — any identifier (variable,
   function, parameter, attribute) that appears in a chunk title must be
   wrapped in `[[...]]`.  This tells noweave to render it as code
   (monospace) and prevents LaTeX errors from underscores.

   **BAD** — bare identifier, underscore breaks LaTeX:
   ```noweb
   <<restrict to top-level when not show_tree>>=
   if not show_tree:
       ...
   @
   ```

   **GOOD** — identifier escaped with `[[...]]`:
   ```noweb
   <<restrict to top-level when not [[show_tree]]>>=
   if not show_tree:
       ...
   @
   ```

   Other examples: `<<add graders to [[graders]] list>>`,
   `<<initialise [[default_username]]>>`.

   **IMPORTANT**: Do not escape underscores or other special characters
   *inside* `[[...]]`.  The brackets already tell noweb to escape
   everything.  `[[__init__.py]]` is correct;
   `[[\_\_init\_\_.py]]` is wrong and will double-escape.
6. **Decompose by concept, not syntax**
7. **Explain the "why"** - don't just describe what the code does.
   Prose that merely restates the code in English teaches nothing.  Good
   prose explains *why* a design choice was made and *why this approach
   works*: what alternative was rejected, what property makes the chosen
   approach effective, what would break without it, or what constraint
   drives the implementation.

   **Self-test:** If your prose could be mechanically generated from the
   function signature, it's "what" not "why."  Ask yourself: *What design
   decision does this paragraph justify?  What alternative did we reject
   and why?  Why does the chosen approach work here?*  If the paragraph
   doesn't answer those questions, rewrite it.

   **BAD** — prose restates code in English:
   ```noweb
   \subsection{Counting $n$-grams}

   We count overlapping $n$-grams.
   If $n$ is larger than the input, the result is empty.

   <<functions>>=
   def ngram_counts(text, *, n):
       ...
   @
   ```

   **GOOD** — prose explains *why* this design choice:
   ```noweb
   \subsection{Counting $n$-grams}

   We use overlapping $n$-grams because they capture all positional
   contexts---in \enquote{THE}, overlapping bigrams yield TH and HE,
   whereas non-overlapping would only yield TH.  This matches the
   standard definition used in cryptanalysis.

   <<functions>>=
   def ngram_counts(text, *, n):
       ...
   @
   ```

   **Red flags** that prose is "what" not "why":
   - Begins "We [verb] the [noun]" where the verb matches a function name
   - Describes parameter types or return values already in the signature
   - Restates conditional logic ("If X, we do Y") without explaining
     *why* X matters
7. **Keep chunks focused — one function per `<<functions>>=` chunk with
   prose before it.** Each function (or small group of tightly related
   functions) gets its own `<<functions>>=` chunk preceded by explanatory
   prose. Never put multiple unrelated functions in a single chunk.

   **BAD** — four functions crammed into one chunk with minimal prose:
   ```noweb
   \subsection{Helper Functions}

   We provide several utility functions.

   <<functions>>=
   def normalize_text(text): ...

   def letters_only(text): ...

   def key_shifts(key): ...

   def index_of_coincidence(text): ...
   @
   ```

   **GOOD** — each function with its own subsection and prose:
   ```noweb
   \subsection{Text Normalization}

   Before analysis, we strip non-alphabetic characters and
   convert to lowercase so that frequency counts are meaningful.

   <<functions>>=
   def normalize_text(text): ...
   @

   \subsection{Index of Coincidence}

   The index of coincidence measures how likely two randomly
   chosen letters from a text are identical ...

   <<functions>>=
   def index_of_coincidence(text): ...
   @
   ```
8. **Decompose long functions into named sub-chunks** — If a function has
   more than ~25 lines and contains two or more distinct algorithmic
   phases, decompose it into named sub-chunks.  Each sub-chunk name
   should read like a step in an algorithm description.  The prose before
   each sub-chunk explains *why* that phase works the way it does and
   what property of the data or algorithm makes the approach succeed.
   This is the classic Knuth technique.

   **BAD** — 80-line function with one line of prose:
   ```noweb
   We generate plaintext by concatenating sentences.

   <<functions>>=
   def generate_plaintext(size, *, sources, seed=None):
       """..."""
       if size <= 0:
           raise ValueError(...)
       paragraphs = extract_paragraphs(sources, ...)
       ...  # 75 more lines
       return normalize(prefix, options)
   @
   ```

   **GOOD** — function body decomposed into named sub-chunks with prose:
   ```noweb
   <<functions>>=
   def generate_plaintext(size, *, sources, seed=None):
       """..."""
       <<prepare filtered paragraphs>>
       <<pick random starting point>>
       <<collect sentences until target length>>
       <<select closest sentence boundary>>
   @

   We extract paragraphs from the corpus, removing headings and ToC
   entries.  Paragraphs lacking sentence-ending punctuation are
   discarded---they are typically list items or table rows.

   <<prepare filtered paragraphs>>=
   if size <= 0:
       raise ValueError("size must be positive")
   ...
   @

   To avoid always starting at the beginning of the corpus, we
   rotate to a random paragraph.

   <<pick random starting point>>=
   rng = random.Random(seed)
   ...
   @
   ```

9. **Decompose classes by method** — Introduce the class shell in one
   chunk with a placeholder like `<<repo methods>>`, then define each
   method in its own `\section` or `\subsection` with prose + method
   chunk + tests.  This is the class-level analogue of guideline 7
   (one function per chunk) and guideline 8 (decompose long functions).
   The class shell gives the reader the whole picture; the method
   sections fill in each part with full explanations and verification.

   **BAD** — entire class in one chunk:
   ```noweb
   \section{The Repository}

   <<classes>>=
   class Repo:
       def __init__(self, path):
           ...

       def save(self, data):
           ...

       def load(self, key):
           ...
   @

   \section{Tests}
   <<test functions>>=
   def test_save(): ...
   def test_load(): ...
   @
   ```

   **GOOD** — class shell + one section per method, tests distributed:
   ```noweb
   \section{The Repository}

   The class needs two operations: saving and loading.  We introduce
   the class shell here and fill in each method in its own section.

   <<classes>>=
   class Repo:
       def __init__(self, path):
           self.path = pathlib.Path(path)

       <<repo methods>>
   @

   \subsection{Saving data}

   We serialise to JSON because students can inspect the files
   manually, unlike a binary format.

   <<repo methods>>=
   def save(self, data):
       """Persist ``data`` to disk as JSON."""
       ...
   @

   Let's verify that saving round-trips correctly:

   <<test functions>>=
   def test_save_creates_file(tmp_path):
       repo = Repo(tmp_path)
       repo.save({"key": "value"})
       assert (tmp_path / "data.json").exists()
   @

   \subsection{Loading data}

   We return [[None]] for missing keys rather than raising, because
   a missing key is a normal condition during first run.

   <<repo methods>>=
   def load(self, key):
       """Load data for ``key``, or ``None`` if absent."""
       ...
   @

   <<test functions>>=
   def test_load_missing_returns_none(tmp_path):
       repo = Repo(tmp_path)
       assert repo.load("absent") is None
   @
   ```

   The chunk name `<<repo methods>>` is a **bucket chunk** scoped to
   the class: noweb concatenates all definitions, so each
   `<<repo methods>>=` adds another method to the class body.  Choose
   a name that reflects the class (e.g. `<<iolog methods>>`,
   `<<stream capture methods>>`).

   Apply the same pattern to test classes.  If `<<test functions>>=`
   introduces `class Test...:`, put only the class shell there and
   delegate the body to a class-specific bucket chunk such as
   `<<feature a test methods>>`.  Do not concatenate indented test
   methods directly into `<<test functions>>=`; nested scopes are
   clearer and less error-prone when they use their own bucket chunk.

10. **Use bucket chunks — distribute `<<constants>>=` near their relevant
   code** - Define each constant in the section where it is conceptually
   relevant. Never group all constants into a single `\subsection{Constants}`.

   **IMPORTANT**: When a constant exists only to support one helper or one
   small cluster of related helpers, place its `<<constants>>=` bucket
   immediately adjacent to the bucket that contains those helpers.  Do not
   hide configuration keys in one distant global block if the reader only
   needs them to understand one local section.

   **Preferred pattern** — prose, then helper bucket, then local constants
   bucket for that helper family:
   ```noweb
   We read the debug flag from configuration rather than the process
   environment so detached hooks and interactive commands see the same
   value.

   <<helper functions>>=
   def track_debug_enabled():
       return config.get(TRACK_DEBUG_CONFIG)
   <<constants>>=
   TRACK_DEBUG_CONFIG = "track.debug"
   @
   ```

   This keeps the constant close enough to the narrative that readers meet
   it when they need it, without forcing them to search a giant global
   constants block.

   **BAD** — all constants dumped in one subsection:
   ```noweb
   \subsection{Constants}

   <<constants>>=
   DATA_DIR = ...        % used in loading section
   GUTENBERG_START = ... % used in extraction section
   SENTENCE_RE = ...     % used in sentence splitting section
   KEEP_PUNCT = ...      % used in normalization section
   @
   ```

   **GOOD** — each constant near the code that uses it:
   ```noweb
   \subsection{Loading Texts}

   <<constants>>=
   DATA_DIR = Path(__file__).parent / "data"
   <<functions>>=
   def load_text(path): ...
   @

   \subsection{Extracting Body Text}

   <<constants>>=
   GUTENBERG_START = "*** START OF"
   GUTENBERG_END = "*** END OF"
   <<functions>>=
   def extract_body(text): ...
   @
   ```
11. **Co-locate wiring chunks with the entities they mutate, not the helpers
   they call.**  A wiring chunk (attribute assignment, `register()`/`install()`
   call, decorator-style mutation) has two natural neighbours: the helper
   functions it *calls* and the objects it *mutates*.  Place it next to the
   objects it mutates so a reader who lands on the option/class/registry
   sees what is attached to it; the helper has its own section and does
   not benefit from a trailing assignment block.  Chunk source order is
   independent of tangle order, so co-locating the source costs nothing
   at runtime.

   **BAD** — wiring sits next to the helper it calls, far from the option
   it mutates:
   ```noweb
   <<constants>>=
   LAYOUT_OPTION = typer.Option("slide", "--layout", help=LAYOUT_HELP)
   @

   ...300 lines later...

   <<functions>>=
   def _choice_completer(values): ...
   <<option completions>>=
   LAYOUT_OPTION.autocompletion = _choice_completer(LAYOUT_CHOICES)
   @
   ```

   **GOOD** — wiring sits next to the object it mutates; the helper moves
   to live near the same neighbourhood:
   ```noweb
   <<constants>>=
   LAYOUT_OPTION = typer.Option("slide", "--layout", help=LAYOUT_HELP)
   <<functions>>=
   def _choice_completer(values): ...
   <<option completions>>=
   LAYOUT_OPTION.autocompletion = _choice_completer(LAYOUT_CHOICES)
   @
   ```
12. **Define constants for magic numbers** - never hardcode values
13. **Co-locate dependencies with features** - feature's imports in feature's section
14. **Never leave prose inside an open code chunk** — When inserting local
    `<<constants>>=` buckets or explanatory paragraphs, first close the
    current code chunk with `@`.  Documentation between two function
    sections must be outside code mode; otherwise noweb tangles the prose
    into Python and produces syntax errors.

    **BAD** — prose accidentally tangled as Python:
    ```noweb
    <<helper functions>>=
    def get_default_daily_limit():
        ...

    This helper uses the daily-limit config key.

    <<constants>>=
    DEFAULT_DAILY_LIMIT_CONFIG = "track.daily_limit"
    @
    ```

    **GOOD** — close the code chunk before prose, then reopen a bucket:
    ```noweb
    <<helper functions>>=
    def get_default_daily_limit():
        ...
    @

    This helper uses the daily-limit config key.

    <<constants>>=
    DEFAULT_DAILY_LIMIT_CONFIG = "track.daily_limit"
    @
    ```

    Conversely, when a code chunk is immediately followed by *another code
    chunk* with no prose between them, omit the `@` — see "Don't Write `@`
    Between Adjacent Code Chunks" above.
15. **Prefer public functions** - Default to making functions public with
    docstrings. Only use `_`-prefixed private functions for true internal
    helpers tightly coupled to a single caller. Public utilities (e.g.,
    `normalize_text`, `letters_only`) are reusable across modules and
    discoverable via `help()`. Duplicated private helpers across modules
    (e.g., `_to_ascii` in both `vigenere.nw` and `plaintexts.nw`) are a
    sign the function should be public in a shared module.
16. **Keep lines under 80 characters** - both prose and code
17. **Survey siblings before introducing a new pattern.**  Before reaching
    for a new mechanism in a `.nw` file, grep the same file (and sibling
    `.nw` files) for places that already solve the same task.  If three
    command-local options already attach completion via `autocompletion=...`
    at construction, the fourth option should match — *or* the prose must
    explain why the divergence is necessary (forward-reference constraint,
    chunk-tangle order, dependency on a later-defined symbol, etc.).  The
    cost of this survey is one grep; the cost of skipping it is an
    asymmetric file where readers cannot tell whether the new mechanism is
    load-bearing or accidental.

### LaTeX Documentation Quality

Apply `latex-writing` skill. Most common anti-patterns in .nw files:

**Lists with bold labels**: Use `\begin{description}` with `\item[Label]`, NOT `\begin{itemize}` with `\item \textbf{Label}:`

**Code with manual escaping**: Use `[[code]]`, NOT `\texttt{...\_...}`

**Manual quotes**: Use `\enquote{...}`, NOT `"..."` or `` ``...'' ``

**Manual cross-references**: Use `\cref{...}`, NOT `Section~\ref{...}`

**TikZ without preamble support**: If a `.nw` file introduces a TikZ
diagram, add `\usepackage{tikz}` to the project's `preamble.tex`.

**Non-ASCII bytes in code chunks weave into the `.tex`**: `noweave` copies
code chunks *verbatim*, so any non-ASCII character inside a chunk — a
box-drawing diagram in a test fixture, a Unicode normalization table, fancy
quotes — lands in the woven LaTeX and must be typeset by the engine.  How that
behaves is **engine-dependent**: under pdfLaTeX an unmapped byte is a fatal
`! LaTeX Error: Unicode character … (U+XXXX) not set up` (at the woven line);
under XeLaTeX/LuaLaTeX it is at worst a non-fatal `Missing character` warning.
Check the build engine first — a literate project's build rules are often
tangled from a `.nw` (e.g. `tex.mk`), so a `make`/submodule update can flip
`latexmk -pdf` to `-xelatex` and change which fix is correct.

Fix it in the project's `preamble.tex`, **not** by deleting or escaping the
byte in the `.nw` — the tangled program usually needs the real character at
runtime (the test that asserts an ASCII-art figure is filtered, the table that
maps real typographic punctuation).  Before touching any non-ASCII byte in a
code chunk, confirm whether the generated code depends on it.  The preamble fix
differs per engine (`\DeclareUnicodeCharacter` under pdfLaTeX —
defined via `\usepackage[utf8]{inputenc}`; `\newunicodechar` under
XeLaTeX/LuaLaTeX; guard with `iftex`).  See the `latex-writing` skill's
`references/unicode-and-fonts.md` for the full engine matrix, the
T1-`fontenc` requirement for pdfLaTeX monospace fonts like Bera Mono, and the
`pdffonts`/`pdftotext` diagnostics.

## Progressive Disclosure Pattern

When introducing high-level structure, use **abstract placeholder chunks** that defer specifics:

```noweb
def cli_show(user_regex,
             <<options for filtering>>):
  <<implementation>>
@

[... later, explain each option ...]

\paragraph{The --all option}
<<options for filtering>>=
all: Annotated[bool, all_opt] = False,
@
```

Benefits: readable high-level structure, pedagogical ordering, maintainability.

The same technique applies to **function bodies**: long functions can use
`<<phase name>>` sub-chunks to present algorithmic steps in pedagogical
order with prose between them (see Writing Guideline 8, "Decompose long
functions").

## Chunk Concatenation Patterns

**Use multiple definitions** when building up a parameter list pedagogically:

```noweb
\subsection{Adding the diff flag}
<<args for diff>>=
diff=args.diff,
@

[... later ...]

\subsection{Fine-tuning thresholds}
<<args for diff>>=
threshold=args.threshold
@
```

**Use separate chunks** when contexts differ (different scopes):

```noweb
<<args from command line>>=  # Has args object
diff=args.diff,
@

<<params for recursion>>=    # No args, only parameters
diff=diff,
@
```

## Chunk Dependency Hazards

When a chunk references a variable defined in another chunk, there is an
**implicit dependency** between them. Unlike function calls, noweb does not
enforce that prerequisite chunks are included — the compiler only sees the
tangled output. This makes it easy to reuse a chunk in a new code path
while accidentally omitting the chunk that defines a variable it needs.

**Rule: When reusing a chunk in a new code path, verify that all variables
it references are defined by preceding chunks in that path.**

**BAD** — chunk B depends on a variable set in chunk A, but a new path
omits A:

```noweb
<<path one>>=
<<chunk A>>
<<chunk B>>
@

<<path two>>=
<<chunk B>>      % ← UnboundLocalError: variable from A missing
@
```

**GOOD** — either include the prerequisite or document the dependency:

```noweb
<<path two>>=
<<chunk A>>
<<chunk B>>
@
```

**Tip**: If a chunk both defines variables AND performs side effects that
are not always wanted, consider splitting it so the variable-defining part
can be included independently.

**Design rule**: Prefer extracting shared logic into a **function** rather
than a reusable chunk when the logic is used across multiple code paths.
Functions make dependencies explicit through parameters — a missing
argument is a compile-time error, while a missing prerequisite chunk is
only caught at runtime. Reserve chunks for pedagogical decomposition
(presenting code in narrative order); use functions for operational
decomposition (sharing logic between code paths).

## Test Organization

**CRITICAL**: Tests MUST appear AFTER implementation, distributed throughout
the file near the code they verify. **NEVER** create a `\section{Tests}` or
`\section{Unit Tests}` that groups all tests at the end of the file.

See `references/testing-patterns.md` for detailed patterns.

Key rules:
- Each implementation section is followed by its `<<test functions>>=` chunk
- Use single `<<test functions>>` chunk name — noweb concatenates them
- If `<<test functions>>=` introduces a test class, treat it as the class
  shell and accumulate methods in a class-specific bucket chunk such as
  `<<feature a test methods>>`
- Use `from module import *` in the test file header
- Frame tests pedagogically: "Let's verify this works..."

**BAD** — all tests collected at the end:
```noweb
\section{Encryption}
<<functions>>=
def encrypt(text, key): ...
@

\section{Decryption}
<<functions>>=
def decrypt(text, key): ...
@

\section{Tests}          % ← NEVER do this

<<test functions>>=
def test_encrypt(): ...
def test_decrypt(): ...
@
```

**GOOD** — each test immediately after its implementation:
```noweb
\section{Encryption}
<<functions>>=
def encrypt(text, key): ...
@

Let's verify that encryption produces the expected ciphertext:

<<test functions>>=
def test_encrypt(): ...
@

\section{Decryption}
<<functions>>=
def decrypt(text, key): ...
@

We can verify that decryption inverts encryption:

<<test functions>>=
def test_decrypt(): ...
@
```

If a test section needs a test class, introduce the class in
`<<test functions>>=` and collect its methods in a class-specific
bucket chunk rather than concatenating indented methods directly into
`<<test functions>>=`.  See `references/testing-patterns.md` for a
worked example and anti-pattern.

## Multi-Directory Projects

For large projects (5+ .nw files), see `references/multi-directory-projects.md`.

Key structure:
```
project/
├── Makefile       # Root orchestrator (compile → test → docs)
├── pyproject.toml # Poetry packaging configuration
├── src/           # .nw files → .py + .tex
├── doc/           # Document wrapper (.nw), preamble.tex
├── tests/         # Extracted test files (unit/ subdir)
└── makefiles/     # Shared build rules (noweb.mk, subdir.mk)
```

### Initializing a New Project

See `references/project-initialization.md` for full details. Quick checklist:

1. Create `pyproject.toml` with `[tool.poetry]` packages/include/exclude
2. Create `src/.gitignore` (`*.py`, `*.tex`) and `tests/.gitignore` (`*.py`)
3. Create `src/packagename/Makefile` with explicit `__init__.py` rule
4. Create `src/packagename/packagename.nw` with `<<[[__init__.py]]>>` and
   `<<test [[packagename.py]]>>` chunks
5. Create `tests/Makefile` with auto-discovery (uses `%20` encoding, `cpif`,
   `unit/` subdirectory)
6. Create `doc/packagename.nw` wrapper, `doc/Makefile`, `doc/preamble.tex`
7. Create root `Makefile` orchestrating compile → test → docs

### LaTeX-Safe Chunk Names

Use `[[...]]` notation for Python chunks with underscores:

```noweb
<<[[module_name.py]]>>=
def my_function():
    pass
@
```

Extract with: `notangle -R"[[module_name.py]]" file.nw > module_name.py`

### Filename Chunk Names Drive Language Inference

Naming root chunks exactly like their output filenames is load-bearing,
not just a convention: the `autolang` and `tominted` filters infer each
chunk's language from filename-like names — Python for
`<<[[fib.py]]>>`, Make for `<<[[Makefile]]>>` — and chunks whose names
are not filenames (`<<functions>>`, `<<test functions>>`) inherit the
language of the chunks that use them.  This is what lets one `.nw` file
mix languages (a program plus its Makefile) while each chunk is
highlighted by its own lexer and the identifier index stays free of
foreign identifiers.  See `references/noweb-commands.md` for the
inference rules and `.ext=lexer` / `name=lexer` mapping overrides.

## Best Practices Summary

1. **Write documentation first** - then add code
2. **Keep lines under 80 characters**
3. **Check for unused chunks** - run `noroots` to find typos
4. **Keep tangled code in .gitignore** - .nw is source of truth
5. **NEVER commit generated files** - .py and .tex from .nw are build artifacts
6. **Test your tangles** - ensure extracted code runs
7. **Require PEP-257 docstrings on all public functions** - Prose in `.nw`
   is for **maintainers** reading the literate source; docstrings are for
   **users** of the compiled `.py` who never see the `.nw` file. Both are
   needed. Private functions (prefixed `_`) may omit docstrings. Never use
   `\cref` or other LaTeX commands inside docstrings — and never use noweb
   `[[...]]` code-quoting there either. `[[...]]` is only interpreted by
   noweave in *documentation* chunks; inside a docstring (a string in a code
   chunk) it is copied verbatim, so it leaks into the generated `.py` and
   `help()` output. Quote code in docstrings however your project's
   docstrings already do (plain text, markdown `` `x` ``, or RST
   `` ``x`` ``) — just not with `[[...]]`.

   Chunk *references* (`<<...>>`) inside docstrings are fine: the
   standard weave's custom lexer (`tominted -lexer noweb_lexer.py`)
   keeps them hyperlinked in the woven PDF even though they sit inside
   a Python string literal.

   **BAD** — noweb `[[...]]` in a docstring leaks into `help()`:
   ```noweb
   <<functions>>=
   def __setattr__(self, name, value):
       """Keep [[labels]] a sorted, duplicate-free list."""
       ...
   @
   ```

   **GOOD** — quote code with the project's docstring convention:
   ```noweb
   <<functions>>=
   def __setattr__(self, name, value):
       """Keep `labels` a sorted, duplicate-free list."""
       ...
   @
   ```

   **BAD** — function with prose but no docstring:
   ```noweb
   We convert text to lowercase ASCII for uniform comparison.

   <<functions>>=
   def normalize_text(text):
       return text.lower().encode("ascii", "ignore").decode()
   @
   ```

   **GOOD** — prose for maintainers AND docstring for users:
   ```noweb
   We convert text to lowercase ASCII for uniform comparison.

   <<functions>>=
   def normalize_text(text):
       """Return lowercase ASCII version of ``text``.

       Non-ASCII characters are silently dropped.
       """
       return text.lower().encode("ascii", "ignore").decode()
   @
   ```
8. **Keep the maps in sync** - When a change affects structure, flow, entry
   points, chunk grouping, or likely edit locations, update the overview,
   local intro prose, roadmap diagrams, and any relevant `README.md` in the
   same change
9. **Include table of contents** - add `\tableofcontents` in documentation

## Git Workflow

See `references/git-workflow.md` for details.

**Core rules:**
- Only commit .nw files to git
- Add generated files to .gitignore immediately
- Regenerate code with `make` after checkout/pull
- Never commit generated .py or .tex files

## Noweb Commands Quick Reference

See `references/noweb-commands.md` for details, including the one-time
custom-lexer setup the standard weave below depends on.

```bash
# Tangling
notangle -R"[[module.py]]" file.nw > module.py
notangle -t8 -R"[[Makefile]]" file.nw > Makefile  # -t8 keeps tabs
noroots file.nw                              # List root chunks

# Weaving (standard recipe: highlighted with minted, clean index)
# For inclusion; the master preamble loads minted via \usepackage[minted]{noweb}
noweave -n -delay -autolang -autodefs python3 -autodefs sh \
    -autodefs make -index \
    -filter 'tominted -lexer noweb_lexer.py' file.nw > file.tex
# compile with -shell-escape (pdflatex -shell-escape or latexmk option)
# Standalone (noweave writes the preamble): add -minted so it loads minted
noweave -autolang -autodefs python3 -autodefs sh -autodefs make \
    -index -minted file.nw > file.tex

# Classic fallback (no minted/patched noweb; identifier uses inside
# code stay hyperlinked, at the price of no syntax highlighting)
noweave -n -delay -x -t2 file.nw > file.tex  # For inclusion
noweave -latex -x file.nw > file.tex         # Standalone
```

Pipeline rules baked into the standard recipe: `-autolang` always runs
first no matter where it appears on the command line; `tominted` must
be the *last* filter, after `-index`.  `tominted` is LaTeX-only —
never combine it with `-html`.

Stacking several `-autodefs` works because `-autolang`'s `@language`
annotations gate each filter to its own chunks.  Available filters:
`python3`, `sh`/`bash`, `make`, `haskell`, `rust`, `java`, `c`
(ANSI C chunks only), `cpp` (C++ chunks: classes, templates,
namespaces, qualified methods), plus the classic
`icon`/`sml`/`tex`/`yacc`/etc. — run `noweave -showautodefs` for the
installed list.  Filter budget: the dbosk fork's pipeline is unbounded
— it accumulates filters in a single variable and joins them with `|`,
so any number of `-autodefs` filters can stack alongside `-autolang`,
`-index` (which inserts two filters, `finduses` and `noidx`) and
`tominted` in one weave.  A six-language document is one pass, not two.
(Stock and pre-fork noweave enumerated only seven filter slots, a
portability artifact of the array-less `/bin/sh` pipeline builder; that
ceiling — three `-autodefs` for a highlighted indexed weave, four for a
classic one — applies only if you run against an older noweave, in
which case split the languages across a second weave; see the
`multilang` example in noweb's `examples/`.)

Never quote an *indexed* identifier with `[[...]]` inside a
`\section{...}`/`\subsection{...}` heading: `-index` turns the quote
into a hyperlinked identifier use, and hyperref breaks on links in
moving arguments.  Use `\texttt{...}` in headings; keep `[[...]]` in
body prose.

## When Literate Programming Is Valuable

- Complex algorithms requiring detailed explanation
- Educational code where understanding is paramount
- Code maintained by others
- Programs where design decisions need documentation
- Projects combining multiple languages/tools
