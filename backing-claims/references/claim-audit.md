# Claim audit: finding the claims that carry no citation

The find → verify → record protocol starts from a claim. The failure this
file guards against is the claim nobody recognised as one, so the protocol
never ran. It happened in the intropy course notes (2026-09): a deck told
students to follow PEP 8 "because code should be readable to someone other
than its author", verified PEP 8 against its primary source, wrote in its
appendix that "the module makes no claims that needed a literature search",
and every reviewer accepted that sentence. The author's question — "is
adhering to PEP 8 really beneficial, or can we skip it without any negative
effect?" — turned into an 18-source two-sided search whose answer was
"partly, and weaker than assumed": names, indentation and short lines have
experimental support; PEP 8's specific numbers do not, and one tested rule
was better violated.

## Where claims hide

| Sentence form | The hidden claim | What "verified" must mean |
|---|---|---|
| Advice: "follow X", "use Y", "always/never Z" | Doing X produces a benefit | Two-sided review of the benefit, not a check that X exists |
| The "because" of advice: "so that others can read it" | The mechanism/benefit is real and applies to this population | Same: scope (novices? professionals?) and strength |
| "X is standard / established / best practice" | Adopted and validated, not merely proposed | Evidence of adoption AND a counter-search for criticism |
| Convention checked against its source ("PEP 8 says four spaces") | Only the attribution is backed | Say so; the benefit is a second claim |
| "This text makes no claims needing a search" | A claim about the text | List the text's imperatives and "because" clauses; test each |
| Common sense ("it obviously helps to …") | The common sense is a claim | Search it; obvious claims fail often (four-space indentation) |
| Numbers in advice ("79 characters", "four spaces", "one blank line") | The specific number, not the principle, is what is prescribed | Back the number or state that only the principle is backed |

## The audit, in five questions

Run it over the finished text (prose, slides, learning objectives,
summaries), not only over the sentences you planned to cite:

1. Grep for imperatives and modals — Swedish *ska, bör, måste, följ, använd,
   undvik, alltid, aldrig*; English *should, must, always, never, use,
   avoid, follow* — and for *because / eftersom / därför att / så att*.
2. For each hit, write the benefit it asserts as one sentence with scope and
   strength ("consistent style makes code measurably easier for a novice
   reader to understand").
3. Decide what is actually backed today: the attribution (the convention
   exists and says this), the principle (readability helps), or the specific
   rule (four spaces). Most advice is backed only at the first level.
4. Run the protocol on the benefit: support-search, counter-search, screen,
   verify in full text, record provenance, one appendix chapter per claim.
5. Rewrite the advice to the strength the evidence carries: keep the rule as
   a convention if that is all it is ("we do this because the community
   does"), cite the principle where it is backed, and say plainly which
   numbers are unbacked. Never let "verified against the primary source"
   stand in for "the benefit is backed".

## Signs the audit was skipped

- An appendix or evidence log that says the document makes no claims.
- Advice cited only to the style guide, standard, or textbook that issues
  it.
- "Because it improves readability/maintainability/quality" with no
  reference, or with a reference to the guide itself.
- A learning objective that tells students to follow a convention while the
  notes never say what following it is known to buy.
