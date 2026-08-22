---
name: kth-data
description: |
  Where to find KTH facts Claude cannot know by itself: the user's Canvas
  sandbox course for write-testing canvaslms, KTH room facts (capacity,
  building, address) via kth.se/places, the academic-year period dates
  (läsårsindelning) which must be searched for because intranet URLs change,
  and the user's teaching schedule via `nytid schedule show`. Use proactively
  when: (1) a task needs a Canvas course to test canvaslms write commands
  against, (2) a task mentions KTH rooms, lecture halls, seats/capacity,
  room booking, or mapping students/TAs to rooms, (3) a task needs period,
  term, exam-period or läsår dates (P1–P4, HT/VT, tentaperiod), (4) a task
  needs the user's (or TAs') schedule, lecture times, or which room an event
  is in. Read-only sources; pair with canvas-info/canvaslms for Canvas edits
  and nytid-todo for work items.
---

# KTH data sources

Facts about KTH that recur across tasks, and the one place to look each up.
Everything here is a *lookup*; the editing itself happens with other tools
(`canvaslms`, `nytid`).

## 1. Canvas sandbox course: "Sandbox dbosk"

Use the Canvas course **"Sandbox dbosk"** (Canvas course id 24725) to test any
`canvaslms` command that writes (create/edit/delete pages, assignments,
module items, calendar events, quizzes, ...). It is the user's own sandbox;
nothing in it is load-bearing.

- Select it with an anchored regex — several other Sandbox courses exist:
  `canvaslms ... -c "^Sandbox dbosk$"`
- Prefer reusing existing items; name throwaway artifacts recognizably
  (e.g. a `canvaslms-test-DELETE-ME` prefix) and delete them afterwards.
- Verify writes with `--no-cache`: the CLI updates its local cache on write,
  so a cached read can mask a server-side no-op.
- Restore whatever you moved or changed when the test is done.
- Never write-test fan-out paths (e.g. create-in-all-courses) against the
  real server, not even from the sandbox.

Real courses (datintro26, tilkry, ...) are for read-only research
(`canvas-info` skill) unless the task explicitly is to change them.

## 2. Rooms: https://www.kth.se/places/

KTH's room directory. The page's search box is JavaScript-driven, but
**`https://www.kth.se/places/room/<ROOM NAME>` redirects to the room's
page** (`/places/room/id/<uuid>`), which lists, among other things:

| Label on page | Meaning |
|---|---|
| `Platser:` | seats (use this for lecture/seminar capacity) |
| `Examinationsplatser:` | seats when used for written exams (much lower) |
| type line (`Hörsal`, `Övningssal`, ...) | room type |
| `Byggnad:`, `Adress:`, `Vån:`, `Campus:` | where it is |
| `Utrustning` | projector, HDMI, whiteboards, ... |

Browsing by building: `https://www.kth.se/places/building`.

Use the bundled script instead of scraping by hand (TSV: name, seats, exam
seats, type, building, address, url; unknown rooms print `not found` and
give exit status 1):

```bash
~/.claude/skills/kth-data/scripts/kth_room.py V32 B1 "Ka-Sal C" | column -t -s$'\t'
```

Room names are the short KTH codes as they appear in schedules (`V32`,
`B1`, `E1`, `Ka-Sal C`, `D2`, `Q1`). Adjacent numbering usually means
adjacent rooms in the same building (V32/V33/V34/V35, B1/B2/B3) — useful
when a large group must be split across rooms. Seat counts are the
authoritative capacity; do not reuse numbers from last year's pages without
re-checking, rooms get rebuilt.

## 3. Period and term dates: läsårsindelning

KTH publishes the academic-year calendar (läsårsindelning: terms HT/VT,
study periods P1–P4, exam periods, re-exam periods) on the intranet, one page
per academic year, e.g.
`https://intra.kth.se/utbildning/schema-och-lokalbokning/lasarsindelning/lasaret-2026-2027-1.1380361`.

**Search for the page rather than trusting a remembered URL** — the numeric
suffix and path change between years and site reorganizations:

- `WebSearch` for `KTH läsårsindelning läsåret <YYYY>-<YYYY+1>` (or
  `site:intra.kth.se läsårsindelning <year>`); the overview index is
  `https://intra.kth.se/utbildning/schema-och-lokalbokning/lasarsindelning/perioder`.
- Then `WebFetch` the year page and read the dates as written (Swedish
  `YY-MM-DD`). Conventions: P1 starts the Monday of the week after
  "inledande veckor", P1/P2 = HT, P3/P4 = VT; each period ends with a
  "Tentaperiod"; "Omexaminationsperiod" = re-exams.
- The English version lives under `/en/utbildning/...` on the same site.

Quote the fetched dates with the source URL in anything you produce; a date
from memory is not acceptable for deadlines or schedules.

## 4. The user's schedule: `nytid schedule show`

The user's (dbosk's) teaching schedule, including rooms and the TAs booked
per event, is available locally:

```bash
nytid schedule show --help     # filters: course, date range, register
nytid schedule show            # the user's events, today .. +7 days
nytid schedule show datintro26 --start 2026-08-22 --end 2026-09-01 --no-todo --week
```

Use it to answer "when/where is X", to find which rooms are booked for an
event (e.g. twelve rooms streaming one lecture), and which TAs are booked
(`Booked TAs:` field, sign-up order; `--user '.*'` does *not* work). Pair
with §2 to get the capacity of every booked room. Details, output columns
and gotchas: `references/nytid.md`.

## 5. Course register, student numbers, TAs, Zulip (nytid)

Course rounds live in nytid's registers (`tcs` = the TCS group's shared
register on AFS, `mine` = the user's symlinks into it). A multi-programme
course has one merged config plus one subcourse per programme, each with the
planning number of students:

```bash
nytid courses ls -r tcs | grep datintro26
nytid courses config datintro26-cdate num_students --register tcs
nytid hr users datintro26                 # TA usernames booked on the course
nytid zulip datintro26 streams            # course chat; `send` posts as the user
```

Use the register's `num_students` — not Canvas enrolment — when planning
rooms before a round starts. How the register, TA roster and Zulip commands
work, and what can go wrong: `references/nytid.md`.

## Workflow example: allocate programmes to rooms for a lecture

1. `nytid schedule show` → find the event and the rooms booked for it.
2. `scripts/kth_room.py <rooms…>` → seats per room.
3. Course register → expected students per programme.
4. Fit programmes to rooms (keep a split programme in adjacent rooms or at
   least the same building; B-huset and Q-huset are ~200 m apart, V-huset
   floors share stairs), leave a margin, and list the mapping as
   `room: seats, PROGRAMME`. With little slack a perfect fit is often
   impossible — prefer a small deficit with "overflow to Zoom" over a
   programme spread across three floors or a room shared by many
   programmes. Honour lecturer constraints first (who sits with which
   programme, who is online).
5. Publish the student-facing mapping in Canvas (`canvaslms pages edit`; if
   the course keeps its pages as files in a repo, edit the file and push it
   from there so the file stays the source of truth). Keep staff-only
   details (which TA runs which room) out of Canvas: put them in the course
   Zulip — draft the message for the user to post unless told otherwise.
