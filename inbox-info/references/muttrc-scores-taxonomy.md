# Email Taxonomy from `~/.muttrc.scores`

The authoritative source for "what's important in this inbox" lives in
`/home/dbosk/.muttrc.scores`. SKILL.md embeds a condensed view. This
file extracts the full taxonomy so triage decisions have the complete
picture without re-reading the raw scoring config every time.

If the user updates `~/.muttrc.scores`, refresh this file.

## Score-encoded priority signals

The scoring config encodes the user's importance model. Key invariants:

- **Flagged messages stay important indefinitely.** `score ~F +150` plus
  positive overrides for old-but-flagged (`~d >30d ~F +20`,
  `~d >90d ~F +20`, `~d >6m ~F +80`). Unflagged messages decay after
  30/60/90 days.
- **Personal mail to dbosk@kth.se** gets `+15`.
- **Mail addressed personally to me** (`~p`) gets `+10`; unaddressed
  (`~u`) gets `-10`.

## Category regex (subject patterns)

| Category | Regex | Score | Notes |
|----------|-------|-------|-------|
| Forwarded | `(Fwd\|FWD\|FW\|Fw\|Forward\|VB):?` | +30 | |
| ID:KTH-INC | `"ID:KTH-INC"` | +100 | Incident IDs |
| Important | `(viktig\|important\|brådska\|urgent)` | +50 | |
| Urgent | `(bråttom\|brådskande\|urgent)` | +100 | |
| Timesheets | `(ti[dm]s?(rapport\|ersättning)\|time ?sheet\|lön\|timmar\|arvode\|jobbade timmar)` | +75 | |
| TA management | `(assning\|asse\|assistent\|TA)` | +50 | |
| Missing grades | `(ladok\|betyg)` | +50 | **First-class category** |
| Credit transfer | `tillgodoräk` | +50 | |
| CSN | `CSN` | +50 | Student loan agency |
| Sick leave | `(sjuk\|sick\|[^a-zA-Z]ill)` | +50 | |
| Lab make-ups | `rest(er\|labb\|uppgift\|inlämn)` | +50 | |
| Course analysis / PM | `(kurs)?.?(analys\|PM\|pm\|(ut)?värdering)` | +50 | |
| Programme tags | `(CINEK\|CMAST\|CITEH\|CDATE\|CFATE\|CTMAT\|CTFYS\|CLGYM)` | +50 | KTH programme codes |
| Make-up exam | `kompletter(a\|ing)` | +15 | |
| Examination | `examin(era\|ation)` | +15 | |
| Grading work | `rätt(ad?\|ning)` | +15 | |
| Presentations | `redovis(a\|ning)` | +15 | |
| Labs | `lab(b\|oration)` | +15 | |
| Reports | `r(ap\|e)port` | +15 | |
| Questions | `fråga` | +15 | |
| Reviewing | `(reviewer.*invitation\|invitation.*reviewer)` | +30 | |
| KTH Survey | (from "KTH Survey") | +50 | |
| Cron from rpi | `Cron.*dbosk@rpi` | +200 | High urgency |
| Aktuell pedagogik | `"Aktuell högskolepedagogisk forskning"` | +60 | |
| Stress program | `stresshanteringsprogram` | +50 | |
| Storträffen | `(bordsledare\|Storträffen)` | +20 | Meetings |
| TEL meetings | `(TEL.(meeting\|möte))` | +20 | |
| Cerise | `[Cc]erise` | +20 | Project name |

## Course-code regex

| Course / nickname | Subject regex |
|-------------------|---------------|
| DD1301 datorintro | `(DD1301\|dat(a\|or)?intro(duktion)?)` |
| DD131[057] programmering | `(DD131[057]\|programmering(steknik)?\|prg.)` |
| DD1320 tilda | `(DD1320\|tilda[vh]?)` |
| DD1337 inda | `(DD1337\|inda)` |
| DD2520 tilkry (applied crypto) | `(DD2520\|till?kry)` |
| DA2215 / DD2302 science of cyber security | `(DA2215\|DD2302\|vetcyb\|science.*security)` |
| DA150X bachelor thesis | `(DA150[Xx]\|dkex\|dkand\|kex-?jobb\|kandidat\|kex\|bachelor.*thesis)` |
| DA231X master thesis | `(DA231[Xx]\|exjobb\|master.*thesis)` |
| Thesis (generic) | `thesis` |
| Course labs | `(LAB[123]\|KAL1\|MAT1)` |
| Datorprov | `[Dd]atorprov` |
| INL1 written/oral/quiz | `(INL1([Ww]ritten\|[Oo]ral\|[Qq]uiz)?)` |
| LH219V pedagogy | `LH219V` |
| ProSam | `(DD139[01]\|[Pp]rosam)` |
| Indek perspective | `(([Kk]ompletterande\\ \|I-)[Pp]erspektiv\|indek\|I-student)` |

## High-signal senders

### Special-attention people (+150)
- Celina Soori
- Yara Faris

### Very high (+100)
- Yasmina Altayy
- Senders matching `@timeedit.com`

### High (+80)
- Liisa Wettemark
- Edita Korlat
- Francisco Gomes
- Bedour Alshaigy
- Laurie Gale
- Lennart Franked
- Jan-Erik Jonsson
- `maffei@kth.se`

### Notable (+30 to +50)
- "Anna Olanås Jansson" (+50)
- "Hanna Holmqvist" (+50)
- `pa-.*@.*\.kth\.se` (+50)
- Generic `@(.*\.)?(kth|kau|uu|chalmers|lu|miun|ltu|lnu|oru).se` (+50) — Swedish universities
- Generic `@(.*\.)+(edu|ac\.[a-z]{2,3})` (+30) — academic addresses
- `viggo@`, `karlm@`, `akhog@`, `buc@`, `glassey@/rjglasse@gmail.com`,
  `maguire@`, `lk@/Linda Kann`, `riese@/Emma Riese`,
  `(Mathieu Gestin|Davide Frey|Guillaume Piolle)` — all +30 to +50
- "Mats Näslund", "Ol(le|of) B[äa]lter", "Johan Snider",
  "Alexander Baltazis", "Monperrus", "Olga Viberg",
  "Leif Kari", "Camilla Björn" — +20 to +30
- `Calendly ~s "New Event"` (+150) — calendar invites
- `Niccolas Albiz`, `Annie Holgersson` (+20) — ProSam
- `simone.fischer-huebner@kau.se` (+50) — SWITS
- `feedbackfruits` (+30)
- `noreply@urkund.se` (=0, neutralized)

### Institutional senders (+15 to +30)
- `schema@admin.kth.se` (scheduling)
- `service@eecs.kth.se`
- `education-support@eecs.kth.se`
- `student-support@eecs.kth.se`
- `hr-support@eecs.kth.se`
- `it-support@kth.se`
- `e-learning@kth.se` (+15)
- `@indek.kth.se`
- `~t teachers@(.*\.)?kth.se` (+15) — teachers list
- `~c dbosk@kth.se` (+15) — cc'd to me
- `Canvas ~s dis[ck]ussion` (+50)
- `Canvas ~s (message|meddelande)` (+10)
- `GitHub`, `notifications@github.com` (+50)
- `Zulip` (+50)
- `notifications@instructure.com` (+20)
- SWITS list (+50)

## Known noise — exclude from triage

These senders/subjects are explicitly scored negative. Even if one slips
through with a flag, **don't surface in triage suggestions** — the user
already decided they're not worth attention:

- `Google Scholar` (-100)
- `The Download` (-80)
- `Nature Briefing` (-80)
- `News from Science` (-80)
- `Times Higher Education` (-60)
- `Springer Alert` (-60)
- `ScienceDirect Message Center` (-60)
- `KTH Magazine` (-40)
- `KTH Opportunities Fund` (-40)
- `KTH Alumni` (-60)
- `SIAM` (-200)
- `SANS` (-90)
- `EIT Digital` (-100)
- `IEEE` (-50)
- `ACM` (-50)

Two ACM-adjacent senders are *positive* exceptions: `ACM Digital Library`
(+10) and `Xplore` (+10) — these are useful for paper access.

## How to use this taxonomy

1. When triaging flagged emails, walk this file's categories top-to-bottom
   by priority (urgent > grades > timesheets > course work > general).
2. For each flagged email, find its best-matching category (subject first,
   body second — see Rule 5 in `todo-conversion-rules.md`).
3. Group multiple emails in the same category into one todo (Rule 2).
4. Use the regex from this file as the subject pattern in the Form A
   neomutt review command.

If a flagged email matches a "known noise" sender, flag it as a likely
mis-flag rather than a triage candidate — ask the user before creating
a todo for it.
