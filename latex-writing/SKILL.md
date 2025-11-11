---
name: latex-writing
description: Guide LaTeX document authoring following best practices and proper semantic markup. Use proactively when: (1) writing or editing .tex files, (2) creating LaTeX content in .nw literate programming files, (3) user mentions LaTeX, BibTeX, or document formatting, (4) reviewing LaTeX code quality. Ensures proper use of semantic environments like description vs itemize.
---

# LaTeX Writing Best Practices

This skill guides the creation of well-structured, semantically correct LaTeX documents following established best practices.

## Core Principle: Semantic Markup

Use LaTeX environments that match the semantic meaning of the content, not just the visual appearance.

## List Environments: When to Use What

### Use `description` for Term-Definition Pairs

When you have labels followed by explanations, definitions, or descriptions, use the `description` environment:

```latex
\begin{description}
\item[Term] Definition or explanation of the term
\item[Label] Content associated with the label
\item[Property] Description of the property
\end{description}
```

**NEVER do this:**
```latex
\begin{itemize}
\item \textbf{Term:} Definition or explanation
\item \textbf{Label:} Content associated with label
\end{itemize}
```

### Common Use Cases for `description`

- **API parameters**: `\item[username] The user's login name`
- **Configuration options**: `\item[timeout] Maximum wait time in seconds`
- **Glossary entries**: `\item[LaTeX] A document preparation system`
- **Passes/Fails examples**: `\item[Passes] Correct implementation...`
- **Feature descriptions**: `\item[Auto-save] Automatically saves every 5 minutes`

### Use `itemize` for Simple Lists

Use `itemize` when items are uniform list elements without labels:

```latex
\begin{itemize}
\item First uniform item
\item Second uniform item
\item Third uniform item
\end{itemize}
```

### Use `enumerate` for Numbered Steps or Rankings

Use `enumerate` when order matters:

```latex
\begin{enumerate}
\item First step in the process
\item Second step in the process
\item Third step in the process
\end{enumerate}
```

## Recognition Patterns

When reviewing or writing LaTeX, look for these patterns that indicate `description` should be used:

- `\item \textbf{SomeLabel:}` → Should use `\item[SomeLabel]`
- `\item \emph{SomeLabel:}` → Should use `\item[SomeLabel]`
- `\item SomeLabel ---` → Should use `\item[SomeLabel]`
- Lists where every item starts with bold/emphasized text

## Fixing Common Anti-Patterns

### Anti-Pattern: Bold Labels in Itemize
```latex
% INCORRECT
\begin{itemize}
\item \textbf{Passes:} \verb|\documentclass{article}|
\item \textbf{Fails:} No documentclass declaration
\end{itemize}
```

### Correct: Description Environment
```latex
% CORRECT
\begin{description}
\item[Passes] \verb|\documentclass{article}|
\item[Fails] No documentclass declaration
\end{description}
```

### Anti-Pattern: Manual Formatting Instead of Semantic Structure
```latex
% INCORRECT
\noindent\textbf{Configuration:} Set timeout to 30 seconds.\\
\textbf{Performance:} Optimized for large datasets.
```

### Correct: Semantic Description
```latex
% CORRECT
\begin{description}
\item[Configuration] Set timeout to 30 seconds
\item[Performance] Optimized for large datasets
\end{description}
```

## Additional Best Practices

### Cross-References
- Use `\label` and `\ref` instead of hard-coded numbers
- Labels should be descriptive: `\label{sec:introduction}` not `\label{s1}`

### Citations
- Use proper citation commands (`\cite`, `\citep`, `\citet`) not manual references
- Never write `[1]` or `(Smith 2020)` manually

### Quotations (csquotes package)
- **Always** use `\enquote{...}` for quotes, never manual quote marks
- Handles nested quotes automatically: `\enquote{outer \enquote{inner} quote}`
- Language-aware: Swedish uses »...« or "...", English uses "..." or '...'
- For block quotes, use `\begin{displayquote}...\end{displayquote}`

**Anti-pattern**: Manual quotes
```latex
% INCORRECT
"This is a quote"
``This is a quote''
'single quotes'
```

**Correct**: Use csquotes
```latex
% CORRECT
\enquote{This is a quote}
\enquote{outer \enquote{inner} quote}
```

**Why**: Manual quote marks don't adapt to language settings and can cause typographical inconsistencies. The csquotes package handles all quote styling correctly based on document language.

### Emphasis
- **Never** use ALL CAPITALS for emphasis in running text
- Use `\emph{...}` to emphasize words or phrases
- For strong emphasis, use `\textbf{...}` or nested `\emph{\emph{...}}`
- Let LaTeX handle the typographic styling

**Anti-pattern**: ALL CAPITALS for emphasis
```latex
% INCORRECT
This is VERY important to understand.
We must do this NOW before moving forward.
The BENEFITS of classes are clear.
```

**Correct**: Semantic emphasis
```latex
% CORRECT
This is \emph{very} important to understand.
We must do this \emph{now} before moving forward.
The \emph{benefits} of classes are clear.
```

**Why**: ALL CAPITALS in running text is considered shouting and poor typography. It's harder to read and looks unprofessional. Use `\emph{...}` to provide semantic emphasis, and LaTeX will render it appropriately (typically as italics, but this can be configured based on context and document style).

**Exception**: Acronyms and proper names that are conventionally written in capitals (e.g., NASA, USA, PDF) are fine and should not be emphasized.

### Floats
- Use `figure` and `table` environments with `\caption` and `\label`
- Remember the principle: an image is not a figure, but a figure can contain an image

### Verbatim and Code
- Use `listings` package for code with syntax highlighting
- Use `\verb` for inline code snippets
- Never paste code as normal text

### Paths
- Always use forward slashes in paths: `figures/diagram.pdf` not `figures\diagram.pdf`
- Use platform-independent path specifications

## Workflow for Writing LaTeX

When writing or editing LaTeX content:

1. **Identify content structure**: Is this a list of uniform items or term-definition pairs?
2. **Choose semantic environment**: Match the environment to the content meaning
3. **Use proper commands**: Leverage LaTeX's semantic commands rather than manual formatting
4. **Verify cross-references**: Ensure labels and references are descriptive and correct
5. **Check for anti-patterns**: Review for `\textbf{Label:}` in itemize environments

## When Reviewing LaTeX Code

Check for these common issues:
- [ ] Lists using `\textbf{Label:}` instead of `description` environment
- [ ] Hard-coded numbers instead of `\ref`
- [ ] Manual citation formatting instead of `\cite` commands
- [ ] Manual quotes (`"..."`, `'...'`, `` `...` ``) instead of `\enquote{...}`
- [ ] Images without `figure` environment
- [ ] Code without proper formatting (listings/verbatim)
- [ ] Windows-style backslashes in paths

## Remember

LaTeX is a **document preparation system** based on **semantic markup**, not a word processor. The goal is to describe what content *is*, not how it should *look*. Let LaTeX handle the formatting based on the semantic structure you provide.
