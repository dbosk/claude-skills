# Email-to-Todo Conversion Rules

Detailed rules and rationale for turning flagged emails into `nytid todo`
items. SKILL.md summarizes these; this file holds the full reasoning and
worked examples. Read this when actually performing the conversion.

## Rule 1 — Never assign to dan-claude

Email-derived todos are for the user (`daniel@bosk.se`) themselves. Omit
`--who dan-claude` from suggested commands. The default worker (current
user) is correct.

**Why:** The user personally handles correspondence — replies to
colleagues, students, and administration are inherently human work.
dan-claude is a delegated worker for code/tooling tasks, not a stand-in
for the user in human communication. Assigning email replies to dan-claude
would be meaningless and would pollute its queue with items it cannot
act on.

**Contrast with normal nytid-todo usage:** The `nytid-todo` skill defaults
to `--who dan-claude` for code-related autonomous work. This skill's
rule is the explicit opposite for email items.

## Rule 2 — Group by theme, never per-email

Cluster flagged emails before suggesting todos. Never emit one
`nytid todo add` per message. Group by:

- **Category** (missing grades, urgent, timesheets, sick leave)
- **Course code** (DD2520, DA231X, etc.)
- **Sender cluster** (a specific student going back and forth, or a
  thread with administration)
- **Subject keyword** (a single project name appearing across senders)

Aim for ≤ 7 groups total — beyond that, triage becomes noise.

**Worked example.** 14 flagged emails, distributed:

- 5 about Ladok / missing grades → 1 todo "Resolve missing grades"
- 3 from Yara Faris on a single thread → 1 todo with Yara's name
- 2 timesheet reminders → 1 todo "Submit timesheets"
- 2 about DD2520 lab make-ups → 1 todo "DD2520 restlabb"
- 2 reviewer invitations → 1 todo "Decide on review invitations"

Result: 5 todos instead of 14. Each todo carries the count in its
description so the user knows the volume.

## Rule 3 — Missing grades is a first-class category

When flagged emails reference grade reporting (Ladok, betyg, tillgodoräk,
or English "grade/missing"), surface them as their own group separate
from other course traffic — even when only 1–2 messages match.

**Why:** Missing grade reports have real downstream impact for students
(blocks their degree progression, CSN payments, course registration).
They recur often enough to deserve standing recognition. Mixing them
with general course-ops emails dilutes urgency.

## Rule 4 — Embed a neomutt review command

Every suggested todo must carry a one-liner shell command in its
description so the user can re-open exactly the relevant messages with
one paste.

### Form A — mutt limit (DEFAULT, state changes persist)

```
neomutt -f /home/dbosk/mail/kth/INBOX \
  -e 'push "<limit>~F ~s \"<regex>\"<enter>"'
```

Use whenever the user will act on the emails: mark read, reply, unflag.
Mutt pattern reference: `~F` flagged, `~s "regex"` subject, `~b "regex"`
body, `~f "regex"` from, space for AND, `|` for OR within a regex.

**Worked example (missing grades):**
```
neomutt -f /home/dbosk/mail/kth/INBOX \
  -e 'push "<limit>~F ~s \"betyg\\|ladok\\|grade\"<enter>"'
```

### Form B — mu virtual maildir (READ-ONLY browsing only)

```
mu find '<mu query>' --format links \
  --linksdir ~/.cache/mu-results/<slug> --clearlinks \
  && neomutt -f ~/.cache/mu-results/<slug>
```

Use only when the query needs mu's richer syntax (cross-folder,
date math, body+subject combined queries that mutt can't express
cleanly).

**Critical caveat:** Form B uses symlinks. Marking a message as read,
unflagging, or deleting in the linksdir renames/removes the *symlink*,
not the underlying file — the change does **not** reach the real inbox.
For any review where the user will mutate state, choose Form A.

The `<slug>` should be a short kebab-case category name
(`missing-grades`, `course-dd2520`, `yara-thread`) so concurrent uses
of Form B don't collide.

## Rule 5 — Don't trust subjects alone

Students frequently write vague subjects: "Hi", "Hej", "Question",
"Help", "Course", a bare first name, or just a course code. When
subject regex doesn't classify a flagged email clearly:

1. **Body query first** (still cheap):
   `mu find 'flag:flagged AND body:/ladok|betyg/' --fields 'd f s'`
2. **Full message inspection** only for genuine borderline cases:
   `mu view <path>` (get path via `--fields l`).
3. **Residual bucket:** if still unclassified, place in
   "uncategorized flagged" rather than forcing a wrong group.

Read Step 4 of SKILL.md for the integrated workflow.

## Suggested todo command template

```
nytid todo add MAIL <optional-course-label> \
  -t "<verb> <object> — <count> emails" \
  --description "<count> flagged emails about <theme>. Review in neomutt: <Form A or B command>"
```

Use Step-2-of-SKILL.md categories for the title's `<verb> <object>`.
Examples:
- "Resolve missing grades — 5 emails"
- "Reply to Yara on master thesis — 3 emails"
- "Submit pending timesheets — 2 emails"
