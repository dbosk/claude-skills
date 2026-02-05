#!/usr/bin/env python3
"""
Validate Canvas LMS quiz JSON files (INL1Quiz-*.json).

Checks:
  - Valid JSON syntax
  - Required envelope fields (quiz_type, settings.title, items)
  - Each question has required fields
  - scoring_data.value references valid choice positions (multi-answer)
  - scoring_data matches are consistent (matching questions)
  - True/false ratio warnings (outside 40-80%)
  - Summary statistics per quiz

Usage:
    validate_quiz.py <file.json> [<file2.json> ...]
    validate_quiz.py modules/week-3/INL1Quiz-*.json
"""

import json
import sys
from pathlib import Path


def validate_envelope(data):
    """Check top-level quiz structure."""
    errors = []
    warnings = []

    if "quiz_type" not in data:
        errors.append("Missing top-level 'quiz_type'")

    if "settings" not in data:
        errors.append("Missing top-level 'settings'")
    else:
        if "title" not in data["settings"]:
            errors.append("Missing 'settings.title'")
        if "quiz_settings" not in data["settings"]:
            warnings.append("Missing 'settings.quiz_settings'")

    if "items" not in data:
        errors.append("Missing top-level 'items'")
    elif not isinstance(data["items"], list):
        errors.append("'items' must be a list")
    elif len(data["items"]) == 0:
        warnings.append("Quiz has no questions")

    return errors, warnings


def validate_multi_answer(entry, qnum):
    """Validate a multi-answer question."""
    errors = []
    warnings = []

    choices = entry.get("interaction_data", {}).get("choices", [])
    if not choices:
        errors.append(f"Q{qnum}: No choices in interaction_data")
        return errors, warnings

    choice_positions = {c["position"] for c in choices}
    n_choices = len(choices)

    scoring = entry.get("scoring_data", {}).get("value", [])
    if not isinstance(scoring, list):
        errors.append(f"Q{qnum}: scoring_data.value must be a list "
                      f"for multi-answer, got {type(scoring).__name__}")
        return errors, warnings

    n_correct = len(scoring)

    # Check for orphaned scoring references
    for pos in scoring:
        if pos not in choice_positions:
            errors.append(
                f"Q{qnum}: scoring_data references position {pos} "
                f"but choices only have positions {sorted(choice_positions)}"
            )

    # Check for duplicate positions in choices
    if len(choice_positions) != n_choices:
        errors.append(f"Q{qnum}: Duplicate position numbers in choices")

    # True/false ratio
    if n_choices > 0:
        ratio = n_correct / n_choices
        if ratio > 0.80:
            warnings.append(
                f"Q{qnum}: High true ratio {n_correct}/{n_choices} "
                f"= {ratio:.0%} (target 55-75%)"
            )
        elif ratio < 0.40:
            warnings.append(
                f"Q{qnum}: Low true ratio {n_correct}/{n_choices} "
                f"= {ratio:.0%} (target 55-75%)"
            )

    return errors, warnings


def validate_matching(entry, qnum):
    """Validate a matching question."""
    errors = []
    warnings = []

    idata = entry.get("interaction_data", {})
    answers = idata.get("answers", [])
    questions = idata.get("questions", [])

    if not answers:
        errors.append(f"Q{qnum}: No answers in matching question")
    if not questions:
        errors.append(f"Q{qnum}: No questions in matching question")

    scoring = entry.get("scoring_data", {})
    value = scoring.get("value", {})
    edit_data = scoring.get("edit_data", {})
    matches = edit_data.get("matches", [])

    if not isinstance(value, dict):
        errors.append(f"Q{qnum}: scoring_data.value must be a dict "
                      f"for matching, got {type(value).__name__}")
        return errors, warnings

    # Check that all answer strings in value exist in answers list
    for _uuid, answer in value.items():
        if answer not in answers:
            errors.append(
                f"Q{qnum}: scoring_data.value maps to '{answer}' "
                f"which is not in interaction_data.answers"
            )

    # Check edit_data.matches consistency with value
    if len(matches) != len(value):
        warnings.append(
            f"Q{qnum}: edit_data.matches has {len(matches)} entries "
            f"but scoring_data.value has {len(value)}"
        )

    for match in matches:
        qid = match.get("question_id", "")
        if qid not in value:
            errors.append(
                f"Q{qnum}: edit_data.matches references question_id "
                f"'{qid}' not in scoring_data.value"
            )

    return errors, warnings


def validate_choice(entry, qnum):
    """Validate a single-choice question."""
    errors = []
    warnings = []

    choices = entry.get("interaction_data", {}).get("choices", [])
    if not choices:
        errors.append(f"Q{qnum}: No choices in interaction_data")
        return errors, warnings

    scoring_value = entry.get("scoring_data", {}).get("value")
    if scoring_value is None:
        errors.append(f"Q{qnum}: Missing scoring_data.value")
        return errors, warnings

    # value can be a position number or a UUID string
    if isinstance(scoring_value, int):
        choice_positions = {c["position"] for c in choices}
        if scoring_value not in choice_positions:
            errors.append(
                f"Q{qnum}: scoring_data.value {scoring_value} "
                f"not in choice positions {sorted(choice_positions)}"
            )

    return errors, warnings


def validate_ordering(entry, qnum):
    """Validate an ordering question."""
    errors = []
    warnings = []

    choices = entry.get("interaction_data", {}).get("choices", {})
    if not choices:
        errors.append(f"Q{qnum}: No choices in interaction_data")
        return errors, warnings

    scoring_value = entry.get("scoring_data", {}).get("value", [])
    if not isinstance(scoring_value, list):
        errors.append(f"Q{qnum}: scoring_data.value must be a list "
                      f"for ordering, got {type(scoring_value).__name__}")
        return errors, warnings

    # Check all IDs in scoring exist in choices
    choice_ids = set(choices.keys()) if isinstance(choices, dict) else set()
    for item_id in scoring_value:
        if choice_ids and item_id not in choice_ids:
            errors.append(
                f"Q{qnum}: scoring_data references '{item_id}' "
                f"not in choices"
            )

    return errors, warnings


# Question types that need no special validation beyond required fields
SIMPLE_TYPES = {"true-false", "essay", "file-upload", "formula",
                "rich-fill-blank"}


def validate_item(item, qnum):
    """Validate a single quiz item."""
    errors = []
    warnings = []

    if "position" not in item:
        errors.append(f"Q{qnum}: Missing 'position'")
    if "points_possible" not in item:
        errors.append(f"Q{qnum}: Missing 'points_possible'")

    entry = item.get("entry", {})
    if not entry:
        errors.append(f"Q{qnum}: Missing 'entry'")
        return errors, warnings

    for field in ("title", "item_body", "interaction_type_slug",
                  "scoring_algorithm"):
        if field not in entry:
            errors.append(f"Q{qnum}: Missing entry.{field}")

    itype = entry.get("interaction_type_slug", "")

    if itype == "multi-answer":
        e, w = validate_multi_answer(entry, qnum)
        errors.extend(e)
        warnings.extend(w)
    elif itype == "matching":
        e, w = validate_matching(entry, qnum)
        errors.extend(e)
        warnings.extend(w)
    elif itype == "choice":
        e, w = validate_choice(entry, qnum)
        errors.extend(e)
        warnings.extend(w)
    elif itype == "ordering":
        e, w = validate_ordering(entry, qnum)
        errors.extend(e)
        warnings.extend(w)
    elif itype in SIMPLE_TYPES:
        pass  # No special validation needed
    else:
        warnings.append(f"Q{qnum}: Unknown interaction type '{itype}'")

    return errors, warnings


def validate_quiz(path):
    """Validate a single quiz file. Returns (errors, warnings, stats)."""
    errors = []
    warnings = []
    stats = {}

    # Parse JSON
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"], [], {}
    except FileNotFoundError:
        return [f"File not found: {path}"], [], {}

    # Validate envelope
    e, w = validate_envelope(data)
    errors.extend(e)
    warnings.extend(w)

    items = data.get("items", [])
    stats["title"] = data.get("settings", {}).get("title", "<no title>")
    stats["n_questions"] = len(items)
    stats["questions"] = []

    for item in items:
        qnum = item.get("position", "?")
        e, w = validate_item(item, qnum)
        errors.extend(e)
        warnings.extend(w)

        entry = item.get("entry", {})
        itype = entry.get("interaction_type_slug", "?")
        title = entry.get("title", "<no title>")

        if itype == "multi-answer":
            choices = entry.get("interaction_data", {}).get("choices", [])
            correct = entry.get("scoring_data", {}).get("value", [])
            n_choices = len(choices)
            n_correct = len(correct)
            ratio = (n_correct / n_choices * 100) if n_choices > 0 else 0
            stats["questions"].append({
                "position": qnum,
                "title": title,
                "type": itype,
                "n_choices": n_choices,
                "n_correct": n_correct,
                "ratio": ratio,
            })
        elif itype == "matching":
            questions = entry.get("interaction_data", {}).get("questions", [])
            answers = entry.get("interaction_data", {}).get("answers", [])
            distractors = entry.get("scoring_data", {}).get(
                "edit_data", {}).get("distractors", [])
            stats["questions"].append({
                "position": qnum,
                "title": title,
                "type": itype,
                "n_pairs": len(questions),
                "n_distractors": len(distractors),
                "n_answers": len(answers),
            })
        elif itype == "choice":
            choices = entry.get("interaction_data", {}).get("choices", [])
            stats["questions"].append({
                "position": qnum,
                "title": title,
                "type": itype,
                "n_choices": len(choices),
            })
        elif itype == "ordering":
            choices = entry.get("interaction_data", {}).get("choices", {})
            n = len(choices) if isinstance(choices, dict) else 0
            stats["questions"].append({
                "position": qnum,
                "title": title,
                "type": itype,
                "n_items": n,
            })
        else:
            stats["questions"].append({
                "position": qnum,
                "title": title,
                "type": itype,
            })

    return errors, warnings, stats


def print_results(path, errors, warnings, stats):
    """Print validation results for one file."""
    fname = Path(path).name
    print(f"\n{'=' * 60}")
    print(f"  {fname}")
    if stats:
        print(f"  {stats.get('title', '')}")
    print(f"{'=' * 60}")

    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for err in errors:
            print(f"    [x] {err}")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for warn in warnings:
            print(f"    [!] {warn}")

    if not errors and not warnings:
        print("\n  All checks passed.")

    if stats and stats.get("questions"):
        print(f"\n  Questions ({stats['n_questions']}):")
        for q in stats["questions"]:
            if q["type"] == "multi-answer":
                print(f"    Q{q['position']}: {q['title']}"
                      f" -- {q['n_correct']}/{q['n_choices']}"
                      f" = {q['ratio']:.0f}% true"
                      f" -- {q['type']}")
            elif q["type"] == "matching":
                dist = (f" + {q['n_distractors']} distractors"
                        if q.get('n_distractors') else "")
                print(f"    Q{q['position']}: {q['title']}"
                      f" -- {q['n_pairs']} pairs{dist}"
                      f" -- {q['type']}")
            elif q["type"] == "choice":
                print(f"    Q{q['position']}: {q['title']}"
                      f" -- {q['n_choices']} choices"
                      f" -- {q['type']}")
            elif q["type"] == "ordering":
                print(f"    Q{q['position']}: {q['title']}"
                      f" -- {q['n_items']} items"
                      f" -- {q['type']}")
            else:
                print(f"    Q{q['position']}: {q['title']}"
                      f" -- {q['type']}")

    status = "FAIL" if errors else ("WARN" if warnings else "OK")
    print(f"\n  Result: {status}")
    return len(errors) == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_quiz.py <file.json> [<file2.json> ...]")
        print("\nValidates Canvas LMS quiz JSON files.")
        print("Checks structure, scoring references, and true/false ratios.")
        sys.exit(1)

    all_ok = True
    for path in sys.argv[1:]:
        errors, warnings, stats = validate_quiz(path)
        ok = print_results(path, errors, warnings, stats)
        if not ok:
            all_ok = False

    print()
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
