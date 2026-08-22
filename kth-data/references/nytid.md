# nytid as a data source: schedule, course register, TA roster, Zulip

`nytid` (`~/.local/bin/nytid`, source `~/devel/edu/nytid`) is the user's
teaching-admin tool. Besides `nytid todo` (see the `nytid-todo` skill) it
holds the facts below. Every subcommand has `--help`; consult it for exact
flags — this file records what the flags mean and the gotchas.

## Registers: where courses live

A *register* is a named directory of course configs (like git remotes):

```bash
nytid courses registry ls
#   tcs   /afs/kth.se/misc/projects/eecs/tcs/nytid/courses   # the TCS group's shared register
#   mine  ~/afs/.nytid/mine                                  # symlinks into tcs for the user's own courses
nytid courses ls -r tcs | grep datintro26          # list course rounds / subcourses
nytid courses config datintro26-cdate --register tcs              # whole config (JSON)
nytid courses config datintro26-cdate num_students --register tcs # one key
```

Raw files: `/afs/kth.se/misc/projects/eecs/tcs/nytid/courses/<course>/config.json`
(AFS must be mounted/authenticated; if `ls /afs/kth.se/...` fails, say so
rather than guessing numbers).

Conventions seen in the register:

- A course with several programmes has one *merged* course (`datintro26`,
  register `mine`, aggregate `num_students`, the sign-up sheet and Zulip
  invite) plus one subcourse per programme in `tcs`
  (`datintro26-cdate`, `-cinek`, `-ctfys`, `-cfate`, `-ctmat`), each with its
  own TimeEdit `ics` URL, `num_students` and `num_groups`.
- `num_students` is the *planning* number (set from admissions before the
  round starts); Canvas enrolment lags behind it for weeks. Use the register
  for room planning, Canvas for who is actually there.
- The numbers are set once a year by `~/devel/edu/introtools/adm/nytid.nw`
  (tangled to `adm/nytid.sh`); if the `.nw` and the live config disagree,
  the live config wins (the `.nw` may be out of sync).

## Schedule

```bash
nytid schedule show --help
nytid schedule show                       # the user's events, today .. +7 days
nytid schedule show datintro26 --start 2026-08-22 --end 2026-09-01 --no-todo --week
nytid schedule show datintro26 --start 2026-08-24 --end 2026-08-26 --no-todo --register '.*' -f csv
```

Output columns (table): `[Week N Weekday] DD/MM HH:MM  <event title>  <rooms, comma-separated>  Needed TAs: n; Booked TAs: <usernames in booking order>`.

Gotchas:

- Times are the TimeEdit booking (e.g. `10:00`); KTH teaching starts at the
  academic quarter (`10:15`).
- `--register '.*'` shows the raw TimeEdit view of every subcourse (one line
  per subcourse, with the TimeEdit description: lecturer, "Helklass",
  programme codes) and warns about subcourses without a sign-up sheet —
  harmless.
- `--user '.*'` returns nothing (the user filter is not a regex). Keep the
  default user and read the `Booked TAs:` field instead.
- The `Booked TAs` order is the sign-up-sheet order: leftmost first in the
  queue, the last ones beyond `Needed TAs` are reserves.
- TimeEdit does **not** say which programme sits in which room when one
  event books many rooms; that mapping is the course's own (Canvas page /
  Zulip), see the workflow in SKILL.md.
- The live bookings are the Google sign-up sheet (`signupsheet.url` in the
  merged course config); the CSV snapshot under the course's `data/` dir
  can be stale.
- `nytid schedule ics` exports; `nytid schedule external` shows other
  courses' events.

## TA roster

```bash
nytid hr users datintro26          # every username booked on at least one session
canvaslms users -c datintro26 -a   # TAs enrolled in Canvas (names + emails)
```

`~/afs/.nytid/reported_TAs/<course>.txt` lists who has been reported to HR
(with personnummer — do not copy into messages or files). Amanuensis
paperwork per TA is under `~/devel/edu/intropy/adm/assistants/`.

## Zulip (course chat)

Each course config can carry `zuliprc.user` / `zuliprc.bot` next to it;
`nytid zulip` uses them, so there is no need to know the realm or keys:

```bash
nytid zulip datintro26 streams                      # list streams (channels)
nytid zulip datintro26 topics <stream>
nytid zulip datintro26 read -s general -t "<topic>" # read before posting
nytid zulip datintro26 send -s <stream> -t "<topic>" "<message>"   # or "-" to read stdin
nytid zulip datintro26 users list
```

- `send` prefers `zuliprc.user`, i.e. **posts in the user's own name** —
  confirm wording and target with the user before sending; it is
  outward-facing.
- The datintro26/prgi26 realm is `prgi26.zulipchat.com`; the `~/.zuliprc`
  default points at a different realm, so never use bare `zulip-send`
  without `--config-file`.
- `zulipcli --zuliprc <path> …` is the same tool without the course lookup.

## Also in nytid

`nytid utils rooms booked|unbooked` tracks free rooms from a TimeEdit ICS
(configured rooms in `~/.config/nytid/config.json` → `utils.rooms`);
`nytid signupsheets` manages the sign-up sheets; `nytid hr` the HR reports.
