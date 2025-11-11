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

1. **Why specific pedagogical strategies are used**
   - "We use try-first pedagogy here to activate prior knowledge"
   - "This applies the contrast pattern from variation theory"

2. **References to learning theories**
   - Variation theory patterns (contrast, separation, generalization, fusion)
   - Cognitive load theory considerations
   - Active learning principles

3. **Intended learning outcomes**
   - What critical aspects students should discern
   - Which learning objectives an activity addresses

4. **Design trade-offs and decisions**
   - Why examples are ordered in a particular way
   - Why certain details are omitted or included

5. **Future improvements**
   - Notes for refining the material
   - Data to collect for assessment

6. **Statistical or assessment purposes**
   - "This question helps us gauge prior knowledge"
   - "We collect this data to improve future iterations"

## Writing Effective Didactic Notes

### CRITICAL: Connect to Learning Objectives

**Core principle**: Variation patterns must be tied to specific learning objectives.

When documenting variation theory applications, ALWAYS:

1. **State learning objectives explicitly** at the beginning of sections:
   ```latex
   \ltnote{%
     \textbf{Learning Objectives:}
     \begin{enumerate}
       \item Students should discern [critical aspect]
       \item Students should identify [relationship/pattern]
       \item Students should be able to [apply/justify]
     \end{enumerate}
   }
   ```

2. **Map variation patterns to objectives**: Show HOW the variation helps achieve the objectives:
   ```latex
   \ltnote{%
     \textbf{Relation to Learning Objectives:}

     This [pattern name] directly addresses:
     \begin{itemize}
       \item \textbf{LO1}: By varying [X] while keeping [Y] invariant,
         students can discern [critical aspect]
       \item \textbf{LO2}: The contrast makes [relationship] visible
     \end{itemize}

     \textbf{Variation Pattern: [Name]}

     \textbf{What varies}: ...
     \textbf{What remains invariant}: ...
     \textbf{Critical aspects to discern (mapped to LOs)}: ...
   }
   ```

3. **Explain why the variation works**: Connect Marton's principles to your objectives:
   ```latex
   \textbf{Why this variation works:} Following Marton \& Pang (2006),
   we vary [X] while keeping [Y] invariant. This makes [critical aspect]
   discernible because students can see EXACTLY what changes...
   ```

### Structure Your Notes

1. **State learning objectives**: What should students be able to do?
2. **Reference theory**: Connect to established learning principles
3. **Explain the mechanism**: How does this design choice support the objectives?
4. **Map activities to objectives**: Show which activities address which objectives
5. **Note alternatives or improvements**: What else could work?

### Example Patterns

**Referencing variation theory:**
```latex
\ltnote{%
  This adheres to the variation theory principle of starting with the
  whole, to later break it down into parts by focusing on different
  aspects using patterns of variation.
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

Document how your material creates patterns of variation:

```latex
\ltnote{%
  We vary the programming language (Python vs Java) while keeping the
  algorithm invariant. This helps students discern that the algorithmic
  principle is independent of language syntax.
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

```latex
\section{Introduction to Recursion}

Let's start with your intuition.

\ltnote{%
  We begin with an exploration of prior knowledge following try-first
  pedagogy. This helps students connect recursion to concepts they
  already understand (like Russian dolls or fractals).
}

\begin{activity}\label{WhatIsRecursion}
  Have you seen anything in everyday life that contains smaller versions
  of itself?
\end{activity}

Now let's look at how this appears in programming.

\ltnote{%
  We move from concrete everyday examples to code, providing a bridge
  between intuitive and formal understanding. This follows variation
  theory's principle of using familiar contexts before abstract ones.
}

Here's a simple recursive function:

<<factorial function>>=
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
@

\ltnote{%
  We start with the complete function (the whole) following variation
  theory. In subsequent sections, we'll break down the base case and
  recursive case (the parts), varying what we focus on while keeping
  other aspects invariant.
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
