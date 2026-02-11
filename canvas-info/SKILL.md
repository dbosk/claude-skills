---
name: canvas-info
description: |
  Research and answer questions about Canvas LMS courses using the canvaslms
  CLI. Use proactively when: (1) user asks about course content, assignments,
  pages, grades, deadlines, or announcements, (2) user mentions a Canvas
  course name or course code, (3) user asks "what assignments/pages/modules
  are in [course]?", (4) user wants to find specific course materials or
  check deadlines. This skill is read-only; to create quiz content, use the
  canvas-quiz skill instead.
---

# Canvas Course Information Research

## Overview

The `canvaslms` CLI provides read-only access to Canvas LMS course data:
assignments, pages, modules, discussions, announcements, grades, quizzes, and
calendar events. This skill teaches a research workflow for answering user
questions about their courses.

For detailed options on any subcommand, run `canvaslms <subcommand> -h`.

## Research Workflow

Follow these steps when answering a Canvas-related question:

### Step 1: Identify the Course

```bash
canvaslms courses              # List all courses
canvaslms courses "regex"      # Filter by name/code (case-insensitive regex)
```

Note the course ID from the output. Use it with `-c <id>` in subsequent
commands.

### Step 2: Explore Course Structure

Choose the right entry point based on the question:

| Question type | Start with |
|---------------|------------|
| "What's in this course?" | `canvaslms modules list -c <id>` |
| "What assignments exist?" | `canvaslms assignments list -c <id>` |
| "Any announcements?" | `canvaslms discussions list -c <id> -t announcement` |
| "What pages are available?" | `canvaslms pages list -c <id>` |
| "What are the deadlines?" | `canvaslms calendar -c <id>` |
| "How did students do?" | `canvaslms results -c <id>` |

### Step 3: Drill into Content

Use `view` subcommands to read specific items:

```bash
canvaslms modules view -c <id> -m "module regex"
canvaslms pages view -c <id> -p "page regex"
canvaslms assignments view -c <id> -a "assignment regex"
canvaslms discussions view -c <id> -d "discussion regex"
```

The `view` commands output full content (markdown for pages, HTML for
assignments). The `list` commands output tab-delimited CSV summaries.

### Step 4: Refine with Filters

Most commands accept regex filters and additional flags. Run
`canvaslms <subcommand> -h` to discover available filters for each command.

Common refinement patterns:
- Combine course + item filters: `-c "DD2520" -a "lab"`
- Filter by module: `-c <id> -m "week 3"`
- Filter submissions by user: `canvaslms submissions -c <id> -u "username"`

### Step 5: Synthesize and Answer

After gathering data:
- Quote relevant content directly when answering
- Summarize lists into readable format (tables, bullets)
- If data seems stale, suggest re-running with `--no-cache`
- Provide the course/assignment/page names so the user can navigate in Canvas

## Quick Reference

| To find... | Command | Key flags |
|------------|---------|-----------|
| All courses | `canvaslms courses` | regex filter, `-i` for ID only |
| Course modules | `canvaslms modules list` | `-c`, `-m` |
| Module contents | `canvaslms modules view` | `-c`, `-m` |
| Assignments | `canvaslms assignments list` | `-c`, `-a`, `-m` |
| Assignment details | `canvaslms assignments view` | `-c`, `-a` |
| Wiki pages | `canvaslms pages list` | `-c`, `-p`, `-m` |
| Page content | `canvaslms pages view` | `-c`, `-p` |
| Announcements | `canvaslms discussions list` | `-c`, `-t announcement` |
| Discussions | `canvaslms discussions list` | `-c`, `-t discussion` |
| Discussion content | `canvaslms discussions view` | `-c`, `-d` |
| Quizzes | `canvaslms quizzes list` | `-c`, `-q` |
| Submissions | `canvaslms submissions` | `-c`, `-a`, `-u` |
| Grades/results | `canvaslms results` | `-c`, `-a` |
| Calendar/deadlines | `canvaslms calendar` | `-c`, date range flags |
| Users/enrollment | `canvaslms users` | `-c`, role filters |
| Groups | `canvaslms groups` | `-c` |

## Regex Filtering Patterns

- Course matching is case-insensitive: `"dd2520"` matches "DD2520"
- Use anchors for precision: `"^DD2520$"` for exact match
- Partial match works: `"crypt"` matches "Applied Cryptography"
- Combine flags for specificity: `-c "DD2520" -m "week 3" -a "lab"`

## Output and Caching

- `list` commands produce **tab-delimited CSV** (pipe through `column -t -s$'\t'` for readability)
- `view` commands produce **full content** (markdown, HTML, or YAML frontmatter + content)
- Results are cached; use `--no-cache` to force a fresh fetch
- Pages `view` output includes YAML frontmatter with metadata

## Common Pitfalls

**Always identify the course first:**
```
BAD:  canvaslms assignments list -a "lab 1"     # No course specified
GOOD: canvaslms assignments list -c 12345 -a "lab 1"
```

**Use `list` before `view` to discover item names:**
```
BAD:  canvaslms pages view -c 12345 -p "syllabus"   # Guessing the page name
GOOD: canvaslms pages list -c 12345                   # Discover available pages
      canvaslms pages view -c 12345 -p "Course Syllabus"  # Use actual name
```

**Use the right content type flag for discussions:**
```
BAD:  canvaslms discussions list -c 12345              # Missing type
GOOD: canvaslms discussions list -c 12345 -t announcement
GOOD: canvaslms discussions list -c 12345 -t discussion
```

## Scope

This skill is **read-only** — it retrieves and presents course information.
It does not create, modify, or delete any Canvas content. To create quiz
content, use the `canvas-quiz` skill instead.
