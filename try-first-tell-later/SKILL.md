---
name: try-first-tell-later
description: Structure educational content using try-first-tell-later pedagogy where students predict, attempt, or reflect before receiving explanations. Creates active learning through cognitive engagement and variation theory's contrast patterns. Use when writing educational materials, designing exercises, creating lecture notes, structuring tutorials, writing teaching examples with LaTeX/Beamer, developing problem sets, or when user mentions try-first, predict-first, productive failure, Socratic method, question-before-answer, exercise-driven learning, or inquiry-based teaching.
---

# Try-First-Tell-Later Pedagogy

This skill applies the pedagogical principle of engaging learners' thinking **before** presenting information, creating active learning through anticipation, prediction, and problem-solving attempts.

## Core Principle

**Ask students to think, predict, or attempt solutions BEFORE providing the answer or explanation.**

This creates powerful learning through:
- **Double contrast**: Students contrast known approaches with new problems, then contrast their thinking with expert knowledge
- **Active engagement**: Learning happens through attempting, not just receiving
- **Metacognitive awareness**: Predicting and comparing reveals gaps in understanding
- **Productive failure**: Research shows attempting before instruction produces better learning than passive study

## Quick Example

**Traditional "Tell-First" approach:**
```
Python uses the def keyword to define functions. Here's the syntax:

def function_name(parameters):
    # function body
    return result
```

**Try-First-Tell-Later approach:**
```
\begin{exercise}
  How would you create a reusable piece of code in Python that
  takes inputs and returns a result? What keyword might make sense?
  Think about it before continuing.
\end{exercise}

Python uses the def keyword to define functions...
[Then show syntax and compare with their thinking]
```

The second approach activates prior knowledge, creates cognitive engagement, and sets up contrast between their prediction and the actual syntax.

## Seven Implementation Patterns

Use different prompt types to engage students before providing explanations:

1. **Prediction Prompts**: "What do you think will happen if...?"
2. **Design/Solution Prompts**: "How would you...?" or "How could you implement...?"
3. **Conceptual Definition Prompts**: "What is...? Try to formulate your own definition before..."
4. **Reasoning Prompts**: "Why do you think...?" or "Varför tror du...?"
5. **Comparison Prompts**: "Jämför..." or "Which differences do you see...?"
6. **Reflection Prompts**: "Reflektera över..." or "What advantages/disadvantages do you see...?"
7. **Experimentation Prompts**: "Prova!" or "Write a program that..."

**For detailed implementation guidance, examples, and LaTeX/Beamer templates, see `patterns.md`.**

## Typical Flow

```
Context → Prompt to Try/Predict → [Student thinking] →
Explanation → Explicit contrast → Highlight critical aspects
```

## Guidelines for Effective Use

### When to Use Try-First Prompts

**Ideal situations**:
- Concepts students can partially reason about from prior knowledge
- Situations with intuitive but incorrect predictions
- Design decisions with multiple reasonable approaches
- Conventions or patterns with underlying rationale
- Comparisons where differences aren't immediately obvious

**Less suitable situations**:
- Completely novel concepts with no prior knowledge base
- Arbitrary facts with no logical derivation
- Situations where frustration would outweigh benefit

### Crafting Effective Prompts

**Good prompts**:
- Are specific enough to guide thinking
- Build on accessible prior knowledge
- Have clear expectations ("try to formulate", "think through", "compare")
- Include explicit invitation to think before continuing
- Are genuinely worth thinking about (not trivial)

**Avoid**:
- Questions with obvious answers (wastes cognitive effort)
- Questions requiring knowledge students can't possibly have
- Prompts without clear follow-through explanation
- Too many prompts in succession (creates fatigue)

### The Critical Follow-Through

**Always**:
- Provide the explanation/answer after the prompt
- Explicitly acknowledge and contrast student thinking
- Validate correct intuitions while correcting misconceptions
- Show why the correct answer matters
- Make critical aspects visible through the contrast

**Never**:
- Ask questions without providing answers
- Skip the explanation assuming students "figured it out"
- Dismiss student predictions as simply wrong without explanation
- Fail to highlight what they should learn from the contrast

## Variation Theory Integration

This approach creates specific variation patterns:

**Student Attempt → Expert Explanation**
- Variant: The approach/understanding
- Invariant: The problem/concept
- Discernment: Critical aspects of expert approach vs. naive approach

**Prediction → Reality**
- Variant: Expected vs. actual behavior
- Invariant: The code/system/concept
- Discernment: Critical aspects that cause the actual behavior

**Multiple Student Approaches → Canonical Solution**
- Variant: Different solution strategies
- Invariant: The problem requirements
- Discernment: Critical aspects that make the canonical solution effective

**For detailed examples from actual teaching practice, including Python classes, operator overloading, and fraction arithmetic with LaTeX/Beamer code, see `examples.md`.**

## Key Principles Summary

1. **Always ask before telling** - Engage prediction/attempt before explanation
2. **Make thinking explicit** - Use phrases like "tänk igenom innan du fortsätter"
3. **Provide genuine answers** - Never leave prompts unresolved
4. **Highlight the contrast** - Explicitly compare prediction with reality
5. **Build on prior knowledge** - Ask questions students can partially answer
6. **Vary the prompt types** - Use prediction, design, reflection, comparison, etc.
7. **Connect to critical aspects** - Use the contrast to highlight what matters
8. **Create safe failure** - Frame attempts as learning opportunities, not tests

## Supporting Files

- **`patterns.md`**: Detailed implementation guidance for all seven prompt types, LaTeX/Beamer templates, and markdown examples
- **`examples.md`**: Real examples from Python programming courses showing each pattern in action
- **`references.md`**: Theoretical background on productive failure, retrieval practice, variation theory, and the Socratic method
