---
name: variation-theory
description: Apply variation theory of learning to structure instructional content using contrast, separation, generalization, and fusion patterns. Use when writing educational materials, explanations, tutorials, or when user mentions variation theory, learning theory, pedagogy, or critical aspects of learning.
---

# Variation Theory of Learning

This skill applies the variation theory of learning, developed by Ference Marton and colleagues, to structure content for optimal learning.

## Core Theoretical Principles

### The Object of Learning
The **object of learning** is what is to be learned. Understanding develops when learners discern the critical aspects of the object of learning.

### Critical Aspects and Discernment
**Critical aspects** are the features that must be discerned for understanding to occur. **Discernment** is the ability to distinguish these aspects.

Marton's central principle: "to learn something, the learner must discern what is to be learned. Discerning the object of learning amounts to discerning its critical aspects" (Marton & Pang, 2006).

### Variation and Invariance
The necessary condition for discernment: learners must experience **variation in a dimension corresponding to that aspect, against the background of invariance** in other aspects.

Key insight: "When some aspect of a phenomenon or an event varies while another aspect or other aspects remain invariant, the varying aspect will be discerned."

## The Four Patterns of Variation

According to Marton and Pang (2006), there are four patterns that enable discernment:

### 1. Contrast
**Purpose**: Help learners recognize that an aspect exists by experiencing what it is versus what it is not.

**How it works**: Present examples that differ in one critical aspect while keeping all other factors constant. The learner experiences variation of different values in one dimension.

**Example**: To understand "height," show two objects identical in all respects except height.

### 2. Separation
**Purpose**: Isolate critical features from the whole so learners can discern them independently.

**How it works**: Systematically vary certain elements while holding others constant, revealing which aspects are invariant and which vary.

**Example**: To understand how multiple variables affect a concept, vary them together so learners can examine the distinct effect of each variable.

### 3. Generalization
**Purpose**: Help learners recognize that a pattern or principle holds across different contexts.

**How it works**: Present the same critical value in varied appearances. Experience the invariant aspect across different contexts.

**Example**: Show the same geometric principle applied to triangles, rectangles, circles to reveal the universal pattern.

### 4. Fusion
**Purpose**: Enable learners to experience multiple critical aspects simultaneously as an integrated whole.

**How it works**: Vary several critical aspects at once so learners must attend to their simultaneous interrelationships.

**Example**: In understanding circuits, vary resistance and voltage simultaneously to grasp how changes in one parameter impact the others.

## Pedagogical Sequence

Research suggests using patterns in this developmental order:

1. **Begin with Contrast** - Establish that the aspect exists
2. **Use Separation** - Isolate individual critical aspects
3. **Apply Generalization** - Show the pattern across contexts
4. **Achieve Fusion** - Integrate aspects into comprehensive understanding

### Temporal Sequencing: Examples Before Generalizations

**Core principle**: Examples must precede generalizations. Students need concrete instances creating the necessary variation before abstract principles become meaningful.

**Why this matters**: Variation must be **experienced** before invariants can be discerned. When you state a general principle first, students have no variation pattern to map it onto. The principle remains abstract and difficult to integrate with existing knowledge.

**Anti-pattern example**:
```latex
% BAD: Generalization before examples
Filer behövs för tre huvudsakliga anledningar: persistens, datautbyte,
och skalbarhet.

\begin{example}[Spara spelets progress]
  ...
\end{example}
```

**Good pattern example**:
```latex
% GOOD: Examples create variation, then generalize
\begin{example}[Spara spelets progress]
  Ett spel behöver komma ihåg spelarens poäng mellan körningar...
\end{example}

\begin{example}[Dela data mellan program]
  Ett program genererar e-postadresser som ett annat sedan använder...
\end{example}

\begin{example}[Bearbeta stora datamängder]
  SCB:s namnstatistik innehåller miljontals poster...
\end{example}

\begin{remark}[Varför filer behövs]
  Filer behövs för persistens (minnas mellan körningar), datautbyte
  (överföra mellan program), och skalbarhet (hantera stora mängder data).
\end{remark}
```

**Pedagogical sequence**:
1. Show concrete examples that vary in one dimension (use case)
2. Keep invariant: the solution (using files)
3. Students discern the pattern: different problems, same solution
4. Generalize the pattern in a semantic environment (remark/definition/block)

**Key insight**: The generalization is only meaningful AFTER students have experienced the variation that makes the invariant pattern discernible.

### Side-by-Side Contrast with \textbytext*

**Purpose**: Create simultaneous visual contrast when two concepts need immediate comparison. This implements the Contrast pattern spatially rather than temporally.

**When to use**: Concepts that are defined **in relation to each other** and whose critical aspects are best understood through direct juxtaposition.

**The tool**: LaTeX didactic.sty provides `\textbytext*{...}{...}` to place environments side-by-side:
- **Starred version** (`\textbytext*`): Uses fullwidth for maximum space
- **Non-starred** (`\textbytext`): Uses normal column width

**IMPORTANT - Beamer compatibility**:
- `\textbytext*` (starred) does NOT work inside `\begin{frame}...\end{frame}`, even with `[fragile]`
- **Solution**: Use mode-specific versions:
  - `\mode<presentation>` with `\textbytext` (non-starred, column width works in beamer)
  - `\mode<article>` with `\textbytext*` (starred, fullwidth for article mode)
- This pattern is REQUIRED when using side-by-side contrast in beamer presentations

**Example use case**: Primärminne vs Sekundärminne - concepts defined by their opposing characteristics (flyktigt vs oflyktigt, snabbt vs långsamt).

**Implementation** (beamer-compatible with mode splits):
```latex
\begin{frame}
  \mode<presentation>{%
    \textbytext{%
      \begin{definition}[Primärminne]
        Datorns arbetsminne där exekverande program lagras.
        Detta är flyktigt minne med mycket snabb åtkomst
        (storleksordning nanosekunder).
      \end{definition}
    }{%
      \begin{definition}[Sekundärminne]
        Oflyktigt minne där icke-exekverande program och
        data (filer) lagras. Långsammare åtkomst än primärminne
        (storleksordning mikro- till millisekunder).
      \end{definition}
    }
  }
  \mode<article>{%
    \textbytext*{%
      \begin{definition}[Primärminne]
        Datorns arbetsminne där exekverande program lagras.
        Detta är flyktigt minne med mycket snabb åtkomst
        (storleksordning nanosekunder).
      \end{definition}
    }{%
      \begin{definition}[Sekundärminne]
        Oflyktigt minne där icke-exekverande program och
        data (filer) lagras. Långsammare åtkomst än primärminne
        (storleksordning mikro- till millisekunder).
      \end{definition}
    }
  }
\end{frame}
```

**For article-only contexts** (not beamer), you can use `\textbytext*` directly:
```latex
\textbytext*{%
  \begin{definition}[Primärminne]
    ...
  \end{definition}
}{%
  \begin{definition}[Sekundärminne]
    ...
  \end{definition}
}
```

**Variation pattern analysis**:
- **What varies**: Memory type (primary vs secondary) and all associated characteristics
- **What remains invariant**: The concept of computer memory storing data
- **Critical aspects made discernible**: Volatility (flyktigt/oflyktigt), speed (nanosekunder/millisekunder), purpose (executing/stored programs)

**Why this works**: Side-by-side presentation allows students to scan back and forth between the definitions, making the contrasting features immediately apparent. The spatial arrangement reinforces the conceptual opposition.

**Alternative approaches and when NOT to use**:
- **Sequential presentation** (uncoverenv): Better when you want students to understand each concept independently before comparing
- **\textbytext*** (side-by-side): Better when the concepts are mutually defining and comparison is essential for understanding

### Generalizations in Semantic Environments

**Principle**: When generalizing from examples, capture the generalization in a semantic environment (definition, remark, block) placed AFTER the examples.

**Why use semantic environments**:
1. **Highlights importance**: Visual distinction signals "this is a key takeaway"
2. **Makes referenceable**: Can be cited in pedagogical notes and student materials
3. **Suitable for notes**: Environments appear cleanly in article mode/handouts
4. **Searchable**: Students can scan for definitions/remarks when reviewing

**Environment selection guide**:
- **definition**: Formal concept definitions
  - Example: "En fil är en namngiven samling data som lagras i sekundärminnet"
- **remark**: Important observations, principles, or implications
  - Example: "Filer behövs för persistens, datautbyte, och skalbarhet"
- **block**: Key takeaways, summaries, or synthesis points
  - Example: "Återkommande programmeringsmönster: validera input, dict för räkning, läs-bearbeta-skriv"
- **example**: When the generalization is best shown through a code pattern
  - Example: The general pattern for file transformation (read-process-write)

**Anti-pattern**: Generalizations buried in prose paragraphs
```latex
% BAD: Important principle lost in prose
När vi arbetar med filer måste vi alltid öppna dem först,
sedan arbeta med innehållet, och till sist stänga dem.
Detta mönster återkommer i all filhantering.

\begin{example}[Läsa fil]
  ...
\end{example}
```

**Good pattern**: Generalization highlighted in semantic environment
```latex
% GOOD: Examples first, then generalization in environment
\begin{example}[Läsa fil]
  with open("data.txt", "r") as fil:
      innehåll = fil.read()
\end{example}

\begin{example}[Skriva fil]
  with open("data.txt", "w") as fil:
      fil.write(text)
\end{example}

\begin{remark}[Filhanteringsmönster]
  All filhantering följer mönstret: öppna → bearbeta → stäng.
  Funktionen \mintinline{python}{with} garanterar att filen stängs
  automatiskt även om fel uppstår.
\end{remark}
```

**Integration with variation theory**: The semantic environment containing the generalization represents the discernible **invariant pattern** that emerged from the **variation** in the examples. Students have experienced the pattern varying across different contexts (reading, writing, different file types) while the core structure remained invariant.

## Language Consistency When Documenting Variation Patterns

**CRITICAL**: When documenting variation theory in pedagogical notes (e.g., `\ltnote`), match the document's instructional language.

**Rule**: Write variation theory annotations in the same language as the student-facing content.

**Standard terminology translation examples (Swedish)**:
- "Variation Pattern" → "Variationsmönster"
- "Contrast" → "Kontrast"
- "Separation" → "Separation"
- "Generalization" → "Generalisering"
- "Fusion" → "Fusion"
- "What varies" → "Vad som varierar"
- "What remains invariant" → "Vad som hålls invariant"
- "Critical aspects to discern" → "Kritiska aspekter att urskilja"
- "Learning Objectives" → "Lärandemål"
- "Why this variation works" → "Varför denna variation fungerar"

**Keeping English terms when appropriate**:
- Citations: "Following Marton & Pang (2006)..." → "Enligt Marton & Pang (2006)..."
- Technical terms without standard translations: use `\foreignlanguage{english}{term}`
- Code-related terms: naturally remain in English

**Example - Swedish documentation:**
```latex
\ltnote{%
  \textbf{Variationsmönster}: Kontrast

  \textbf{Vad som varierar}: Implementeringsmetod (dict-baserad vs klassbaserad)

  \textbf{Vad som hålls invariant}: Problemet (telefonbokshantering) och
  funktionaliteten

  \textbf{Kritiska aspekter att urskilja}: Genom att se samma problem
  löst både med och utan klasser kan studenter urskilja vad en klass ÄR
  kontra vad den INTE är.

  \textbf{Varför denna variation fungerar}: Enligt Marton \& Pang (2006)
  varierar vi implementeringsmetoden medan vi håller problemet invariant.
  Detta gör FÖRDELARNA med klasser urskiljbara eftersom studenter kan se
  EXAKT vad som förändras när man introducerar klasser.
}
```

**Example - English documentation:**
```latex
\ltnote{%
  \textbf{Variation Pattern}: Contrast

  \textbf{What varies}: Implementation approach (dict-based vs class-based)

  \textbf{What remains invariant}: The problem domain and functionality

  \textbf{Critical aspects to discern}: By seeing the same problem solved
  with and without classes, students can discern what a class IS versus
  what it is NOT.

  \textbf{Why this variation works}: Following Marton \& Pang (2006), we
  vary the implementation approach while keeping the problem invariant...
}
```

**Avoid mixing languages unnecessarily** - it creates cognitive load for instructors reviewing the pedagogical design.

## When Applying This Skill

- Identify the **object of learning** (what should be understood)
- Determine the **critical aspects** (what must be discerned)
- Structure content using the **four patterns** to create necessary conditions for learning
- Remember: "there is no discernment without variation" (Marton, 2015)

## Key References

- Marton, F., & Booth, S. (1997). *Learning and Awareness*. Mahwah, NJ: Lawrence Erlbaum.
- Marton, F., & Pang, M. F. (2006). On Some Necessary Conditions of Learning. *Journal of the Learning Sciences*, 15(2), 193-220.
- Marton, F. (2015). *Necessary Conditions of Learning*. London: Routledge.
- Marton, F., & Tsui, A. (2004). *Classroom discourse and the space of learning*. Mahwah, NJ: Lawrence Erlbaum.
