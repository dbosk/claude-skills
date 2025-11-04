---
name: try-first-tell-later
description: Structure educational content by prompting learners to think, predict, or try solutions before providing explanations. Creates cognitive engagement through anticipation and enables variation theory's contrast between learner predictions and expert knowledge. Use when writing tutorials, lectures, explanations, or any instructional content.
---

# Try-First-Tell-Later Pedagogy

This skill applies the pedagogical principle of engaging learners' thinking **before** presenting information, creating active learning through anticipation, prediction, and self-directed problem-solving.

## Core Principle

**Ask students to think, predict, or attempt solutions BEFORE providing the answer or explanation.**

Rather than presenting information first and then asking students to apply it, this approach:
- Poses questions or challenges that students attempt with their existing knowledge
- Prompts predictions about what will happen or what solution might work
- Asks for reflection on concepts before introducing them formally
- Encourages comparison of approaches before revealing the canonical solution

## Theoretical Foundation

### Connection to Variation Theory

This approach creates powerful learning opportunities through variation theory's patterns:

**1. Contrast Through Prediction**
- Students first contrast known approaches with unknown problems
- When the explanation follows, they contrast their initial thinking with expert knowledge
- This double contrast enhances discernment of critical aspects

**2. Separation of Critical Aspects**
- By trying first, students experience which aspects they can already handle (invariant) versus which aspects they struggle with (variant)
- This naturally separates critical aspects that require attention

**3. Active Engagement with Patterns**
- Attempting before learning makes students aware of patterns they already recognize
- Subsequent instruction highlights patterns they missed
- This creates variation in pattern recognition itself

### Cognitive Benefits

**Productive Failure**: Research shows that attempting problems before instruction, even unsuccessfully, produces better learning outcomes than passive study

**Retrieval Practice**: Trying to solve problems activates retrieval processes that strengthen memory and understanding

**Metacognitive Awareness**: Predicting and then comparing creates awareness of gaps in understanding

**Schema Activation**: Attempting activates relevant prior knowledge, making new information easier to integrate

## Implementation Patterns

### 1. Prediction Prompts

Ask students to predict outcomes, behaviors, or solutions before showing them.

**Pattern**: "What do you think will happen if...?"

**Examples from practice**:
- "Vad tror du händer om du försöker läsa ett fält som inte finns för en person?"
- "Hur tror du vi kan läsa information från en Person-instans?"
- "Vad tror du `__str__()`-metoden gör?"

**Implementation**:
```
Before introducing a concept:
1. Present a concrete scenario or code example
2. Ask students to predict the outcome or behavior
3. Encourage them to articulate their reasoning
4. THEN provide the explanation and actual answer
5. Explicitly contrast their prediction with the reality
```

### 2. Design/Solution Prompts

Ask students to attempt designing a solution before showing the standard approach.

**Pattern**: "How would you...?" or "How could you implement...?"

**Examples from practice**:
- "Hur skulle du modifiera programmet ovan för att även lagra adresser? Tänk igenom strukturen innan du fortsätter läsa."
- "Om du skulle skapa en PersonNick-klass som är precis som Person men också har ett smeknamn, hur skulle du göra det?"
- "Hur kan vi implementera multiplikation av två bråk?"

**Implementation**:
```
Before showing a solution:
1. Describe the problem or requirement clearly
2. Ask students to think through their own approach
3. Optionally: Ask them to consider multiple approaches
4. Encourage "thinking through before continuing to read"
5. THEN present the standard/expert solution
6. Compare approaches, highlighting trade-offs
```

### 3. Conceptual Definition Prompts

Ask students to formulate their own definitions before providing formal ones.

**Pattern**: "What is...?" or "Try to formulate your own definition before..."

**Examples from practice**:
- "Vad är en klass och vad är ett objekt? Varför vi behöver två olika begrepp i överhuvudtaget? Försök att formulera dina egna definitioner innan du fortsätter läsa."
- "Vad är skillnaden mellan attribut och metoder i en klass? Försök att formulera dina egna definitioner innan du fortsätter läsa."

**Implementation**:
```
Before defining a concept:
1. Ask students to formulate their own understanding
2. Explicitly request they do this "before continuing to read"
3. Optionally: Provide familiar examples to ground thinking
4. THEN provide the formal definition
5. Show how the formal definition captures (or extends) their intuition
```

### 4. Reasoning Prompts

Ask students to reason about causes, implications, or connections.

**Pattern**: "Why do you think...?" or "Varför tror du...?"

**Examples from practice**:
- "Varför tror du att attributen börjar med dubbla understreck (`__`)? Vad betyder detta i Python?"
- "Varför tror du det är bra att inte kunna komma åt attributen direkt? Vad skulle kunna gå fel om vi tillät det?"
- "Varför tror du det är användbart att kunna jämföra objekt med operatorer som `<` och `==`? Ge ett exempel på när detta skulle vara praktiskt."

**Implementation**:
```
Before explaining rationale:
1. Present a design decision, convention, or pattern
2. Ask why it exists or what purpose it serves
3. Encourage connection to their experience
4. THEN explain the actual reasoning
5. Validate correct intuitions, correct misconceptions
```

### 5. Comparison Prompts

Ask students to compare approaches, options, or examples before explaining differences.

**Pattern**: "Jämför..." or "Vilka skillnader ser du...?"

**Examples from practice**:
- "Jämför koden för att skapa personer i de två exemplen. Vilka skillnader ser du? Vilket sätt tycker du är tydligare och varför?"
- "Vilka problem kan du se med denna approach? Tänk på: [specific aspects]"

**Implementation**:
```
Before analyzing differences:
1. Present two or more alternatives side-by-side
2. Ask students to identify differences
3. Ask them to evaluate trade-offs
4. THEN provide expert analysis
5. Show critical aspects they might have missed
```

### 6. Reflection Prompts

Ask students to reflect on broader implications, advantages, or applications.

**Pattern**: "Reflektera över..." or "Vilka fördelar/nackdelar ser du...?"

**Examples from practice**:
- "Reflektera över fördelarna med arv: När skulle det vara lämpligt att använda arv? När skulle det vara bättre att skapa en helt ny klass istället?"
- "Vilka fördelar ser du med att använda klasser jämfört med uppslagslistor? Lista minst tre fördelar."

**Implementation**:
```
After introducing a concept:
1. Ask students to step back and consider implications
2. Prompt analysis of when/why to use the approach
3. Encourage connection to principles or patterns
4. THEN provide expert perspective
5. Synthesize their insights with broader framework
```

### 7. Experimentation Prompts

Encourage students to try something themselves before showing the result.

**Pattern**: "Prova!" or "Skriv ett program som..."

**Examples from practice**:
- Exercise blocks that ask students to write programs before showing solutions
- "(Prova!)" annotations encouraging hands-on experimentation
- Problems to solve before revealing implementations

**Implementation**:
```
Before showing working code:
1. Present clear requirements or goal
2. Provide enough context but not full solution
3. Encourage actual implementation attempt
4. THEN show the complete solution
5. Compare their approach with shown solution
```

## Structuring Educational Materials

### Typical Flow Pattern

```
1. Context/Scenario
   ↓
2. Prompt to Predict/Try/Reflect
   ↓
3. Space for student thinking
   ↓
4. Explanation/Answer
   ↓
5. Explicit contrast between prediction and reality
   ↓
6. Deeper explanation of critical aspects
```

### LaTeX/Beamer Implementation

When writing LaTeX slides or notes, use this structure:

```latex
% 1. Set context
Vi har sett hur... Nu ska vi...

% 2. Exercise/prediction prompt
\begin{exercise}
  Hur skulle du...? / Vad tror du...?
  Tänk igenom innan du fortsätter läsa.
\end{exercise}

% 3. Space (implicit - student pauses)

% 4. Answer/explanation
Svaret är att... / Vi kan göra detta genom att...

% 5. Contrast and deeper explanation
Notera att... / Detta skiljer sig från... /
Här ser vi att...
```

### Markdown/Text Implementation

```markdown
## Topic

Brief context setting...

**Think about this first**: How would you...? What do you think happens when...?

[student thinking space]

### The Answer

Here's how it actually works...

**Comparing your thinking**: You might have thought... But actually...
This is because...
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

## Examples from Practice

### Example 1: Predicting Behavior

```
Context: Students have seen dictionary access with phonebook["name"]

Prompt: "Vad händer om du försöker läsa ett fält som inte finns
för en person? Vilket fel kommer du att få?"

[student thinks]

Answer: "Svaret är att du får ett KeyError."

Explanation: "Detta måste vi hantera när vi läser informationen.
Låt oss se hur koden för att läsa informationen blir..."
```

**Variation created**:
- Student predicts based on prior knowledge
- Reality shows specific Python behavior
- Contrast highlights the critical aspect: missing keys raise exceptions

### Example 2: Design Challenge

```
Context: Phone book program that stores names and phone numbers

Prompt: "Hur skulle du modifiera programmet ovan för att även
lagra adresser? Tänk igenom strukturen innan du fortsätter läsa."

[student thinks through nested dictionaries, lists, etc.]

Answer: "Ett första försök skulle kunna vara att använda en
nästlad uppslagslista..."

Explanation: Shows the nested dictionary approach, then reveals
its problems, then shows class-based solution

Follow-up: "Vilka problem kan du se med denna approach?"
```

**Variation created**:
- Student tries to extend simple dictionary
- Multiple approaches shown (nested dict vs. classes)
- Contrast highlights critical aspects: structure, maintainability, error handling

### Example 3: Conceptual Understanding

```
Prompt: "Vad är en klass och vad är ett objekt? Varför vi behöver
två olika begrepp i överhuvudtaget? Försök att formulera dina
egna definitioner innan du fortsätter läsa."

[student formulates intuitive understanding]

Answer: "Klassen är som ritningen av huset: den beskriver hur
huset ska se ut... Objekten är de faktiska husen som byggs
enligt ritningen."

Explanation: Formal definitions with blueprint metaphor,
then code examples
```

**Variation created**:
- Student's informal understanding
- Expert definition with metaphor
- Contrast highlights critical aspect: specification vs. instance

## Key Principles Summary

1. **Always ask before telling** - Engage prediction/attempt before explanation
2. **Make thinking explicit** - Use phrases like "tänk igenom innan du fortsätter"
3. **Provide genuine answers** - Never leave prompts unresolved
4. **Highlight the contrast** - Explicitly compare prediction with reality
5. **Build on prior knowledge** - Ask questions students can partially answer
6. **Vary the prompt types** - Use prediction, design, reflection, comparison, etc.
7. **Connect to critical aspects** - Use the contrast to highlight what matters
8. **Create safe failure** - Frame attempts as learning opportunities, not tests

## References

This approach integrates:

**Productive Failure**:
- Kapur, M. (2008). Productive failure. *Cognition and Instruction*, 26(3), 379-424.
- Kapur, M., & Bielaczyc, K. (2012). Designing for productive failure. *Journal of the Learning Sciences*, 21(1), 45-83.

**Testing Effect / Retrieval Practice**:
- Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. *Psychological Science*, 17(3), 249-255.
- Bjork, R. A., & Bjork, E. L. (2011). Making things hard on yourself, but in a good way. In M. A. Gernsbacher et al. (Eds.), *Psychology and the real world* (pp. 56-64). Worth Publishers.

**Variation Theory**:
- Marton, F., & Pang, M. F. (2006). On Some Necessary Conditions of Learning. *Journal of the Learning Sciences*, 15(2), 193-220.
- Marton, F. (2015). *Necessary Conditions of Learning*. London: Routledge.

**Socratic Method**:
- Paul, R., & Elder, L. (2007). *The Thinker's Guide to the Art of Socratic Questioning*. Foundation for Critical Thinking.
