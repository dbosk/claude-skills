---
name: didactic-notes
description: |
  Document pedagogical design decisions in educational materials using the
  didactic LaTeX package and \ltnote command. Use proactively when (1) writing
  or editing educational LaTeX materials with pedagogical content, (2) adding
  or revising variation-theory annotations such as "What varies" or "What
  stays invariant", (3) explaining design trade-offs or choices in educational
  materials, (4) documenting why specific examples or exercises are sequenced
  in a particular way, or (5) moving pedagogical reasoning out of
  student-facing prose and into instructor notes. Invoke when user mentions
  didactic notes, \ltnote, pedagogical reasoning, learning theory notes,
  educational design documentation, or asks to move pedagogical reasoning to
  instructor notes. CRITICAL: \ltnote captures reasoning about how the teaching
  material itself is written and sequenced (variation/invariance labels, why
  this example, what a question should reveal), NOT substantive content or
  system/code design decisions, which belong in the body text even when they
  cite research.
---

# Didactic Notes: Literate Pedagogy

This skill documents pedagogical design decisions in educational materials, analogous to how literate programming documents code design decisions.

## Reference Files

This skill includes detailed references in `references/`:

| File | Content | Search patterns |
|------|---------|-----------------|
| `latex-examples.md` | Restatable LOs, citations, complete examples | `restatable`, `\cref{}`, `biblatex` |
| `beamer-patterns.md` | Mode splits, overlays, verbose environments | `\mode<article>`, `uncoverenv`, `\textbytext` |
| `semantic-environments.md` | Environment selection, generalizations | `definition`, `remark`, `example`, `block` |

## Core Principle

**Document not just what you teach, but *why* you teach it that way.**

Just as literate programming makes code reasoning explicit, didactic notes make pedagogical reasoning explicit using `\ltnote{...}` from the LaTeX `didactic` package.

## Scope: `\ltnote` documents the *material's* design, not the subject

`\ltnote` is meta-commentary about **how and why the teaching text itself is
written** — which example was chosen, the order of presentation, a
variation/invariance pattern, what a question is meant to reveal. It is the
authorial reasoning that a reader of the finished material should not see, but a
future *author* or *educator* should.

It is **not** a place for substantive content about the subject being taught or
the system being documented — including design decisions and the references that
justify them. Those are part of the material and belong in the **body text**,
even when the justification cites learning-science literature.

**The test:** if the note explains a choice about *the writing*, it is an
`\ltnote`. If it states *how the thing being described works* (or why it was
built that way), it is body text.

### Example: a literate program (`.nw`)

A literate program's prose is maintainer-facing documentation of the **code**, so
a design decision about the code — even one grounded in pedagogy research — is
content, and it (with its citations) goes in the narrative:

```latex
% BODY TEXT (correct) — a design decision and the evidence for it:
The map carries no subject; subject rides on the entities a room holds, so one
labyrinth can interleave subjects rather than trap a learner in a single one.
Interleaving aids retention by spacing repeated
encounters~\autocite{taylor2010interleaved,cepeda2006distributed}.

% \ltnote (correct) — reasoning about the writing itself:
\ltnote{%
  Introduced before the maze chapter so the reader meets ``no subject'' while
  the data model is still fresh; the interleaving payoff is only sketched here
  and developed where placement is implemented.
}
```

Putting the citation-bearing design rationale *inside* the `\ltnote` is the
common mistake: it is content, not a note about the writing. It is also fragile
— `\ltnote` expands to a `\marginpar`, and biblatex `\autocite` inside a margin
float can fail with ``Float(s) lost''. Keep substantive citations in the body.

## Quick Example

**Without didactic notes:**
```latex
\begin{activity}\label{PredictOutput}
  What do you think this function returns?
\end{activity}
```

**With didactic notes:**
```latex
\begin{activity}\label{PredictOutput}
  What do you think this function returns?
\end{activity}

\ltnote{%
  Following try-first pedagogy, we ask students to predict before
  explaining. This creates contrast between their mental model and
  the actual behavior, helping them discern the critical aspect.
}
```

### Anti-pattern: visible variation labels

Pedagogical labels such as \enquote{What varies} and \enquote{What stays
invariant} belong in notes, not in the student-facing body text.

**Bad:**
```latex
These two examples form a deliberate contrast.

\begin{description}
\item[What varies] Whether [[base_url]] is passed explicitly.
\item[What stays invariant] The helper, the question, and the layout.
\end{description}
```

**Good:**
```latex
\ltnote{%
  \textbf{Variation pattern}: Contrast
  \textbf{What varies}: Whether [[base_url]] is passed explicitly.
  \textbf{What stays invariant}: The helper, the question, and the layout.
}
```

## The `didactic` Package

### Package Setup

```latex
\usepackage[marginparmargin=outer]{didactic}
```

Options:
- `marginparmargin=outer` - Place margin notes on outer margins
- `inner=20mm`, `outer=60mm` - Set margin widths
- `notheorems` - Disable automatic theorem environments

### The `\ltnote` Command

Creates margin notes documenting pedagogical rationale:

```latex
\ltnote{%
  We want to investigate what people think literate programming is.
  This will help us understand the correctness of their prior knowledge.
}
```

## Learning Objectives with Restatable

Use `restatable` environment for learning objectives that can be referenced throughout:

```latex
\begin{restatable}{lo}{FilesLOPersistence}\label{FilesLOPersistence}%
  Förklara skillnaden mellan primärminne och sekundärminne.
\end{restatable}
```

**Key points:**
- Use **mnemonic labels** (e.g., `FilesLOPersistence`, not `FilesLO1`)
- Add `\label{MnemonicLabel}` for `\cref{}` support
- The `%` after opening brace prevents unwanted whitespace

### Referencing LOs

**Method 1: `\cref{}`** (Recommended for detailed notes):
```latex
\ltnote{%
  Relevanta lärandemål:
  \cref{FilesLOPersistence}

  \textbf{Kritiska aspekter för} \cref{FilesLOPersistence}:
  \begin{itemize}
    \item \textbf{Persistens}: Data överlever avstängning
  \end{itemize}
}
```

**Method 2: Starred commands** (Compact):
```latex
\ltnote{%
  Relevanta lärandemål:
  \FilesLOPersistence*

  \textbf{Kontrast}: Typ av minne (primär vs sekundär).
}
```

**CRITICAL**: LO commands cannot be inside `\begin{itemize}` or other list environments.

## When to Use `\ltnote`

Document:

1. **Learning objectives addressed**: Reference with `\cref{}` or starred commands
2. **Pedagogical strategies**: "We use try-first pedagogy to activate prior knowledge"
3. **Variation theory patterns**: Contrast, generalization, fusion
4. **Critical aspects students should discern**
5. **Design trade-offs about the *material***: which example, what order, how to
   phrase it — *not* design decisions about the system or subject being
   documented, which belong in the body text (see Scope above)
6. **Assessment purposes**: "This question gauges prior knowledge"
7. **Mentipy question intent**: What a live poll, QR question, or open-text prompt should reveal
8. **Future improvements**: Notes for refining material

When using Mentipy in slides or handouts, document why that question appears
at that moment, what responses are expected to reveal, and how the result will
shape the explanation or discussion that follows.

## Writing Effective Notes

### CRITICAL: Connect to Learning Objectives

Variation patterns must be tied to specific learning objectives:

```latex
\ltnote{%
  Relevanta lärandemål:
  \cref{FilesLOPersistence}

  \textbf{Variationsmönster}: Kontrast

  \textbf{Vad som varierar}: Typ av minne (primär vs sekundär)
  \textbf{Vad som hålls invariant}: Behovet att lagra data

  \textbf{Kritiska aspekter för} \cref{FilesLOPersistence}:
  \begin{itemize}
    \item \textbf{Persistens}: Studenten måste urskilja att filer
      löser problemet med datapersistens.
  \end{itemize}
}
```

### Structure Your Notes

1. **State learning objectives**: What should students learn?
2. **Reference theory**: Connect to established learning principles
3. **Explain the mechanism**: How does this design support objectives?
4. **Note alternatives**: What else could work?

### Language Consistency

**CRITICAL**: Match the language of `\ltnote` content to the surrounding document.

```latex
% Good - Swedish document with Swedish notes
\ltnote{%
  \textbf{Variationsmönster}: Kontrast
  Vi varierar operationen medan vi håller mönstret invariant.
}

% Use \foreignlanguage for English terms without translation
\ltnote{%
  Vi använder \foreignlanguage{english}{try-first pedagogy} här...
}
```

### Choosing Between Detailed and Compact Notes

**Use detailed notes with `\cref{}`** when:
- Writing comprehensive annotations
- Explaining multiple critical aspects
- Need prose-style integration

**Use compact notes with starred commands** when:
- Space is limited
- Quick overview needed
- Simple annotations suffice

## Citing Pedagogical Research

Cite in an `\ltnote` only when the citation justifies an **authoring or teaching
choice** — why this sequence, why try-first here. Use biblatex commands rather
than hardcoded references:

```latex
\ltnote{%
  Following \textcite{MartonPang2006}, we vary the operation while holding the
  pattern invariant, so learners can discern it.
}
```

Common commands:
- `\textcite{key}` → "Marton and Pang (2006)"
- `\parencite{key}` → "(Marton and Pang 2006)"

If the citation instead supports a **claim in the material** or a **design
decision about the subject/system** being documented, cite it in the **body
text**, not the note (see Scope above). There is also a technical reason to keep
heavy citations out of notes: `\ltnote` is a `\marginpar`, and biblatex
`\autocite`/`\textcite` inside a margin float can fail with ``Float(s) lost''.

**Best practice**: Use a separate `ltnotes.bib` for pedagogical references when
the project keeps them apart; otherwise add them to the project's main `.bib`.

## Integration with Learning Theories

### Variation Theory

Document how material creates patterns of variation:

```latex
\ltnote{%
  \textbf{Mönster}: Generalisering
  \textbf{Varierar}: Programmeringsspråk (Python vs Java)
  \textbf{Invariant}: Algoritmisk princip
}
```

### Try-First Pedagogy

Explain when and why you ask students to attempt before explaining:

```latex
\ltnote{%
  Following try-first pedagogy, we ask students to predict the output
  before running the code. This creates a knowledge gap that makes the
  subsequent explanation more meaningful.
}
```

### Cognitive Load Theory

Note considerations about cognitive load:

```latex
\ltnote{%
  We introduce only two parameters here to manage cognitive load.
  Additional parameters will be introduced after students master the
  basic pattern.
}
```

## Semantic Environments

See `references/semantic-environments.md` for details.

Key environments: `activity`, `exercise`, `question`, `remark`, `definition`, `example`, `block`

### Generalizations After Examples

Capture generalizations in semantic environments AFTER examples:

```latex
\begin{example}[Läsa fil]
  with open("data.txt", "r") as fil:
      innehåll = fil.read()
\end{example}

\begin{example}[Skriva fil]
  with open("data.txt", "w") as fil:
      fil.write(text)
\end{example}

\begin{remark}[Filhanteringsmönster]
  All filhantering följer: öppna → bearbeta → stäng.
\end{remark}
```

## Beamer Patterns

See `references/beamer-patterns.md` for details.

### Key Points

- Notes are hidden by default in slide builds
- Write expanded prose outside `frame` environments
- Use `\only<article>` / `\only<presentation>` for mixed content
- `\textbytext*` does NOT work inside frames—use mode splits

### Side-by-Side Contrast (Beamer-compatible)

```latex
\begin{frame}
  \mode<presentation>{%
    \textbytext{%
      \begin{definition}[Primärminne]
        Flyktigt minne med snabb åtkomst.
      \end{definition}
    }{%
      \begin{definition}[Sekundärminne]
        Oflyktigt minne, långsammare.
      \end{definition}
    }
  }
  \mode<article>{%
    \textbytext*{%
      \begin{definition}[Primärminne]
        Flyktigt minne med snabb åtkomst.
      \end{definition}
    }{%
      \begin{definition}[Sekundärminne]
        Oflyktigt minne, långsammare.
      \end{definition}
    }
  }
\end{frame}
```

### Verbose Environments

Split verbose content between presentation and article modes:

```latex
\mode<presentation>{%
  \begin{remark}[Title]
    \begin{itemize}
      \item Concise point 1
      \item Concise point 2
    \end{itemize}
  \end{remark}
}
\mode<article>{%
  \begin{remark}[Title]
    Full explanatory text with detailed reasoning...
  \end{remark}
}
```

### Overlays with Didactic Environments

Wrap in `uncoverenv` (didactic environments don't support `<overlay>` directly):

```latex
\begin{uncoverenv}<1,3>
  \begin{definition}[Title]
    Content...
  \end{definition}
\end{uncoverenv}
```

## Toggling Notes

```latex
\ltnoteon   % Show notes (default)
\ltnoteoff  % Hide notes
```

## Best Practices

1. **Write notes as you design** - Don't wait until the end
2. **Be specific** - Reference particular activities, examples
3. **Cite theory** - Connect to established research
4. **Think long-term** - Write for someone years later
5. **Question yourself** - Why this order? Why this example?
6. **Document failures** - Note when designs don't work
7. **Link to assessment** - How will you know if students learned?
8. **Keep notes focused** - One clear point per note

## Workflow

1. **Plan learning objectives** - What should students learn?
2. **Design approach** - How will you structure learning?
3. **Write content with inline notes** - Document reasoning as you write
4. **Review notes** - Check pedagogical rationale is clear
5. **Test with students** - Gather data mentioned in notes
6. **Refine based on feedback** - Update both content and notes

## Complementary Skills

- **variation-theory**: Reference variation patterns in notes
- **try-first-tell-later**: Document try-first pedagogy
- **literate-programming**: Apply similar documentation principles to code
- **latex-writing**: Follow LaTeX best practices in documentation

## Summary

**Key insight**: Literate programming explains code to humans; didactic notes explain *pedagogical design* to educators. Both make implicit reasoning explicit for future readers.

But keep the line sharp: `\ltnote` documents the design of the *teaching text* — why it is written and sequenced as it is. Claims about the subject, and decisions about the system being documented (with their citations), stay in the body text. If the note would still make sense to a reader who only cares *how the thing works*, it is body text, not an `\ltnote`.
