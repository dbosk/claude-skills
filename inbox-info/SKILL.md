---
name: inbox-info
description: |
  Research and answer questions about email in the user's Maildir via mu
  (maildir-utils). Use proactively when: (1) user asks about emails, inbox,
  flagged messages, senders, subjects, or specific correspondence,
  (2) user asks "what do I need to handle / respond to?" — flagged emails
  are the user's marker for actionable items, (3) user mentions mu, mutt,
  neomutt, or Maildir, (4) user wants to convert email-derived work into
  nytid todos. Strictly read-only; never modifies mail state.
---

# Inbox Information Research

## Overview

The user reads email with NeoMutt against a Maildir indexed by `mu`
(maildir-utils). This skill wraps `mu find` / `mu view` to answer questions
about the inbox without scanning Maildir files directly. It also helps
convert flagged emails into themed `nytid todo` items.

**Canonical "needs handling" signal:** the user **flags** every email they
need to act on (the `\Flagged` / "starred" IMAP flag). Default to
`flag:flagged` for triage queries — not `flag:unread`.

This skill is **strictly read-only**: query `mu`, suggest `nytid todo`
commands, and let NeoMutt own flag/state changes.

## Known Setup

Embedded so the skill activates with zero tool calls. Re-verify with
`mu info` only if a query misbehaves.

- **Maildir+ account root** (use with `mu` — it indexes the whole tree):
  `/home/dbosk/mail/kth`
- **INBOX leaf mailbox** (use with `neomutt -f` — it opens a single folder):
  `/home/dbosk/mail/kth/INBOX`
- **Xapian DB**: `/home/dbosk/.cache/mu/xapian`
- **Verified**: 2026-05-27

The account root contains subfolders (`INBOX/`, `Sent/`, `Archive/`, etc.)
but no `cur/new/tmp` of its own. Pointing `neomutt -f` at the root opens
the folder browser, not messages — `~F ~s "..."` limits then filter an
empty set. Always target `INBOX` (or the specific subfolder) for mutt.

**Lazy fallback — call `mu info` only if:**
- a query returns unexpectedly zero results,
- the user reports the index seems stale,
- or `mu find` errors out.

## Research Workflow

### Step 1: Pick the right query

| Question | Query |
|----------|-------|
| "What needs handling?" | `mu find 'flag:flagged' --fields 'd f s' --sortfield date --reverse` |
| "What's been flagged forever?" | `mu find 'flag:flagged AND date:..1m' --fields 'd f s' --sortfield date` |
| "Recent from X?" | `mu find 'from:NAME date:1m..' --fields 'd f s' --maxnum 20` |
| "Anything on topic Y?" | `mu find 'subject:Y OR body:Y' --threads --fields 'd f s'` |
| "How many of Z?" | `mu find QUERY --fields i \| wc -l` |
| "Show me message N" | `mu view <path>` (path from `--fields l`) |

Bound output: always use `--maxnum N` and `--fields` to keep results compact.

### Step 2: Classify against the user's taxonomy

The authoritative classifier lives in `~/.muttrc.scores`. For the full
extracted taxonomy — every category regex, every high-signal sender,
every noise filter — see
`references/muttrc-scores-taxonomy.md`. Read it when classification is
non-trivial or when the user updates their scoring config.

The common categories (priority order) are:

| Category | Subject regex | Notes |
|----------|---------------|-------|
| **Missing grades / Ladok** | `ladok\|betyg\|tillgodoräk` | **First-class — always its own bucket** |
| Urgent | `brådska\|bråttom\|urgent\|viktig\|important` | |
| TA management | `assning\|asse\|assistent\|\bTA\b` | |
| Course operations | `kompletter\|examin\|rättning\|redovis\|labb?\|rapport\|rest(er\|labb\|uppgift\|inlämn)` | grading, make-ups, lab reports |
| Course analysis / PM | `(kurs)?.?(analys\|PM\|pm\|utvärdering)` | |
| Timesheets / pay | `tidrapport\|timersättning\|timesheet\|lön\|timmar\|arvode` | |
| Sick / personal | `sjuk\|sick\|\bill\b` | |
| Reviewing | `reviewer.*invitation\|invitation.*reviewer` | |
| Scheduling | from `schema@admin.kth.se` or `@timeedit.com` | |

**Course codes** to recognize:
- DD1301 (`datorintro`/`dataintro`)
- DD131[057] (`programmering`/`prg`)
- DD1320 (`tilda`)
- DD1337 (`inda`)
- DD2520 (`tilkry`/`tillkry`)
- DA2215, DD2302 (`vetcyb`, science/security)
- DA150X (`dkex`/`dkand`/`kex`, bachelor thesis)
- DA231X (`exjobb`, master thesis)
- LH219V (pedagogy)

**Programme tags** to recognize: `CINEK|CMAST|CITEH|CDATE|CFATE|CTMAT|CTFYS|CLGYM`.

**High-signal senders** (from `~/.muttrc.scores`): Celina Soori, Yara Faris,
Yasmina Altayy, Liisa Wettemark, Edita Korlat, Francisco Gomes, Bedour
Alshaigy, plus institutional addresses (`schema@admin.kth.se`,
`service@eecs.kth.se`, `education-support@eecs.kth.se`, etc.). When a
flagged email is from one of these, give it its own cluster.

**Known noise** (excluded from triage even if flagged): Google Scholar,
KTH Magazine, IEEE, ACM, SIAM, Nature Briefing, The Download, KTH Alumni,
etc. — see negative scores in `~/.muttrc.scores`.

### Step 3: Handle ambiguous subjects (students often write bad ones)

Many emails arrive with vague subjects: "Hi", "Hej", "Question", "Help",
"Course", a bare first name, or just a course code. Don't trust subject
regex alone. Two-tier approach:

1. **Subject regex first** (cheap) — sort flagged emails into the
   obvious buckets.
2. **Body query for ambiguous matches**:
   `mu find 'flag:flagged AND body:/ladok|betyg/' --fields 'd f s'`
   catches grade-adjacent emails whose subjects don't mention grades.
3. **Read the full message** with `mu view <path>` only for the
   borderline cases — never as a default step.
4. If still unclassified, put it in a residual **"uncategorized flagged"**
   group rather than forcing a wrong bucket.

### Step 4: Group flagged emails into themed todos

When the user asks for todos from flagged email, propose **themed batches**
— never one todo per message. Cluster by category, course code, sender, or
topic, then suggest one `nytid todo add` per group.

For the full rules with rationale and worked examples, see
`references/todo-conversion-rules.md`. Headlines:

- **NEVER use `--who dan-claude`.** Email-derived todos are for the user
  themselves. dan-claude doesn't answer the user's email. Omit `--who`
  entirely so the default (current user) applies.
- **Missing grades is always its own group**, separate from other course
  traffic, even when only 1–2 messages match.
- **Every todo description must embed a review command** so the user can
  re-open the relevant emails with one paste.

### Step 5: Choose the right review-command form

Two forms. Default to **Form A** unless you specifically need mu's richer
query language for read-only browsing.

**Form A — mutt `limit` on the real Maildir (DEFAULT).** State changes
(mark read, reply, unflag) persist to the real inbox:

```
neomutt -f /home/dbosk/mail/kth/INBOX \
  -e 'push "<limit>~F ~s \"betyg\\|ladok\\|grade\"<enter>"'
```

Note `INBOX`, not the account root — see "Known Setup" above.

Mutt patterns: `~F` flagged, `~s "regex"` subject, `~b "regex"` body,
`~f "regex"` from, `!~s "regex"` negation. Combine with space (AND) or `|` (OR
within a single regex). **Date filters**: `~d "<3m"` newer than 3 months ago
(within last 3 months), `~d ">3m"` older than 3 months ago. Offsets: `d` day,
`w` week, `m` month, `y` year. Absolute range: `~d "01/27/26-02/27/26"` (US
`MM/DD/YY`). When embedding in a shell string, escape inner double quotes:
`~d \"<3m\"`.

**Form B — mu virtual maildir, READ-ONLY browsing only.** Use when a
query can't be expressed as mutt patterns (cross-folder, mu's richer
operators):

```
mu find 'flag:flagged AND (subject:/grade|betyg|ladok/ OR body:/ladok|betyg/)' \
  --format links --linksdir ~/.cache/mu-results/missing-grades --clearlinks \
  && neomutt -f ~/.cache/mu-results/missing-grades
```

**Form B caveat — symlinks don't propagate state.** Marking a message
as read in the linksdir renames the *symlink*, not the underlying file.
State changes do NOT reach the real inbox. Pick Form A whenever the
user will mutate state.

Use a per-group slug under `~/.cache/mu-results/<slug>/` for Form B
so concurrent uses don't collide.

### Step 6: Suggest the todo (don't run it)

Print the command for the user to run. **Prefer `--command` (`-c`)** over
`--description` for the review command — that way `nytid todo start <id>`
runs it directly, no copy-paste. Put context/rationale in `--description`
for `view`, put the executable command in `-c`.

```
nytid todo add MAIL \
  -t "Resolve missing grades — 5 student emails" \
  --description "5 flagged emails about missing grades (Ladok/betyg)." \
  -c "neomutt -f /home/dbosk/mail/kth/INBOX -e 'push \"<limit>~F ~s \\\"betyg|ladok|grade\\\"<enter>\"'"
```

**Escape ladder** (bash → nytid storage → shell on `start` → mutt `-e`
parser → mutt push string). Inside a bash double-quoted argument, use
`\\\"` for every literal `"` that mutt's push-string parser must see — `\\`
becomes `\` and `\"` becomes `"`, yielding the stored `\"` that mutt
unescapes back to `"`. When you splice variables into the template, make
sure they're *bare* (no quotes baked in) and let the template add the
`\\\"` around them.

For adding email context to an existing todo, suggest:
`nytid todo note <ID> -m "Saw a follow-up email from <sender> on <date>"`.

See the `nytid-todo` skill for broader todo-workflow details, including
auto-parenting behavior (a new `nytid todo add` without `--top-level`
parents under the currently active todo — handy when the user has an
"Clear inbox" todo in-progress and wants each bucket as a child).

## Quick Reference

| Operator | Meaning |
|----------|---------|
| `from:NAME` | sender match |
| `to:NAME` | recipient match |
| `subject:TEXT` | subject contains |
| `body:TEXT` | body contains |
| `flag:flagged` | starred / actionable |
| `flag:unread` | unread |
| `date:1w..` | last week to now |
| `date:..1m` | older than 1 month |
| `date:20260101..20260131` | absolute range |
| `mime:TYPE` | attachment mime type |
| `AND` / `OR` / `NOT` | boolean combiners |

`--fields` letters: `d` date, `f` from, `t` to, `s` subject, `l` path,
`i` message-id, `g` flags.

## Output Handling

- Default fields: `d f s`. Add `l` only when feeding `mu view`.
- For large result sets, summarize aggregates ("12 flagged from this
  month, mostly course ops") instead of dumping the full list.
- Use `--threads` for topic/thread questions.
- Output is tab-delimited by default; pipe through
  `column -t -s$'\t'` for readability when showing to the user.

## Scope

**Strictly read-only.** Never run `mu index`, `mu remove`, `mu mkdir`, or
anything that writes to the Maildir or Xapian DB. Never compose, send, or
modify mail state — defer to NeoMutt. Never create `nytid todo` items
directly; only suggest commands. Don't print email bodies unless the
user asks.

## Common Pitfalls

**Stale index.** Results miss new mail until `mu index` runs. If the
user reports missing emails, run `mu info` to check the last index time
and suggest they reindex.

**Shell quoting.** Always single-quote `mu` queries: `'flag:flagged'`,
`'from:foo AND date:1w..'`.

**mu regex `/.../` is fragile.** Spaces and parentheses inside the slashes
silently match zero results — e.g. `subject:/applied crypto/` and
`subject:/(foo|bar)/` both return nothing instead of erroring. For
multi-word terms or grouped alternations, use boolean OR of word terms:
`(subject:applied OR subject:crypto)`, `(subject:foo OR subject:bar)`.
Single-word alternations like `subject:/foo|bar|baz/` do work. When a
count looks suspiciously low, sanity-check by running each clause
separately with `--fields i | wc -l`.

**Form B is read-only.** Symlink renames stay in the linksdir; the real
inbox is untouched. Use Form A whenever state must persist.

**Trusting subjects.** Student emails frequently have unhelpful subjects.
Use body queries or `mu view` for ambiguous cases.

**Wrong todo ownership.** Never assign email-derived todos to
`dan-claude`. They belong to the user.
