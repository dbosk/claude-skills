# Verification checklist

Use this before recording any reference. The question is never "is this paper
about the topic?" but **"does this specific passage entail this specific claim,
at its scope and strength?"** If you cannot answer yes with a verbatim quote,
the reference does not back the claim — find a better one.

## Table of contents

- [The applicability tests](#the-applicability-tests)
- [Strength words that must match](#strength-words-that-must-match)
- [Source-quality red flags](#source-quality-red-flags)
- [What "verified" requires](#what-verified-requires)

## The applicability tests

Run each test against the candidate source and its supporting quote:

1. **Scope match.** Does the source's population/domain/setting cover the claim?
   A result about *expert* programmers does not back a claim about *novices*; a
   lab study does not automatically back a field claim. Narrow the claim or find
   a source whose scope contains it.

2. **Strength match.** Does the evidence support the verb? *Correlated* is not
   *causes*; *can improve* is not *improves*; *in one trial* is not *robustly*.
   See the strength table below.

3. **Primary vs secondary.** Is this the source that actually established the
   finding, or is it citing someone else for it? Citing a survey or a textbook
   for a specific empirical result is a "citation of a citation" — chase it to
   the primary source and cite that, keeping the survey only for consensus
   claims.

4. **Direction and sign.** Confirm the quote supports the claim, not its
   opposite or a qualified version ("X helped, *but only when* Y"). Read enough
   surrounding text to catch a reversing clause.

5. **Currency.** Has the finding been superseded, replicated, or contested?
   Prefer the most recent authoritative statement; if the claim is contested,
   say so in the prose and cite both sides, or escalate to `deep-research`.

6. **Retraction / correction.** Check the source is not retracted or corrected
   in a way that affects the claim (publisher page, Retraction Watch, Crossref
   `update-to` metadata). For a whole session, `scholar verify "<session>"`
   runs tests 5–6 via Crossref and flags retracted/corrected/superseded papers.

7. **Venue credibility.** Is it a peer-reviewed venue or a reputable preprint
   with corroboration? Be wary of predatory journals and of preprints whose
   only support is themselves. A single un-replicated preprint backs "it has
   been proposed that…", not "it is established that…".

8. **Quote entailment.** Read the quote in isolation: does it, by itself, make
   the claim true? If it needs you to fill gaps, it is too weak — quote more, or
   pick a source that states the claim directly.

## Strength words that must match

| Claim says | Evidence must show | Not enough |
|------------|--------------------|------------|
| causes / improves | controlled/experimental effect, stated direction | correlation, association |
| always / in general | result across the claimed range or a general proof | one study, one dataset |
| is established / well known | survey, meta-analysis, or replicated consensus | a single primary paper |
| can / is possible | one credible demonstration | (this is the easy case) |
| reduces / increases by N | a measured effect size at that magnitude | qualitative "helps" |

When the evidence is weaker than the claim, **soften the prose** rather than
overstate the source.

## Source-quality red flags

- Venue you cannot identify, or one on known predatory lists.
- Citation count and venue wildly inconsistent with the claim's importance.
- The "finding" appears only in the abstract/intro, not the results.
- The paper attributes the claim to a reference (follow it).
- Numbers in the quote differ from the numbers in your claim.

## What "verified" requires

- **Minimum:** the abstract or the specific passage was actually read (via
  `scholar enrich`, `scholar pdf open`, or WebFetch of the source page).
  `scholar pdf quote "<url>" --claim "<claim>"` proposes candidate passages to
  read — it does not verify; you still read and confirm entailment.
- **For a precise quantitative or causal claim:** the relevant results section
  was read in full text, not just the abstract.
- **Never acceptable:** title-only, snippet-only, or "the model recalls this
  paper says…". Record in `VERIFIED` exactly what you read (`abstract` vs
  `full-text`) so the record is honest.
