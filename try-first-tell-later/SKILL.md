---
name: try-first-tell-later
description: Structure educational content using try-first-tell-later pedagogy where students predict, attempt, or reflect before receiving explanations. Creates active learning through cognitive engagement and variation theory's contrast patterns. Use when writing educational materials, designing exercises, creating lecture notes, structuring tutorials, writing teaching examples with LaTeX/Beamer or Mentipy, developing problem sets, or when user mentions try-first, predict-first, productive failure, Socratic method, question-before-answer, exercise-driven learning, inquiry-based teaching, polls, or interactive slide questions.
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

## The Teacher's Paradox and Assessment

### The Teacher's Paradox

Marton identifies a fundamental tension in teaching:

> "[T]he more the teacher does to enable the students to answer the questions asked, to solve the problems given, the fewer opportunities may be left for the students to learn to understand that which they are expected to learn to understand. The reason is that the more clearly the teacher tells the students what is to be done, the less chance the students get to make the necessary distinctions (for instance, between what is critical and what is not)." (NCOL, p. 13)

**Implication**: Try-first prompts should NOT reveal which aspects are critical. Students must discern this themselves.

### Try-First as Diagnostic Pre-Test

Try-first prompts serve a dual purpose:

1. **Learning function**: Engages prediction, activates prior knowledge, creates contrast
2. **Diagnostic function**: Reveals which critical aspects students can already discern

**Key insight** (Marton, NCOL p. 89):
> "If we want to find out to what extent they have learned to do so, we should not point out those aspects for them but let the students discern them by themselves."

And the rule for the question itself (NCOL p. 91, on the physics-exam task whose aspects "all are pointed out in the question"):
> "[T]he questions should not point out the relevant aspects of the problem to be solved, as this is exactly what the students are supposed to find out (discern)."

(Pages 13, 89 and 91 verified against the printed book, 2026-09-06; cite them as `\parencite[s.~13 och 89]{Marton2015}` or with p. 91 when the prompt-design rule is the point.)

**Use try-first prompts to diagnose**:
- Which critical aspects students already discern
- Which aspects need teaching (require variation patterns)
- Common misconceptions to address

### Designing Questions That Don't Reveal Critical Aspects

**BAD example** (Swedish national physics exam):
> "A ball falls and is affected by air braking force F = kv where k = 0.32 N·s/m. The ball's mass is 0.20 kg. What is the final velocity?"

**Problem**: All critical aspects are given. Students just calculate—no discernment needed.

**GOOD example** (Johansson, Marton, Svensson 1985):
> "A car is driven at a high constant speed on a motorway. What forces act on the car?"

**Why better**: Students must discern:
- That "constant speed" implies balanced forces
- Which forces are relevant
- That "engine pushes forward" alone is wrong

**The reveal hides in three more places**: the example's *title* ("Ett program
med ett stavfel" names the bug --- write "Ett program med ett fel"), the *lead-in*,
and the program's own *payload*. A program printing "Den här raden hinner köras."
narrates the answer before the student predicts it; print "Välkommen!" and let
them discern what ran. Keep the question open --- "Vad skriver programmet ut?", not
"Vad är felet?" --- so the critical aspect can surface in the answers without being
pointed at. See `references/patterns.md`, "The payload must not narrate the answer".

**Predict the output only to test a misconception (author, 2026-10-29).**
A predict-the-output exercise ("Vad skriver programmet ut?") hands the
student the program, so the student only reads it. Use one when the
prediction is meant to expose a particular misconception, and name that
misconception in its `\ltnote`. Otherwise the exercise has the student
write the program, applying what they already know to find out something
new ("Skriv en funktion som …", "Undersök det i Python, med `vars` och
`dir`"); it says what to find out and which tools to use, not the
algorithm or the name of the answer, and the program that would have
been given becomes the worked answer after the attempt. The author's ink
beside such an exercise: "We don't want exercises like this unless it's
for testing a particular misconception. Here we have a learning objective
that they should be able to apply previous knowledge to discover new
things. The exercise should make them try to write this program on their
own." And beside one that named the attribute to find and gave the probe
program: "The exercise tells all, let them look for it and find
`__class__` themselves first."

**Names and pairing (author, 2026-09-15).** File, chunk and example names
are part of the question too: `defined-only.py` beside
`defined-and-called.py`, or `return-value.py` beside `print-value.py`,
name the very contrast the exercise asks the student to find — "the names
make the discernment for the students". Name such programs neutrally
(`greet1.py`, `greet2.py`; `return1.py`, `return2.py`) and let the
`\ltnote` carry the rationale. And a contrast pair is *one* exercise
holding both programs ("Vad skriver vart och ett av dem ut?"), never two
consecutive exercises ("Vad skriver programmet ut?" / "Och det här?"):
"we don't want to make the discernment for the student — merge into one
exercise, since we want to compare them". The answer frame showing both
outputs follows as before; the lead-in does not say what differs.
When the second program may only appear *after* the prediction and the
first is by then far behind, the answer re-displays the first beside the
second (variation-theory skill, "Why contrast must come first").

**Write the invariant once (author, 2026-09-22).** When the two cases
differ only in a call, an argument or one line, put them in *one* program:
the shared part (the function) written once, then both calls. "Merge them
into one file so that we can see more easily that the function is the
same in both" — two copies make the reader compare them line by line to
find that they are identical, which is work the contrast should not cost.
Keep two programs only when the cases cannot coexist in one file (one of
them crashes before the other runs, or lacks a definition the other has).

**Show every premise (author, 2026-10-19).** The other side of the
Teacher's paradox: a predict-first question must be answerable from what
has been shown. Hide the critical aspect, never a premise. A premise may
sit on an earlier slide of the same section when the stem points at it
("klassen Account från förra bilden"). What is never allowed is an
option, right or wrong, that rests on something shown nowhere before the
question: a default parameter value, a base class's methods or a
`__str__` revealed only in the answer or never, or a chunk defined later.
The author's ink: "Since we don't know about the interest we can't choose
an option: 816 and 820 are both plausible"; "For this we must see what
methods SavingsAccount has." Put the premise in the code
(`SavingsAccount("1003", "Madicken", 1000, rate=0.02)`), not only in the
stem's prose. Steps: `references/patterns.md`, "Writing a poll".

### Section Order: Ask, Show, Explain, Define

A section that opens with a definition is tell-first even when an exercise
follows: the definition has already pointed out the critical aspect, so
nothing is left to discern (NCOL p. 13). The order that lets the student
discern is

1. **exercise** — a program or case to predict, whose lead-in presupposes
   nothing the definition would introduce and reveals nothing of the
   answer ("Programmets två utskriftsrader ser nästan lika ut. Skriv ner
   vad var och en av dem skriver ut."), not ("Lägg märke till att 5 och
   "5" inte är samma sak: vad skriver programmet ut?");
2. **output** — the real run, in the same example environment;
3. **explanation** — what varied and what that reveals;
4. **definition** — last, naming what the student has now met.

A behavioural claim that stands only in prose ("ett anrop ovanför
definitionen ger NameError", "en funktion utan return lämnar None") is
tell-only: give it the same exercise-then-run pair as everything else, and
move the explaining sentence after the run (author, 2026-09-15: "Another
exercise + example showing that!").

Reordering an existing section usually breaks one paragraph: the lead-in
that referred forward to the definition ("de två sista exemplen i
definitionen") must be rewritten as the try-first prompt, not moved. Record
the ordering decision in an `\ltnote` citing NCOL pp. 13, 89 and 91 (course
author's request, 2026-09-06).

### Prompt Design Checklist

- [ ] Does my question require discerning critical aspects, or point them out?
- [ ] Could this serve as a pre-test to reveal student understanding?
- [ ] Am I avoiding giving away "what matters" in the question?
- [ ] Will responses reveal which critical aspects students see/miss?
- [ ] Can each option be decided from what has been shown
      (`references/patterns.md`, "Writing a poll")?

### Connection to Variation Theory

Try-first prompts and variation theory work together:
1. **Try-first reveals** which critical aspects students cannot yet discern
2. **Variation patterns** then target those specific aspects
3. **Post-test try-first** confirms students now discern the aspects

See the variation-theory skill for designing appropriate patterns once diagnostic results are known.

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

**For detailed implementation guidance, examples, and LaTeX/Beamer templates, see `references/patterns.md`.**

## Mentipy as a Delivery Mechanism

Mentipy fits naturally when try-first prompts should be answered live in
slides or handouts.  Use `mc` for constrained predictions, `scale` for quick
self-assessment or confidence checks, `open_text` for short reflections,
`word_cloud` for brainstorming prior knowledge, `ranking` for ordering
steps, and `pin_text` for "point at the bug" in code.  A prediction about
a program carries the program as `context=`, so students read it on the
phone right under the options.  This works well for brief
diagnostic questions before explanation, especially when the goal is to make
student thinking visible without revealing the critical aspect too early.
An `mc` poll's stem and options follow "Writing a poll" in
`references/patterns.md`.  For writing, building and running the poll,
load the `mentipy` skill.

## Typical Flow

```
Context → Prompt to Try/Predict → [Student thinking] →
Explanation → Explicit contrast → Highlight critical aspects
```

## The Example-Question-Contrast Pattern

Show a problem example, ask a try-first question about it, show the
modified approach, then discuss the contrast. Template with a worked
LaTeX/Beamer example: `references/patterns.md`, "The
Example-Question-Contrast Pattern".

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

### Using Try-First for Diagnostic Assessment

**Before teaching a topic**:
1. Pose open-ended try-first question (without revealing critical aspects)
2. Analyze responses: which critical aspects do students mention?
3. Focus subsequent teaching on missing aspects using variation patterns

**Analyzing student responses**:
- Students who mention the critical aspect → ready for generalization/fusion
- Students who miss the critical aspect → need contrast patterns first
- Common wrong answers → reveal misconceptions to address

**After teaching** (post-test):
- Use same or similar prompt
- Compare responses to pre-test
- Students should now discern the critical aspects

**See `references/patterns.md` for detailed implementation guidance on diagnostic use.**

### Crafting Effective Discovery Questions

**Core principle**: Questions should guide students to discover what you would otherwise tell them.

**Question types by purpose**:

1. **Prediction questions**: "What could go wrong if...?"
   - Example: "What happens if we forget to close a file?"
   - Purpose: Activate thinking about edge cases and failure modes

2. **Comparison questions**: "When would approach A be better than B?"
   - Example: "When would `read()` be better than line-by-line iteration? Consider memory."
   - Purpose: Guide discrimination between similar approaches

3. **Design questions**: "How should X be implemented? Function or method? Why?"
   - Example: "How should `open()` be implemented? What should it return?"
   - Purpose: Engage architectural thinking before revealing design

4. **Exploration questions**: "What problems might arise with this approach?"
   - Example: "What problems could arise with comma-separated format?"
   - Purpose: Discover limitations through attempted use

**Quality criteria for discovery questions**:
- **Specific enough to guide thinking**: Not "What do you think?" but "What happens to original file if transformation fails?"
- **Open enough to allow discovery**: Multiple valid partial answers
- **Connected to upcoming content**: Answer will be provided soon
- **Build on prior knowledge**: Students have tools to partially answer

**Avoid**:
- Questions with obvious answers (wastes cognitive effort)
- Questions requiring knowledge students can't possibly have
- Prompts without clear follow-through explanation
- Too many prompts in succession (creates fatigue)

### Layered Question Sequences

Questions can build on each other: recognition, exploration,
implementation, understanding. Worked example: `references/patterns.md`,
"Layered Question Sequences".

### Write exercises as prose, not bullets

An `exercise`/`activity` body is prose — the question stated as sentences.
Do **not** wrap a single question in `\begin{itemize}\item …\end{itemize}`;
that renders as a lone orphan bullet (ugly on a slide, and it breaks the
prose flow of the notes in a dual beamer/article deck). Use a real list
only for genuinely multiple sub-questions, and frame it with prose. See the
latex-writing and didactic-notes skills for the single-item-list
anti-pattern and article-prose guidance.

```latex
% BAD — lone bullet
\begin{exercise}
  \begin{itemize}
    \item What varies in the pancake-batter example?
  \end{itemize}
\end{exercise}

% GOOD — prose
\begin{exercise}
  What varies in the pancake-batter example?
\end{exercise}
```

### exercise vs activity Environments

**exercise environment**: Short conceptual questions requiring thought but not code execution

**Characteristics**:
- Quick to answer (1-2 minutes of thinking)
- Conceptual or analytical
- No coding required
- Activates prediction or reasoning

**Examples**:
```latex
\begin{exercise}
  Why might files require explicit open/close but terminal I/O doesn't?
\end{exercise}

\begin{exercise}
  What advantages does validating file existence BEFORE opening provide
  compared to catching exceptions AFTER?
\end{exercise}
```

**activity environment**: Hands-on tasks requiring actual coding or exploration

**Characteristics**:
- Takes substantial time (10+ minutes)
- Requires writing code or exploring tools
- Produces artifacts (programs, data files)
- Often followed by discussion of discoveries

**Examples**:
```latex
\begin{activity}[SCB Namnsök]
  Visit SCB Namnsök, download the statistics file, and write a program
  that implements the same functionality as the website.

  What challenges did you encounter with the file format?
\end{activity}

\begin{activity}[Explore CSV module]
  Try using Python's \mintinline{python}{csv} module to read and write
  a file with your own data. Compare with manual string splitting.
\end{activity}
```

**Guideline**: Use `exercise` for quick discovery moments embedded in instruction, `activity` for deeper exploration requiring implementation.

### The Critical Follow-Through

**Always**:
- Provide the explanation/answer after the prompt
- Explicitly acknowledge and contrast student thinking
- Validate correct intuitions while correcting misconceptions
- Show why the correct answer matters
- Make critical aspects visible through the contrast
- Say in the prose what a run has just exposed, especially a limitation
  of the tool being presented: after `"-5".isdigit()` and
  `"1.75".isdigit()` print `False`, write "men vi ser här att det kan
  vara svårt att testa rätt" (author, 2026-09-22) instead of leaving the
  reader to draw the conclusion

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

**For detailed examples from actual teaching practice, including Python classes, operator overloading, and fraction arithmetic with LaTeX/Beamer code, see `references/examples.md`.**

## Key Principles Summary

1. **Always ask before telling** - Engage prediction/attempt before explanation
2. **Make thinking explicit** - Use phrases like "tänk igenom innan du fortsätter"
3. **Provide genuine answers** - Never leave prompts unresolved
4. **Highlight the contrast** - Explicitly compare prediction with reality
5. **Build on prior knowledge** - Ask questions students can partially answer
6. **Vary the prompt types** - Use prediction, design, reflection, comparison, etc.
7. **Connect to critical aspects** - Use the contrast to highlight what matters
8. **Create safe failure** - Frame attempts as learning opportunities, not tests

## Reference Files

This skill includes detailed references in `references/`:

| File | Content | Search patterns |
|------|---------|-----------------|
| `patterns.md` | Implementation guidance for all seven prompt types, LaTeX/Beamer templates, the Example-Question-Contrast and layered sequences, writing a poll | `exercise`, `activity`, `\begin{exercise}`, `Writing a poll` |
| `examples.md` | Real examples from Python programming courses | `Python`, `class`, `fraction` |
| `theoretical-background.md` | Productive failure, retrieval practice, variation theory | `Kapur`, `Socratic`, `research` |
