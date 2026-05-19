# Overview Patterns

Use these patterns when a maintainer-oriented `.nw` file needs to show the
whole before the parts.

## Audience Default

Assume a technically competent maintainer:

- Knows the programming language and common tooling
- Does not yet know this codebase's structure
- Needs project-specific orientation, invariants, boundaries, and likely
  change points

Do not spend the overview teaching language basics. Spend it showing how this
particular system hangs together.

## What A Good Overview Must Cover

For any non-trivial `.nw` file, cover these points early:

1. **Purpose**: What problem this document or module solves.
2. **Main parts**: The major components, phases, or chunk groups.
3. **Relationships**: How those parts depend on or feed into each other.
4. **Roadmap**: Where the document goes next.
5. **Likely edits**: Which sections a maintainer will probably revisit when
   changing behavior.

The overview should reduce the reader's need to build a mental map from later
details.

## When Prose Is Enough

Use prose alone when the structure is short and mostly linear:

- one main flow
- few moving parts
- dependencies that can be described in one paragraph
- no risk that the reader loses track of names or boundaries

## When To Add A Diagram

Add a diagram when relationships are hard to keep in working memory from prose
alone, especially when the file has:

- multiple subsystems or layers
- non-linear control flow or data flow
- bucket chunks that gather material from distant sections
- tests distributed across the file
- a public API, internal helpers, and generated outputs that interact in
  different directions

Diagrams are optional. Use one when it clarifies structure, not as decoration.

## Diagram Rules

Keep structural diagrams simple:

1. Show one main point per figure.
2. Reuse the same names as the code, chunks, or sections.
3. Prefer short labels and directional arrows.
4. Add a caption and label, then refer to it with `\cref{...}`.
5. Explain the figure's relevance in surrounding prose.

If using TikZ, remember to add `\usepackage{tikz}` to the project's
`preamble.tex`. The shared skill reference preamble is only a template, not a
guarantee that an existing project already loads TikZ.

## Overview Patterns

### Module Or Component Map

Use when the reader must quickly see the major pieces and their dependencies.

```latex
\chapter{Overview}

This module turns CLI requests into normalized work items and then dispatches
them to backend-specific handlers. Most changes land in one of three places:
argument parsing, request normalization, or backend dispatch.

\begin{description}
\item[Entry points] Parse user intent and collect options.
\item[Normalization] Convert raw flags into a stable internal request shape.
\item[Dispatch] Route normalized requests to the appropriate backend.
\end{description}

The rest of this file follows that same path: first entry points, then
normalization, then dispatch and error handling.
```

Add a diagram if the subsystems are numerous or cross-linked.

### Pipeline View

Use when the important thing is staged transformation.

```latex
\section{Code overview}

The implementation has a three-stage pipeline:
\begin{description}
\item[Collect] Read configuration and command-line options.
\item[Derive] Compute the effective settings and validate invariants.
\item[Apply] Execute the chosen action and report the result.
\end{description}

Each top-level chunk in [[__init__.py]] corresponds to one of these stages.
```

### Chunk Or Bucket Relationship Map

Use when bucket chunks collect material from far-apart sections.

Explain which high-level chunk acts as the assembly point, then show which
later sections append to it. This is especially useful when noweb
concatenation is central to the design.

```latex
The top-level [[__init__.py]] chunk assembles imports, constants, classes, and
functions. Later sections fill those buckets incrementally, so the reader can
study each concern in isolation before seeing the complete output chunk again.
```

Add a diagram if the bucket structure branches widely.

### Test Roadmap

Use when tests are intentionally distributed after the implementation they
verify.

```latex
\subsection{Test roadmap}

Tests are distributed through the file rather than collected in one section.
Parsing tests follow the parser implementation, normalization tests follow the
request-shaping logic, and integration tests appear after all dispatch paths
are in place.
```

For a fuller pattern, see `references/testing-patterns.md`.

## Minimal TikZ Example

Use TikZ only when a small structural picture is clearer than prose.

```latex
\begin{figure}
\centering
\begin{tikzpicture}[node distance=2.8cm, >=stealth]
  \node (cli) [draw, rounded corners] {CLI entry points};
  \node (norm) [draw, rounded corners, right of=cli] {Normalization};
  \node (dispatch) [draw, rounded corners, right of=norm] {Dispatch};

  \draw[->] (cli) -- (norm);
  \draw[->] (norm) -- (dispatch);
\end{tikzpicture}
\caption{High-level flow from user input to backend execution.}
\label{fig:cli-flow}
\end{figure}
```

Remember to add `\usepackage{tikz}` to `preamble.tex` before introducing this
kind of figure.
