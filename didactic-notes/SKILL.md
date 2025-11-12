---
name: didactic-notes
description: Document pedagogical design decisions in educational materials using the didactic LaTeX package and \ltnote command. Use proactively when (1) writing or editing educational LaTeX materials with pedagogical content, (2) adding variation theory labels or patterns to student-facing content, (3) explaining design trade-offs or choices in educational materials, (4) documenting why specific examples or exercises are sequenced in a particular way. Invoke when user mentions didactic notes, \ltnote, pedagogical reasoning, learning theory notes, educational design documentation, variation theory labels in student content, or asks to move pedagogical reasoning to instructor notes. CRITICAL: Pedagogical reasoning (variation/invariance labels, pattern names, design rationale) should be in \ltnote{}, NOT in student-facing text.
---

# Didactic Notes: Literate Pedagogy

This skill applies the principle of documenting pedagogical design decisions in educational materials, analogous to how literate programming documents code design decisions.

## Core Principle

**Document not just what you teach, but *why* you teach it that way.**

Just as literate programming makes code reasoning explicit, didactic notes make pedagogical reasoning explicit using the `\ltnote{...}` command from the LaTeX `didactic` package.

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
  the actual behavior, helping them discern the critical aspect of
  how the function processes its input.
}
```

The note documents the pedagogical strategy (try-first), the learning theory (contrast pattern from variation theory), and the intended learning outcome (discerning the critical aspect).

## Who Benefits from Didactic Notes

Making pedagogical reasoning explicit helps:

- **Future instructors**: Understand and adapt the material
- **Authors**: Reflect on instructional design choices
- **Researchers**: Analyze pedagogical approaches
- **Students** (when notes are visible): Understand the learning design

## The `didactic` Package

The `didactic` LaTeX package provides infrastructure for educational material design, including:

- The `\ltnote{...}` command for pedagogical margin notes
- Commands to toggle notes on/off: `\ltnoteoff` and `\ltnoteon`
- Various semantic environments (activity, exercise, question, etc.)
- Tools for creating educational materials that work as both slides (Beamer) and articles

### Package Setup

```latex
\usepackage[marginparmargin=outer]{didactic}
```

Options:
- `marginparmargin=outer` - Place margin notes on outer margins (default for `\ltnote`)
- `inner=20mm`, `outer=60mm` - Set margin widths
- `notheorems` - Disable automatic theorem environments

## Learning Objectives with Restatable Environment

**CRITICAL**: When documenting learning objectives in educational materials, use the `restatable` environment with the `lo` semantic environment.

### Defining Learning Objectives

Use `\begin{restatable}{lo}{MnemonicLabel}...\end{restatable}` in your abstract or learning objectives section:

```latex
\begin{restatable}{lo}{FilesLOPersistence}%
  Förklara skillnaden mellan primärminne och sekundärminne samt varför filer
  behövs för persistens.
\end{restatable}

\begin{restatable}{lo}{FilesLOOperations}%
  Använda filoperationer (\mintinline{python}{open()},
  \mintinline{python}{read()}, \mintinline{python}{write()},
  \mintinline{python}{close()}) korrekt.
\end{restatable}
```

**Key points:**
- Use **mnemonic labels** (e.g., `FilesLOPersistence`, not `FilesLO1`)
- Labels describe the objective content, not just numbers
- The `%` after the opening brace prevents unwanted whitespace

### Referring to Learning Objectives

In `\ltnote{}` blocks, refer to learning objectives using the **starred command** created by `restatable`:

**Format pattern:**
```latex
\ltnote{%
  Relevanta lärandemål:
  \FilesLOPersistence*

  \textbf{Kontrast}: Typ av minne (primär vs sekundär)...
}
```

**Key formatting rules:**
1. **Use header**: Begin with "Relevanta lärandemål:" (or "Relevant learning objectives:" in English)
2. **Each LO on its own line**: Don't use commas between multiple LOs
3. **No trailing punctuation**: Don't add periods after LO commands
4. **Blank line after LOs**: Separate LOs from the rest of the note content

**Multiple learning objectives:**
```latex
\ltnote{%
  Relevanta lärandemål:
  \FilesLOOperations*
  \FilesLOContextMgr*
  \FilesLOFileTypes*

  \textbf{Generalisering + Kontrast}: Koppling till...
}
```

**CRITICAL: Do NOT add prefixes like "LO:" or "\textbf{LO}:"**

The command `\FilesLOPersistence*` already produces "Lärandemål 1" (or "Learning Objective 1" in English documents). Adding extra prefixes creates redundancy:

**Wrong:**
```latex
\ltnote{%
  \textbf{LO}: \FilesLOPersistence*.  % WRONG: Double prefix
}
```

**Wrong:**
```latex
\ltnote{%
  \FilesLOPersistence*, \FilesLOContextMgr*.  % WRONG: Commas, periods
}
```

**Correct:**
```latex
\ltnote{%
  Relevanta lärandemål:
  \FilesLOPersistence*
  \FilesLOContextMgr*

  \textbf{Mönster}: ...
}
```

### Learning Objectives Cannot Be in Lists

**CRITICAL**: Learning objective commands created by `restatable` are like theorem environments—they cannot be placed inside `\begin{itemize}` or other list environments.

**Wrong:**
```latex
\ltnote{%
  \textbf{Kritiska aspekter}:
  \begin{itemize}
    \item \FilesLOOperations* --- Resurshantering
    \item \FilesLOContextMgr* --- Automatisk stängning
  \end{itemize}
}
```

**Correct - Move LO commands outside lists:**
```latex
\ltnote{%
  \FilesLOOperations*, \FilesLOContextMgr*.

  \textbf{Kritiska aspekter}:
  \begin{itemize}
    \item \textbf{Resurshantering}: Filer måste stängas.
    \item \textbf{Kontexthanterare}: Automatisk stängning även vid fel.
  \end{itemize}
}
```

**Alternative - Reference in prose:**
```latex
\ltnote{%
  \textbf{Kritiska aspekter för} \FilesLOOperations* \textbf{och} \FilesLOContextMgr*\textbf{:}
  \begin{itemize}
    \item \textbf{Resurshantering}: Filer måste stängas.
    \item \textbf{Kontexthanterare}: Automatisk stängning.
  \end{itemize}
}
```

### Setup for Restatable Learning Objectives

Ensure your preamble includes:

```latex
\usepackage{thmtools,thm-restate}
\usepackage{didactic}

\ProvideSemanticEnv{lo}{Learning Objective}
  [style=definition,numbered=yes]
  {LO}{LO}
  {Learning objective}{Learning objectives}

% Translations for Swedish
\ProvideTranslation{swedish}{Learning Objective}{Lärandemål}
\ProvideTranslation{swedish}{LO}{lm}
\ProvideTranslation{swedish}{Learning objective}{Lärandemål}
\ProvideTranslation{swedish}{Learning objectives}{Lärandemål}
```

## Citing Pedagogical Research with Biblatex

### Separate Bibliography for Pedagogical References

**Best practice**: Use a separate `.bib` file for pedagogical and learning theory references (e.g., `ltnotes.bib`), distinct from domain-specific references.

**In your preamble:**
```latex
\usepackage[natbib,style=alphabetic,maxbibnames=99]{biblatex}
\addbibresource{bibliography.bib}  % Domain references
\addbibresource{ltnotes.bib}        % Pedagogical references
```

### Creating ltnotes.bib

Create a separate file with pedagogical references:

```bibtex
@article{MartonPang2006,
  author    = {Marton, Ference and Pang, Ming Fai},
  title     = {On Some Necessary Conditions of Learning},
  journal   = {Journal of the Learning Sciences},
  year      = {2006},
  volume    = {15},
  number    = {2},
  pages     = {193--220},
  doi       = {10.1207/s15327809jls1502_2}
}

@book{Marton2015,
  author    = {Marton, Ference},
  title     = {Necessary Conditions of Learning},
  publisher = {Routledge},
  address   = {London},
  year      = {2015},
  isbn      = {978-0-415-739139}
}
```

### Using Citations in Didactic Notes

**Use biblatex citation commands** instead of hardcoded references:

**Wrong:**
```latex
\ltnote{%
  Following Marton & Pang (2006), we vary the operation while keeping
  the pattern invariant...
}
```

**Correct:**
```latex
\ltnote{%
  Following \textcite{MartonPang2006}, we vary the operation while keeping
  the pattern invariant...
}
```

**Common biblatex commands for pedagogical notes:**
- `\textcite{key}` → "Marton and Pang (2006)"
- `\parencite{key}` → "(Marton and Pang 2006)"
- `\citeauthor{key}` → "Marton and Pang"
- `\citeyear{key}` → "2006"

**Example in context:**
```latex
\ltnote{%
  \FilesLOPersistence*.

  \textbf{Kontrast}: Typ av minne (primär vs sekundär).

  Enligt \textcite{MartonPang2006} måste studenter erfara variation i
  kritiska dimensioner för att kunna urskilja dessa aspekter.
}
```

## The `\ltnote` Command

The `\ltnote{...}` command creates margin notes documenting pedagogical rationale:

```latex
\ltnote{%
  We want to investigate what people think literate programming is.
  This will help us understand the correctness of their prior knowledge.

  This also gives us the contrast pattern for the goals of literate
  programming. They think of what it might mean, whereas when we give
  the definition below, we introduce contrast to their thoughts.
}
```

### When to Use `\ltnote`

Use `\ltnote` to document:

1. **Which learning objectives are addressed**
   - Use "Relevanta lärandemål:" header (or "Relevant learning objectives:" in English)
   - Reference using restatable commands on separate lines: `\FilesLOPersistence*`
   - Map activities to specific objectives
   - Show how variation patterns support objectives

2. **Why specific pedagogical strategies are used**
   - "We use try-first pedagogy here to activate prior knowledge"
   - "This applies the contrast pattern from variation theory"
   - Cite learning theory: `\textcite{MartonPang2006}`

3. **References to learning theories**
   - Variation theory patterns (contrast, separation, generalization, fusion)
   - Cognitive load theory considerations
   - Active learning principles
   - Use biblatex citations instead of hardcoded references

4. **Critical aspects students should discern**
   - What aspects become visible through variation
   - How invariants help students focus on critical features

5. **Design trade-offs and decisions**
   - Why examples are ordered in a particular way
   - Why certain details are omitted or included

6. **Future improvements**
   - Notes for refining the material
   - Data to collect for assessment

7. **Statistical or assessment purposes**
   - "This question helps us gauge prior knowledge"
   - "We collect this data to improve future iterations"

## Writing Effective Didactic Notes

### CRITICAL: Connect to Learning Objectives

**Core principle**: Variation patterns must be tied to specific learning objectives.

When documenting variation theory applications, ALWAYS:

1. **Reference learning objectives using restatable commands**:
   ```latex
   \ltnote{%
     Relevanta lärandemål:
     \FilesLOPersistence*

     \textbf{Mönster}: Kontrast

     \textbf{Varierar}: Typ av minne (primär vs sekundär)
     \textbf{Invariant}: Behovet att lagra data
   }
   ```

2. **Map variation patterns to objectives**: Show HOW the variation helps achieve the objectives:
   ```latex
   \ltnote{%
     Relevanta lärandemål:
     \FilesLOOperations*
     \FilesLOContextMgr*

     \textbf{Mönster}: Generalisering + Kontrast

     \textbf{Kritiska aspekter}:
     \begin{itemize}
       \item \textbf{Resurshantering}: Filer måste stängas
       \item \textbf{Kontexthanterare}: \mintinline{python}{with} garanterar
         automatisk stängning
     \end{itemize}

     \textbf{Koppling till print/input}: Samma princip (strukturera data för
     I/O), olika destination (terminal vs fil).
   }
   ```

3. **Explain why the variation works**: Connect to learning theory with citations:
   ```latex
   \ltnote{%
     Relevanta lärandemål:
     \FilesLOCSV*

     Enligt \textcite{MartonPang2006} måste studenter erfara variation i
     kritiska dimensioner för att kunna urskilja dessa aspekter. Vi varierar
     formatet (eget vs CSV) medan struktureringsprincipen förblir invariant.
   }
   ```

### Structure Your Notes

1. **State learning objectives**: What should students be able to do?
2. **Reference theory**: Connect to established learning principles
3. **Explain the mechanism**: How does this design choice support the objectives?
4. **Map activities to objectives**: Show which activities address which objectives
5. **Note alternatives or improvements**: What else could work?

### Language Consistency in Notes

**CRITICAL**: Match the language of `\ltnote` content to the document's instructional language.

**Rule**: If the student-facing content is in language X, write `\ltnote` content in language X.

**When to use English in non-English documents**:
- Established technical terms (use `\foreignlanguage{english}{term}`)
- Direct quotations from English sources
- Code examples and command names (naturally in English)
- References to English-language concepts that lack standard translations

**Examples**:

**Good - Swedish document with Swedish notes:**
```latex
\begin{exercise}
  Hur kan vi implementera addition av två bråk?
\end{exercise}

\ltnote{%
  \textbf{Lärandemål}: LO1 (Implementera aritmetiska operationer)

  \textbf{Variationsmönster}: Kontrast

  Vi varierar operationen (addition vs subtraktion) medan vi håller
  operatoröverlagringsmönstret invariant. Detta hjälper studenter att
  urskilja att \mintinline{python}{__add__} och \mintinline{python}{__radd__}
  följer samma mönster.

  Enligt Marton \& Pang (2006) måste studenter erfara variation för att
  kunna urskilja kritiska aspekter. Här skapar vi variation genom att
  visa både \foreignlanguage{english}{commutative} (addition) och
  \foreignlanguage{english}{non-commutative} (subtraktion) operationer.
}
```

**Bad - Mixing languages unnecessarily:**
```latex
\ltnote{%
  \textbf{Learning Objectives}: LO1 (Implement arithmetic operations)

  \textbf{Variation Pattern}: Contrast

  We vary the operation while keeping invariant...
}
```
In a Swedish document, this creates cognitive dissonance and makes notes harder to read for instructors working in Swedish.

**When English is appropriate:**
```latex
\ltnote{%
  Vi använder \foreignlanguage{english}{try-first pedagogy} här eftersom
  studenter ska förutspå innan vi förklarar. Detta skapar
  \foreignlanguage{english}{contrast} mellan deras mentala modell och
  det faktiska beteendet.

  Referens till kod: \mintinline{python}{__add__} kallas automatiskt.
}
```

**LaTeX command for language switching:**
```latex
\foreignlanguage{english}{technical term or phrase}
```

### Example Patterns

**Referencing learning objectives and variation theory:**
```latex
\ltnote{%
  Relevanta lärandemål:
  \FilesLOPersistence*

  \textbf{Kontrast}: Typ av minne (primär vs sekundär), egenskaper (flyktigt vs
  oflyktigt). Invariant: Behovet att lagra data.

  Enligt \textcite{MartonPang2006} gör denna kontrast de kritiska aspekterna
  av persistens urskiljbara för studenter.
}
```

**Referencing multiple learning objectives:**
```latex
\ltnote{%
  Relevanta lärandemål:
  \FilesLOOperations*
  \FilesLOContextMgr*
  \FilesLOFileTypes*

  \textbf{Generalisering}: Koppling till \mintinline{python}{print()}/
  \mintinline{python}{input()}. Samma princip (strukturera data för I/O),
  olika destination.
}
```

**Explaining pedagogical choices:**
```latex
\ltnote{%
  We need to do the same thing twice to contrast what we want the
  students to focus on, namely:
  \begin{enumerate}
  \item The specific feature that works in case A but not case B,
  \item How we can achieve the same goal using different approaches.
  \end{enumerate}
}
```

**Documenting activities:**
```latex
\ltnote{%
  The purpose of \cref{QuestionLabel} is to get students thinking about
  concepts they already know that might relate to this topic. This
  activates prior knowledge and creates mental hooks for new information.
}
```

**Noting assessment purposes:**
```latex
\ltnote{%
  We want to investigate how many students have heard of this concept.
  This will give us baseline statistics and help understand the
  correctness of answers in \cref{FollowUpActivity}.
}
```

**Explaining omissions:**
```latex
\ltnote{%
  We deliberately omit the technical details here to avoid cognitive
  overload. Students should first grasp the conceptual model before
  encountering implementation complexity.
}
```

## Integration with Learning Theories

### Variation Theory

Document how your material creates patterns of variation, citing \textcite{MartonPang2006}:

```latex
\ltnote{%
  Relevanta lärandemål:
  \AlgorithmsLOAbstraction*

  \textbf{Mönster}: Generalisering

  \textbf{Varierar}: Programmeringsspråk (Python vs Java)
  \textbf{Invariant}: Algoritmisk princip

  Enligt \textcite{MartonPang2006} hjälper denna variation studenter att
  urskilja att den algoritmiska principen är oberoende av språksyntax.
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

## Toggling Notes for Different Audiences

Notes can be hidden or shown depending on the audience:

```latex
% In instructor version (notes visible)
\ltnoteon  % This is the default

% In student version (notes hidden)
\ltnoteoff
```

Use cases:
- **Students**: Hide notes to avoid distraction
- **Instructors**: Show notes to understand pedagogical design
- **Co-authors**: Show notes during material development
- **Researchers**: Show notes when analyzing instructional design

## Integration with Other Didactic Features

### Semantic Environments

The `didactic` package provides semantic environments that pair well with `\ltnote`:

```latex
\begin{activity}
  Try implementing this function before reading further.
\end{activity}

\ltnote{%
  This activity uses try-first pedagogy to engage students before
  providing the solution.
}
```

Available environments:
- `activity` - Active learning tasks
- `exercise` - Practice problems
- `question` - Discussion questions
- `remark` - Side notes for students
- `summary` - Section summaries
- `definition`, `theorem`, `example` - Mathematical content

### Cross-References

Use `\label` and `\cref` to reference activities in notes:

```latex
\begin{activity}\label{FirstAttempt}
  What do you think this function does?
\end{activity}

\ltnote{%
  The purpose of \cref{FirstAttempt} is to activate prior knowledge
  before we formally define the concept.
}
```

## Workflow for Educational Material Development

1. **Plan the learning objectives**: What should students learn?
2. **Design the instructional approach**: How will you structure learning?
3. **Write content with inline notes**: Document your reasoning as you write
4. **Review notes**: Check that pedagogical rationale is clear
5. **Test with students**: Gather data mentioned in notes
6. **Refine based on feedback**: Update both content and notes
7. **Share with colleagues**: Notes help them understand and adapt material

## Best Practices

1. **Write notes as you design**: Don't wait until the end
2. **Be specific**: Reference particular activities, examples, or sections
3. **Cite theory**: Connect to established research when applicable
4. **Think long-term**: Write for someone encountering the material years later
5. **Question yourself**: Why this order? Why this example? Why now?
6. **Document failures**: Note when designs don't work as intended
7. **Link to assessment**: How will you know if students learned?
8. **Keep notes focused**: One clear point per note

## Example: Complete Section with Notes

First, define learning objectives in your abstract:

```latex
\begin{restatable}{lo}{RecursionLOConcept}%
  Förklara rekursionsbegreppet och identifiera basfall och rekursivt steg.
\end{restatable}

\begin{restatable}{lo}{RecursionLOImplementation}%
  Implementera enkla rekursiva funktioner korrekt.
\end{restatable}
```

Then use them in your content:

```latex
\section{Introduction to Recursion}

Let's start with your intuition.

\ltnote{%
  Relevanta lärandemål:
  \RecursionLOConcept*

  \textbf{Try-first}: Vi börjar med utforskning av förkunskaper för att
  aktivera studenternas intuitiva förståelse (ryska dockor, fraktaler).
}

\begin{activity}\label{WhatIsRecursion}
  Have you seen anything in everyday life that contains smaller versions
  of itself?
\end{activity}

Now let's look at how this appears in programming.

\ltnote{%
  \textbf{Generalisering}: Vi rör oss från konkreta vardagsexempel till kod,
  vilket ger en bro mellan intuitiv och formell förståelse.

  Enligt \textcite{MartonPang2006} underlättar denna progression från bekanta
  till abstrakta kontexter lärande.
}

Here's a simple recursive function:

<<factorial function>>=
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
@

\ltnote{%
  Relevanta lärandemål:
  \RecursionLOConcept*
  \RecursionLOImplementation*

  \textbf{Mönster}: Generalisering (helhet före delar)

  Vi börjar med den kompletta funktionen (helheten). I senare avsnitt
  bryter vi ner basfallet och det rekursiva steget (delarna), genom att
  variera vad vi fokuserar på medan andra aspekter hålls invarianta.
}
```

## Complementary Skills

Didactic notes work well with:

- **variation-theory**: Reference variation patterns in your notes
- **try-first-tell-later**: Document why you're using try-first pedagogy
- **literate-programming**: Apply similar documentation principles to code
- **pqbl**: Explain the pedagogical reasoning behind question sequences

## When to Use This Skill

Use didactic notes when writing or designing:
- Lecture materials (Beamer slides, course notes)
- Tutorials and educational documentation
- Learning activities and exercises
- Materials for collaborative development
- Instructional design research

## Summary

**Key insight**: Literate programming explains code to humans; didactic notes explain *pedagogical design* to educators. Both make implicit reasoning explicit for future readers (including your future self).
