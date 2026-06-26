---
name: variation-theory
description: Apply variation theory of learning to structure content using contrast, generalization, and fusion patterns. Variation must target the critical aspects of the learning objective. Use proactively when (1) writing educational materials, explanations, tutorials, or lecture slides, (2) designing or reviewing examples in documentation, READMEs, or literate programs (.nw files), especially when multiple examples illustrate alternative approaches to the same task, (3) structuring code examples, CLI usage examples, or API examples where the reader should notice what differs between alternatives, (4) user mentions variation theory, learning theory, pedagogy, contrast, invariance, or critical aspects. Also activate when asked to elaborate, make concrete, or add examples to existing content. Works alongside literate-programming and didactic-notes skills; in educational LaTeX or .nw materials, keep variation-analysis labels in \ltnote{} rather than student-facing prose, unless the document itself is about that design.
---

# Variation Theory of Learning

This skill applies the variation theory of learning, developed by Ference Marton and colleagues, to structure content for optimal learning.

## Reference Files

This skill includes detailed references in `references/`:

| File | Content | Search patterns |
|------|---------|-----------------|
| `common-violations.md` | Generalization-before-example violations | `BAD`, `GOOD`, violation types |
| `latex-examples.md` | Side-by-side contrast, semantic environments | `\textbytext`, `\ltnote`, Swedish |

## Core Theoretical Principles

### The Object of Learning

The **object of learning** is what is to be learned. Understanding develops when learners discern the **critical aspects** of the object of learning.

Marton's central principle: "to learn something, the learner must discern what is to be learned. Discerning the object of learning amounts to discerning its critical aspects."

### Variation and Invariance

The necessary condition for discernment: learners must experience **variation in a dimension corresponding to that aspect**, against the background of **invariance** in other aspects.

**Key insight**: "When some aspect of a phenomenon varies while another aspect remains invariant, the varying aspect will be discerned."

## Critical Aspects as Focus of Variation

**FUNDAMENTAL PRINCIPLE**: Variation must occur in the **critical aspects** of the object of learning. Arbitrary variation does not lead to learning.

### Identifying Critical Aspects First

Before designing any pattern of variation:

1. **Define the object of learning** - What should learners understand/do?
2. **Identify the critical aspects** - Which features must be discerned?
3. **Design variation IN those aspects** - Create patterns varying the critical dimensions

### Dimensions vs Values

The principle "one thing at a time" applies to **dimensions** (aspects), NOT to **values** within a dimension.

- **Dimension (aspect)**: A category/feature type (e.g., "punctuation marks", "file mode")
- **Values/features**: Specific instances (e.g., punctuation marks like period, question mark, exclamation mark; or file modes like `r`, `w`, `a`)

**The principle:**
- **Vary ONE dimension at a time** - to separate aspects from each other
- **Contrast MULTIPLE values together** - within that dimension

**Research evidence**: Teaching punctuation marks separately: 15% improvement. Teaching all three together with contrast: 63% improvement.

### Common Mistake: Varying Non-Critical Aspects

**Anti-pattern**: Creating variation in aspects irrelevant to the learning objective.

**Example**: Teaching "why files need open/close":
- **Wrong**: Vary filename or content (not critical)
- **Right**: Vary what happens when close() is/isn't called (critical aspect is resource management)

## Applying Contrast in Documentation Examples

Variation theory is not limited to classroom teaching — it applies
whenever a reader must discern differences between alternatives.
Documentation, READMEs, and literate programs routinely show multiple
ways to achieve the same goal.  The contrast pattern ensures the
reader's attention falls on the **method** (the critical aspect) rather
than on incidental details.

### Principle: Keep the Problem Invariant, Vary the Method

When showing alternative approaches to the same task, use the **same
concrete names, filenames, and identifiers** across all examples.  If
the names change between examples, the reader must determine whether
the name change is meaningful — this distracts from the actual
difference (the method).

### Where the variation analysis goes: notes vs. body

**Decide with one question first: is the \enquote{what varies / what stays
invariant} analysis commentary *about* the teaching, or is it the document's
*subject matter*?** Getting this backwards is a common mistake — do not reach
for `\ltnote` reflexively.

- **The document teaches a subject** (a tutorial, lecture, README, literate
  program, crypto notes). The reader is there to learn the subject, not the
  pedagogy. The variation analysis is meta-commentary about how the material is
  built, so it goes in `\ltnote{...}` (via the `didactic-notes` skill). Keep the
  visible prose focused on the example itself and the feature the reader should
  use. **This is the common case.**

- **The teaching design *is* the subject** (a research paper, a methods or
  pedagogy writeup, an article *analysing* how to teach against a misconception).
  Here the variation analysis is the content — the very finding the document
  reports — so it belongs in the **body prose**. Putting it in `\ltnote` hides
  the document's own argument. `\ltnote` is then reserved for reasoning about the
  *document's own construction*: why a section is ordered this way, why this
  example was chosen, where a topic is placed.

This is the same scope test the `didactic-notes` skill states: if the note would
still make sense to a reader who only cares *how the thing being described
works*, it is body text. When the thing being described *is* the teaching design,
the variation analysis is body text.

#### Common case — the document teaches a subject

**Bad** --- student-facing pedagogical meta-commentary:

```latex
These two examples form a deliberate contrast.

\begin{description}
\item[What varies] Whether [[show_url]] is set to [[False]].
\item[What stays invariant] The helper, question, and environment.
\end{description}
```

**Good** --- instructor-facing pedagogical annotation:

```latex
\ltnote{%
  \textbf{Variation pattern}: Contrast
  \textbf{What varies}: Whether [[show_url]] is set to [[False]].
  \textbf{What stays invariant}: The helper, question, and environment.
}
```

#### Carve-out — the document is *about* the teaching design

In a research paper whose subject is the variation-theory designs themselves,
state the analysis in the body and keep `\ltnote` for authoring decisions only.

**Good** --- the analysis is body prose (it is the finding):

```latex
We keep the program invariant and vary only the truth value of the condition,
so the reader discerns that a false \mintinline{python}{if} does not terminate
the program and the \mintinline{python}{else} does not also run.
```

**Good** --- `\ltnote` carries a decision about the *paper*, not the design:

```latex
\ltnote{Placed in the types chapter rather than functions/variables because
students first meet it as a property of the string type.}
```

### Example: CLI Documentation with Two Delivery Methods

A tool offers two ways to share a log: push/clone via Git, or
export/play via a bundle file.  The object of learning is "how to
share a log"; the critical aspect is "which delivery method to use."

**BAD** — names vary alongside the method, obscuring what actually
changed:

```
# Method 1: push to remote
learnlog set-remote git@gitlab.kth.se:dbosk/demo-log.git
learnlog push

# Method 2: export as bundle
learnlog export -o lecture01.bundle
learnlog play lecture01.bundle
```

The reader sees `demo-log` vs `lecture01` and wonders: does the name
matter?  Is a bundle different from a repository?  The irrelevant
variation in the name competes with the relevant variation in the
method.

**GOOD** — the name is invariant, only the method varies:

```
# Method 1: push to remote
learnlog set-remote git@gitlab.kth.se:dbosk/lecture01.git
learnlog push
...
learnlog clone git@gitlab.kth.se:dbosk/lecture01.git
learnlog play

# Method 2: export as bundle
learnlog export -o lecture01.bundle
...
learnlog play lecture01.bundle
```

Now `lecture01` is invariant across both examples.  The only thing
that changes is the delivery mechanism (push/clone vs export/play),
which is exactly the critical aspect the reader should discern.

### When to Apply This

Activate this pattern whenever you encounter:
- Multiple code examples showing alternative approaches
- CLI usage sections with different flags or subcommands
- API examples with different authentication methods
- Configuration examples with different backends
- Any documentation where "you can also do X instead of Y"

**Self-test:** If two examples differ in more ways than the one
dimension you intend to contrast, eliminate the incidental differences.

### Mentipy for Live Variation

Mentipy can operationalize variation patterns in live teaching.  Use a short
sequence of `mc`, `scale`, `open_text`, or `word_cloud` questions to vary one
critical aspect at a time while keeping the object of learning invariant.
This is especially useful for diagnostic contrast before an explanation and
for checking whether students now discern the critical aspect afterward.

## The Three Patterns of Variation

### 1. Contrast

**Purpose**: Help learners recognize that an aspect exists by experiencing what it is versus what it is not.

**How it works**: Present examples that differ in one critical aspect while keeping all other factors constant.

**Example**: To understand "height," show two objects identical in all respects except height.

**Note**: Contrast achieves *separation*—the critical aspect becomes discernible through experiencing variation.

### 2. Generalization

**Purpose**: Help learners recognize that a pattern or principle holds across different contexts.

**How it works**: Present the same critical value in varied appearances. Keep the critical aspect invariant while varying other (non-critical) aspects.

**Example**: Show the same geometric principle applied to triangles, rectangles, circles.

### 3. Fusion

**Purpose**: Enable learners to experience multiple critical aspects simultaneously as an integrated whole.

**How it works**: Vary several critical aspects at once so learners must attend to their simultaneous interrelationships.

**Example**: In understanding circuits, vary resistance and voltage simultaneously.

## Pedagogical Sequence

Research suggests using patterns in this order:

1. **Contrast** - Vary the critical aspect while keeping other aspects invariant. This *separates* (makes discernible) the critical aspect.
2. **Generalization** - Keep the critical value invariant while varying other aspects. Shows the pattern holds across contexts.
3. **Fusion** - Vary multiple critical aspects simultaneously. Enables learners to experience interrelationships.

**Important**: Within each pattern, contrast multiple **values** together. "One at a time" applies to **dimensions/aspects**, not values.

## Temporal Sequencing: Examples Before Generalizations

**CRITICAL**: Examples must precede generalizations. Students need concrete instances creating necessary variation before abstract principles become meaningful.

**Why**: Variation must be **experienced** before invariants can be discerned. When you state a general principle first, students have no variation pattern to map it onto.

**Anti-pattern:**
```latex
% BAD: Generalization before examples
Filer behövs för persistens, datautbyte, och skalbarhet.

\begin{example}[Spara spelets progress]
  ...
\end{example}
```

**Good pattern:**
```latex
% GOOD: Examples create variation, then generalize
\begin{example}[Spara spelets progress]
  Ett spel behöver komma ihåg spelarens poäng...
\end{example}

\begin{example}[Dela data mellan program]
  Ett program genererar data som ett annat använder...
\end{example}

\begin{remark}[Varför filer behövs]
  Filer behövs för persistens, datautbyte, och skalbarhet.
\end{remark}
```

See `references/common-violations.md` for detailed violation types and fixes.

## Common Generalization Violations

See `references/common-violations.md` for detailed examples.

**Violation types:**
1. **Generic/placeholder code before concrete examples**
2. **Block/remark environments before examples**
3. **Incomplete skeletons before complete solutions**
4. **Explanatory principles before demonstrating examples**

**Fix pattern** for each violation:
1. Remove the generalization from its current position
2. Ensure 2-3 concrete examples exist creating necessary variation
3. Add back the generalization AFTER examples
4. Verify students can now discern the pattern from the variation

## Side-by-Side Contrast

See `references/latex-examples.md` for details.

For Beamer presentations, use mode splits:

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
      ...
    }{%
      ...
    }
  }
\end{frame}
```

## Generalizations in Semantic Environments

Capture generalizations in semantic environments AFTER examples:

| Environment | Use for |
|-------------|---------|
| `definition` | Formal concept definitions |
| `remark` | Important observations, principles |
| `block` | Key takeaways, summaries |
| `example` | When generalization is best shown through code |

## Language Consistency

**CRITICAL**: When documenting variation theory in notes (e.g., `\ltnote`), match the document's instructional language.

**Swedish terminology:**
- "Variation Pattern" → "Variationsmönster"
- "Contrast" → "Kontrast"
- "What varies" → "Vad som varierar"
- "What remains invariant" → "Vad som hålls invariant"
- "Critical aspects" → "Kritiska aspekter"

## When Applying This Skill

1. Identify the **object of learning** (what should be understood)
2. Determine the **critical aspects** (what must be discerned)
3. Structure content using the **three patterns** to create necessary conditions
4. Remember: "there is no discernment without variation"

## Connection to Try-First-Tell-Later

The try-first-tell-later skill complements variation theory: use try-first prompts to **diagnose which critical aspects students can already discern**, then design variation patterns to teach aspects they cannot yet see.

## Key References

- Marton, F. (2015). *Necessary Conditions of Learning*. Routledge. (Primary reference)
- Marton, F., & Booth, S. (1997). *Learning and Awareness*. Lawrence Erlbaum.
- Marton, F., & Pang, M. F. (2006). On Some Necessary Conditions of Learning. *Journal of the Learning Sciences*, 15(2), 193-220.
- Marton, F., & Tsui, A. (2004). *Classroom discourse and the space of learning*. Lawrence Erlbaum.
