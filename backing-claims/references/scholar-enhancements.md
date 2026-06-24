# `scholar` enhancement ideas (captured, not built)

These are ideas for extending `scholar` (`~/devel/scholar`, repo
`dbosk/scholar`) so it directly supports the find → verify → record provenance
workflow. **None are implemented by this skill.** When the user wants to pursue
one, offer to file it as a `gh issue` on `dbosk/scholar` (per the
`document-issues` convention) rather than building it ad hoc.

`scholar` uses noweb literate programming (`src/scholar/*.nw` are the source of
truth; activate the `literate-programming` skill before editing). Relevant files
from its `AGENTS.md`: `src/scholar/cli.nw` (commands), `src/scholar/scholar.py`
(the `Paper`/`SearchResult` models), `src/scholar/providers.nw` (providers).

## Ideas

1. **Provenance-stub export.** A flag like `scholar search ... -f bibtex+prov`
   (or a `scholar prov stub <key>` command) that emits each entry already
   wrapped in a `% === provenance: <key> ===` block with `FOUND-VIA`
   pre-filled from the actual query, leaving `CLAIM`/`PICKED`/`QUOTE`/`VERIFIED`
   as TODO placeholders. Removes the most error-prone manual step.

2. **`rq` query → `FOUND-VIA` export.** A non-interactive command to print the
   recorded provider-specific queries for a kept paper in a ready-to-paste
   `FOUND-VIA` form, so the reproducibility trail `rq` already stores lands in
   the `.bib` automatically.

3. **Quote-extraction helper.** Given a cached PDF (`scholar pdf`) and a claim,
   a command that surfaces candidate supporting passages (and their page/section)
   to become the `QUOTE` — verification stays human, but the search is assisted.

4. **Retraction / currency check.** `scholar enrich` (or a new `scholar verify`)
   could flag retractions/corrections via Crossref `update-to` metadata, feeding
   the verification checklist's currency and retraction tests.

5. **Provenance round-trip with `scholar notes`.** Import/export the `.bib`
   provenance block to and from `scholar notes` so the two stores stay in sync.

## Filing

```bash
# from ~/devel/scholar, once the user agrees:
gh issue create --repo dbosk/scholar \
  --title "<short title>" --body "<motivation + sketch>"
```
