---
name: canvas-quiz
description: |
  Write and review Canvas LMS quiz JSON files (INL1Quiz-*.json) for the tilkry
  cryptography course. Use proactively when: (1) creating, editing, or
  reviewing INL1Quiz JSON files, (2) user asks to write quiz questions for a
  lecture topic, (3) user asks to review quiz quality, redundancy, or distractor
  balance, (4) user mentions Canvas quiz, INL1Quiz, quiz JSON, or quiz
  questions. Covers JSON structure, question design, scoring, redundancy
  analysis, and validation.
---

# Canvas Quiz Authoring

## Overview

Write and review Canvas LMS quizzes stored as `INL1Quiz-<topic>.json` files.
These quizzes use AllOrNothing scoring, require 100% to pass, allow unlimited
retakes with a 1-hour cooldown, and test conceptual understanding of
cryptography topics.

## File Naming and Location

- Pattern: `modules/week-N/INL1Quiz-<topic>.json`
- Examples: `INL1Quiz-ciphers.json`, `INL1Quiz-zkp.json`, `INL1Quiz-mpc.json`

## Up-to-Date Format Reference

The `canvaslms` CLI provides canonical, up-to-date JSON examples. Run these
to get the latest format (always in sync with the tool):

```bash
canvaslms quizzes create --example      # Full quiz envelope + all settings
canvaslms quizzes items add --example   # All question types with examples
```

These show every supported question type (`choice`, `multi-answer`, `matching`,
`true-false`, `ordering`, `rich-fill-blank`, `essay`, `file-upload`,
`formula`) with correct `scoring_data` structure for each.

## JSON Structure

### Quiz Envelope

```json
{
  "quiz_type": "new",
  "settings": {
    "title": "INL1Quiz <Topic Name>",
    "instructions": "<HTML instructions>",
    "...other settings..."
  },
  "items": [ ]
}
```

Copy `settings` verbatim from an existing quiz file. Only change
`settings.title`. For the canonical settings block, see
`references/quiz-settings.json`.

### Multi-Answer Question (primary format)

```json
{
  "position": 1,
  "points_possible": 1.0,
  "entry": {
    "title": "Short Descriptive Title",
    "item_body": "<p>Check all statements that are true about [topic].</p>",
    "interaction_type_slug": "multi-answer",
    "scoring_algorithm": "AllOrNothing",
    "properties": {
      "shuffle_rules": {
        "choices": {
          "to_lock": [],
          "shuffled": false
        }
      }
    },
    "interaction_data": {
      "choices": [
        {
          "position": 1,
          "item_body": "<p>Statement text here.</p>"
        }
      ]
    },
    "scoring_data": {
      "value": [1, 3, 5]
    }
  }
}
```

**Critical**: `scoring_data.value` lists **position numbers** (1-indexed)
of correct choices. Every value must match a choice position in
`interaction_data.choices`.

### Matching Question (for format variety)

```json
{
  "position": 1,
  "points_possible": 1.0,
  "entry": {
    "title": "Match Properties",
    "item_body": "<div>Match terms with definitions.</div>",
    "interaction_type_slug": "matching",
    "scoring_algorithm": "DeepEquals",
    "properties": {
      "shuffle_rules": {
        "questions": { "shuffled": false }
      }
    },
    "interaction_data": {
      "answers": ["Definition A", "Definition B"],
      "questions": [
        { "item_body": "Term A" },
        { "item_body": "Term B" }
      ]
    },
    "scoring_data": {
      "value": {
        "<uuid-for-term-A>": "Definition A",
        "<uuid-for-term-B>": "Definition B"
      },
      "edit_data": {
        "matches": [
          {
            "answer_body": "Definition A",
            "question_id": "<uuid-for-term-A>",
            "question_body": "Term A"
          }
        ],
        "distractors": []
      }
    }
  }
}
```

Generate fresh v4 UUIDs for each `question_id`. Ensure `scoring_data.value`
maps each UUID to the correct answer and `edit_data.matches` mirrors the
mapping.

## Question Design Principles

### Target 6-8 Questions Per Quiz

Each quiz should have 6-8 questions covering different aspects of the topic.

### Cognitive Levels (aim for a mix)

1. **Definitional**: Match terms with definitions
2. **Mechanical**: Protocol steps, equations, verification
3. **Conceptual**: What a property guarantees, implications
4. **Applied**: Concrete scenario, what happens?
5. **Analytical**: Why does X work / not work?

### Distractor Design

False choices must target **specific misconceptions**:

- "Longer keys prevent side-channel attacks" (confuses algorithmic vs
  implementation security)
- "Semi-honest security implies malicious security" (wrong adversary model
  relationship)
- "Knowledge extraction contradicts zero-knowledge" (confuses who has
  rewinding power)

Avoid obviously wrong distractors like "MPC can only compute simple
functions."

### True/False Ratio

Aim for **55-75% true** choices per question (e.g., 5 true out of 8 choices).
Avoids "default to true" strategy (>80%) and "everything is a trick" feeling
(<40%).

### Contrast Pairs (Variation Theory)

Include choice pairs differing in one critical aspect:

- TRUE: "Privacy guarantees that aside from the output, no additional
  information is revealed"
- FALSE: "Privacy guarantees that no information about inputs is revealed,
  including through the output"

The critical aspect: privacy is *relative to the output*, not absolute.

### Matching Distractors

Matching questions can include extra answers that don't match any term. Add
them to the `answers` array and the `distractors` list in `edit_data`:

```json
"interaction_data": {
  "answers": ["Stockholm", "Oslo", "Copenhagen", "Helsinki", "Berlin"],
  "questions": [
    { "id": "q1", "item_body": "Sweden" },
    { "id": "q2", "item_body": "Norway" }
  ]
},
"scoring_data": {
  "edit_data": {
    "matches": [ ... ],
    "distractors": ["Berlin"]
  }
}
```

### Format Variety

Include at least one non-multi-answer question per quiz. Available types:
- `multi-answer` with `AllOrNothing` — "select all true" (primary)
- `matching` with `DeepEquals` — match terms to definitions
- `choice` with `Equivalence` — single correct answer from choices
- `true-false` with `Equivalence` — true/false statement
- `ordering` with `DeepEquals` — arrange items in correct order

Run `canvaslms quizzes items add --example` for JSON examples of each type.

## Redundancy Analysis

### Within a Quiz

1. Do multiple questions test the **same definitional knowledge** in different
   formats? (Redundant unless testing genuinely different aspects.)
2. Is the same property tested in more than two questions? (Likely redundant.)
3. Do questions describe the same protocol steps? (Acceptable only if testing
   different aspects: commitment properties vs protocol flow vs simulation.)

### Across Quizzes (students take all quizzes in a week)

1. Does a quiz include content from another topic's quiz? (e.g., ZKPK
   properties in an MPC quiz — redundant.)
2. Are the same examples reused without new insight?

### Acceptable Overlap

- Different cognitive levels (definition vs application)
- Different protocol aspects (commitment vs verification vs simulation)
- Progression (general concept early, specific nuance later)

## Validation

After editing quiz JSON, **always** run the validation script:

```bash
python3 ~/.claude/skills/canvas-quiz/scripts/validate_quiz.py <quiz-file.json>
```

To validate multiple files:

```bash
python3 ~/.claude/skills/canvas-quiz/scripts/validate_quiz.py modules/week-3/INL1Quiz-*.json
```

The script checks: valid JSON, required fields, scoring data consistency,
true/false ratios, and prints a per-question summary.

## Canvas Push Workflow

After editing:

```bash
cd modules/week-N
make push-quizzes-questions       # Push with question replacement
make force-push-quizzes-questions  # Force push (ignores timestamps)
```

## Resources

| File | Content |
|------|---------|
| `scripts/validate_quiz.py` | Validates quiz JSON structure and scoring data |
| `references/quiz-settings.json` | Canonical quiz_settings block to reuse |
