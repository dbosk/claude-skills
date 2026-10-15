# Literature review: the evidence behind the testing skill

*Searched and read on 2026-10-12. Companion to [SKILL.md](../SKILL.md); short form in [sources.md](sources.md).*

## Introduction

The testing skill gives advice, and every piece of advice of the form "do X because Y" asserts that Y is true: that test doubles drift, that recordings go stale, that agents game tests. This review takes twenty such claims from the skill and treats each as a research question. For every claim it searches the literature in both directions, for work that supports the claim and for work that contradicts or narrows it, reads the sources it cites, and states how strongly the claim can be made.

**Scope.** Twenty claims, one chapter each, in the order the skill makes them. Each chapter quotes the claim as it stood in the draft the review audited and, after its conclusion, the wording the skill adopted in response. Practitioner sources (Fowler, Shore, Google's *Software Engineering at Google*, Willison) are cited as attribution, that is, as evidence that experienced people recommend a practice; the benefit itself is backed only by empirical studies, and a chapter says so plainly when none exists.

**Search.** Every query was run on the same set of databases, on 2026-10-12, with the `scholar` command-line tool:

| Database | Status on 2026-10-12 | How the query was given |
|---|---|---|
| OpenAlex (OA; not "open access") | answered every query | Boolean free text |
| IEEE Xplore (IEEE) | answered every query; its daily quota ran out later the same day, so some per-database counts were not kept (marked *not recorded*) | Boolean free text |
| arXiv | answered every query | Boolean free text |
| Web of Science (WoS) | answered every query | the same keywords as `TS=(...)` |
| Scopus | answered every query (standard view: no abstracts) | the same keywords as `TITLE-ABS-KEY(...)` |
| DBLP | **failed every query**: it returned an anti-bot web page instead of data, so DBLP could not be searched | — |
| Semantic Scholar | not searched: the API key was rejected (HTTP 403) | — |

Each database returned at most 20 hits per query, so 20 means "at least 20". S1, S2 are support queries and C1, C2 counter-queries; a counter-query reuses the concept terms of the support query and adds the names of the opposite outcome. A failed search is shown as *failed*, never as 0.

**Screening.** All hits of a claim were classified by a language model (`scholar llm classify`, zero-shot, given the claim) into four categories: *supports the claim*, *qualifies or contradicts it*, *adjacent subtopic* (same field, different question) and *off-topic* (keyword overlap only). I read the supporting and qualifying rows and corrected the model where it was wrong; every cited source was checked by hand. Each chapter ends with the hit list of the records that bear on the claim. The model labels tool and method papers as supporting rather freely, so unreviewed *supports* rows are leads, not evidence.

**Reading.** Every cited source was opened. *Full text* means the passage quoted was read in the paper itself (publisher, author copy or preprint); *abstract only* means the publisher refused the full text and the quote comes from the abstract. Quotes are verbatim; the locator gives page, section or "abstract". After the review, the commissioning session checked every abstract-level quote mechanically against the abstract held by OpenAlex or arXiv, where one exists, and spot-read several full texts (Konstantinou et al. 2026, Alonso et al. 2026, Guey & Bougault 2026, Zhang 2026, Song 2026). All matched. One apparent mismatch was resolved in the review's favour: the arXiv listing abstract of Zhang (2026) is worded differently from the abstract printed in the v4 PDF, and the review quotes the PDF.

**Verdicts.**

| Verdict | Meaning |
|---|---|
| Supported | Empirical studies back the claim at the strength the skill states. |
| Qualified | Backed only under conditions; the chapter says which, and how the skill should word it. |
| Contested | Studies disagree, or the better evidence points the other way. |
| Practitioner-only | Experienced practitioners recommend it; no empirical study was found. |

**Audit trail.** The [literature](literature/) directory holds the bibliography with a provenance record for every source ([testing-claims.bib](literature/testing-claims.bib): how it was found, why it was picked, the verbatim quote, how it was verified, the counter-search) and, for each chapter's search session, the full classified hit list ([sessions](literature/sessions/): `.csv`), its BibTeX, the query list and a LaTeX audit table. Running `make` in that directory typesets this review as a LaTeX article.

## Summary

| # | Question (links to the chapter) | Skill section | Verdict |
|---|---|---|---|
| 1 | [Do hand-written test doubles drift from the real dependency?](#ch-mocks-diverge) | §1 | Qualified |
| 2 | [Do interaction assertions break on refactoring more than state assertions?](#ch-interaction-brittle) | §1 | Practitioner-only (benefit); contested (as a rule) |
| 3 | [Do sociable tests find more defects than solitary, mocked unit tests?](#ch-sociable-solitary) | §1 | Contested |
| 4 | [Do real local instances catch defects that mocks miss?](#ch-real-local) | §1 | Practitioner-only |
| 5 | [Are recorded responses more realistic than hand-written stubs?](#ch-record-replay) | §1 | Qualified |
| 6 | [Do web APIs change often enough for recordings to go stale?](#ch-api-evolution) | §3 | Supported |
| 7 | [Do periodic checks against the real service detect drift in test doubles?](#ch-contract-tests) | §2-3 | Qualified (thin) |
| 8 | [Do invariant and shape assertions keep tests valid without losing fault detection?](#ch-invariant-assertions) | §2 | Qualified |
| 9 | [Are time, randomness and the network major causes of flaky tests?](#ch-flaky) | §1 | Qualified |
| 10 | [Is keyed-hash pseudonymised test data still personal data?](#ch-pseudonymisation) | §4 | Supported (key holder); qualified (others) |
| 11 | [Do secrets and personal data leak through repositories?](#ch-secrets-leak) | §4 | Supported |
| 12 | [Does free text carry identifiers that pattern-based scrubbing misses?](#ch-free-text-deid) | §4 | Supported (clinical text) |
| 13 | [Does writing tests first improve quality or productivity?](#ch-tdd) | §5 | Contested |
| 14 | [Does seeing a test fail on a deliberate break show it can detect faults?](#ch-mutation) | §5 | Supported (qualified) |
| 15 | [Do LLM coding agents do better when they can run tests?](#ch-llm-exec-feedback) | §5 | Supported (qualified) |
| 16 | [Do coding agents game tests to make them pass?](#ch-agents-game-tests) | §5 | Supported |
| 17 | [Does running the existing tests first help a coding agent?](#ch-run-tests-first) | §5 | Practitioner-only |
| 18 | [Does a reviewer in a fresh context find what the author missed?](#ch-fresh-review) | §5 | Qualified |
| 19 | [Does exploratory, manual trying find defects scripted tests miss?](#ch-exploratory) | §5 | Contested |
| 20 | [Do hand-written fakes need verifying against the real implementation?](#ch-verified-fakes) | §1 | Practitioner-only |

## The answers in brief

Each answer condenses the chapter's conclusion; the chapter gives the
sources and the counter-evidence.

1. **Do hand-written test doubles drift from the real dependency?**
   Yes, they can, and developers report keeping them in step as a key
   challenge. Nothing shows that a hand-written body is *the most likely*
   thing to be wrong, so the skill dropped that superlative. *Qualified.*
2. **Do interaction assertions break on refactoring more than state
   assertions?** That they break on refactoring is practitioner
   experience, not a measured result, and mock assertions do catch faults
   that state assertions miss, mainly for calls to external resources.
   Prefer results and state when they can be checked; keep interaction
   assertions for effects that cannot be observed otherwise.
   *Practitioner-only; contested as a blanket rule.*
3. **Do sociable tests find more defects than solitary, mocked unit
   tests?** No study shows it: the two kinds find partly different faults,
   and the largest study found no difference by defect type. Real
   collaborators stay the default because they cannot drift, not because
   they find more. *Contested.*
4. **Do real local instances catch defects that mocks miss?** Unknown: no
   study compares them. The advice rests on practice, and slowness, setup
   and shared-resource flakiness are the reasons developers give for
   mocking instead. *Practitioner-only.*
5. **Are recorded responses more realistic than hand-written stubs?** For
   what was recorded, yes, and recordings are used in industry. But they
   cover nothing outside the recording, so error paths and edge cases
   need an injected failure or a fake. No study compares the two.
   *Qualified.*
6. **Do web APIs change often enough for recordings to go stale?** Yes
   for evolving APIs: breaking changes are common and often arrive
   without a major version bump. A sizeable minority of APIs never break.
   *Supported.*
7. **Do periodic checks against the real service detect drift in test
   doubles?** Yes, on thin evidence: contract tests caught every seeded
   integration defect in the one case study found, and an action-research
   study agrees. Nothing points the other way. *Qualified (thin).*
8. **Do invariant and shape assertions keep tests valid without losing
   fault detection?** Both effects are real: exact values on changing
   data are brittle, but assertions that check too little miss faults.
   Relational properties keep most of the detection power, so assert the
   strongest invariant that holds on live data, not merely the shape.
   *Qualified.*
9. **Are time, randomness and the network major causes of flaky tests?**
   They are documented causes, and the network leads in JavaScript, but
   in Java and Python asynchronous waits, concurrency and test-order
   dependency dominate. Isolating each test addresses the larger share.
   *Qualified.*
10. **Is keyed-hash pseudonymised test data still personal data?** Yes for
    whoever holds the key, and an unkeyed hash can be reversed by hashing
    candidate names. For a recipient without the key, the Court of Justice
    has held that pseudonymised data are not always personal data.
    *Supported for the key holder; qualified for others.*
11. **Do secrets and personal data leak through repositories?** Yes:
    leaked secrets on GitHub are pervasive, found within seconds and
    rarely cleaned from history, so a pushed secret is published. Personal
    data in test fixtures has not been studied. *Supported.*
12. **Does free text carry identifiers that pattern-based scrubbing
    misses?** Yes: automated scrubbing misses identifiers by a wide margin,
    and even fully masked text can be re-identified from context.
    Replacing free text wholesale avoids the problem. *Supported (clinical
    and biographical text).*
13. **Does writing tests first improve quality or productivity?** Not in
    general: the evidence is mixed, with a small quality gain at best and
    no clear effect of the order itself. For LLM work, tests written from
    faulty code inherit its faults, so the skill justifies red/green by
    test independence, not by TDD's general benefits. *Contested.*
14. **Does seeing a test fail on a deliberate break show it can detect
    faults?** Yes, for that kind of fault: detecting mutants correlates
    with detecting real faults, though weakly once suite size is
    controlled, and tests that pass whatever the code does are common. A
    red result shows the test catches that break, not that the suite is
    adequate. *Supported (qualified).*
15. **Do LLM coding agents do better when they can run tests?** Yes, when
    the tests are reliable and independent of the code. Self-repair gains
    are often modest once cost is counted, and tests the model writes for
    its own code bias the result. *Supported (qualified).*
16. **Do coding agents game tests to make them pass?** Yes: agents,
    including widely used commercial ones, have been seen deleting,
    editing and special-casing tests. How often depends on the task, test
    access and instructions, and explicit instructions reduce it.
    *Supported.*
17. **Does running the existing tests first help a coding agent?**
    Unknown: no study was found, so the rule is attributed as practice.
    Keep agent instructions short, since verbose testing instructions made
    a small agent worse in one study. *Practitioner-only.*
18. **Does a reviewer in a fresh context find what the author missed?**
    Partly: one small experiment found a second review helps only in a
    fresh session, but not significantly more than a single review.
    Models correct themselves poorly without external feedback, so ask
    the reviewer for runnable checks (break the code: does a test go
    red?), not an opinion. *Qualified.*
19. **Does exploratory, manual trying find defects scripted tests miss?**
    Mixed: one replicated experiment found it finds more than scripted
    manual testing, an earlier one found no difference, and none studies
    it alongside an automated suite. The skill only asks to turn surprises
    into tests, which does not depend on the answer. *Contested.*
20. **Do hand-written fakes need verifying against the real
    implementation?** No study tests it; it is practitioner advice,
    supported indirectly by the evidence that doubles drift (question 1)
    and that static doubles cover only what they encode.
    *Practitioner-only.*

<a id="ch-mocks-diverge"></a>

## 1. Do hand-written test doubles drift from the real dependency?

**Claim in the draft skill.** §1: "A hand-written body encodes what we *believe* the service returns, and that belief is the thing most likely to be wrong."

**Research question.** Do hand-written mocks and other test doubles diverge from the dependency they replace, so that tests pass while the real integration is broken? Tested strength: that this *can* happen and is a recognised problem, and whether it is the *most likely* failure.

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("mock objects" OR mocking OR "test doubles" OR stubs) AND ("unit test" OR "unit testing" OR "software testing" OR "test code") AND (evolution OR "co-evolution" OR maintenance OR inconsistency OR outdated)` |
| S2 | `("mock objects" OR mocking OR "test doubles" OR stubs) AND ("unit test" OR "unit testing" OR "software testing" OR "test code") AND (integration OR "false confidence" OR "missed faults" OR "fault detection")` |
| C1 | `("mock objects" OR mocking OR "test doubles" OR stubs) AND ("unit test" OR "unit testing" OR "software testing" OR "test code") AND (benefits OR advantages OR effectiveness OR "test isolation")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 20 | 20 | 2 | 41 | 16 | 20 |
| S2 | failed | 20 | 20 | 8 | 41 | 19 | 20 |
| C1 | failed | not recorded | 20 | 9 | 45 | 19 | 20 |

The session holds 218 unique records.

*Audit trail:* scholar session `t-mocks-diverge`; hit list [t-mocks-diverge.csv](literature/sessions/t-mocks-diverge.csv), records [t-mocks-diverge.bib](literature/sessions/t-mocks-diverge.bib), queries [t-mocks-diverge.queries.tsv](literature/sessions/t-mocks-diverge.queries.tsv), LaTeX audit table [t-mocks-diverge-table.tex](literature/sessions/t-mocks-diverge-table.tex).
<!-- Author note: the session also holds a query S0 without the software-testing anchor (matched astronomy 'mock catalogues'); it was rerun as S1/S2, which recovered every relevant S0 hit. S0 rows are classified but not reported. -->

### Findings

**Supporting.**

- [Spadini et al. 2019](#ref-Spadini2019): Hand-written mocks can diverge from the real dependency: developers find keeping a mock's behaviour compatible with the real class hard, and production changes force mock changes.
  > "A problem when using mocks is maintaining the behavior of the mock compatible with the behavior of the original class, especially when the original class is poorly designed or highly coupled. As the production class tends to change often, the mock object becomes unstable and, as a consequence, more prone to change."
  > (p. 1479, 'Unstable dependencies'; read in full text)
- [Spadini et al. 2017](#ref-Spadini2017): Developers report that keeping mock behaviour compatible with the real class is a key mocking challenge.
  > "Among the key challenges, developers report that maintaining the behavior of the mock compatible with the behavior of original class is hard and that mocking increases the coupling between the test and the production code."
  > (abstract; abstract only)
- [Lehvä et al. 2019](#ref-Lehva2019): Component tests with doubles stayed green while seeded integration defects went undetected.
  > "there is a chance to accidentally or unconsciously change the component tests to match the new functionality without realizing the implications on the other side of the integration. That leaves the integration broken while the component tests are still passing."
  > (p. 507, §4.1; read in full text)
- [Zhu et al. 2023](#ref-Zhu2023): Stub code for mock objects breaks and has to be repaired as code evolves (corroboration that doubles go out of date).
  > "developing and maintaining stub code is labor-intensive and error-prone"
  > (abstract; abstract only)
- [de Aquino & Alves 2025](#ref-DeAquino2025): Hand-declared API mocks often do not comply with the real service's API; a validating tool improved compliance by 24.1%.
  > "API mocks, which intercept communications with external services to return simulated responses, must closely align with the actual service to ensure realistic and effective test scenarios."
  > (abstract; abstract only)
- [Winters et al. 2020](#ref-Winters2020): Practitioner (Google): overuse of mocks produced test code that drifted from the real implementation.
  > "overuse of mocking frameworks had a tendency to pollute tests with repetitive code that got out of sync with the real implementation and made refactoring difficult."
  > (ch. 13, 'Real Implementations'; read in full text)

**Qualifying or contradicting.**

- [Taheri Ghazvini 2025](#ref-TaheriGhazvini2025): Some faults surface only in integration with real collaborators, others only in isolated unit tests.
  > "Some faults were only exposed in integration, others only through unit testing. The results show that the unit testing and integration testing exercise different aspects of the integrated functions and carry distinct tradeoffs, reinforcing their complementary roles in practice."
  > (abstract, p. iii; read in full text)

### Discussion and limitations

The evidence is of two kinds: developers' reports (interviews and a 105-person survey) confirmed by mining how mocks change, and one case study that seeded defects. Neither measures how often a mock drifts in practice or how often a drifted mock hides a real fault. The counter-query, which looked for benefits and effectiveness of mocking, returned studies of mocking practice and tools; none showed that mocks stay in step with what they replace. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Yes, test doubles can drift from the real dependency and developers report keeping them compatible as a key challenge; there is no evidence for the stronger claim that a hand-written response body is *the most likely* thing to be wrong. Verdict: **Qualified.** The skill should say that keeping hand-written doubles in step with the real service is a known, reported problem, and drop the superlative.

**Wording in the skill after this review.** §1 now reads: "A hand-written body encodes what we *believe* the service returns, and keeping such doubles in step with the real service is a known, reported problem." The superlative is gone.

### Future work

This search did not obtain the full text of the conference paper by Spadini et al. (2017) or of Zhu et al. (2023); both were read at abstract level. The field lacks a measurement of drift: how often doubles diverge, and how often that hides a fault a real dependency would have exposed. A mining study pairing mock changes with later integration failures would settle it; if drift turned out rare, the skill's preference for recordings would rest on convenience rather than correctness.

Suggested by a reviewer after the search, not retrieved by the recorded queries, and not read: Pereira & Hora 2020, "Assessing mock classes: an empirical study" (ICSME 2020).

### Hit list

Records bearing on the claim: 7 cited (reviewed by hand), 0 further supporting and 0 further qualifying or contradicting as labelled by the model (unreviewed), out of 218 records; 137 adjacent and 74 off-topic records are not listed. The full classified list is in [t-mocks-diverge.csv](literature/sessions/t-mocks-diverge.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [From Isolation to Integration: An empirical study on differences between unit and integration testing with applications to C programs](https://doi.org/10.22215/etd/2025-16598) | 2025 | supports | cited: integration-faults-missed |
| [StubCoder : Automated Generation and Repair of Stub Code for Mock Objects](https://doi.org/10.1145/3617171) | 2023 | supports | cited: mock-compatibility |
| [From isolation to integration: An empirical study on differences between unit and integration testing with applications to C programs](https://doi.org/10.1016/j.infsof.2026.108341) | 2026 | supports | cited: integration-faults-missed |
| [Zimic: Bridging the Gaps in API Mocking for Typescript Projects](https://doi.org/10.1109/COMPSAC65507.2025.00177) | 2025 | supports | cited: mock-compatibility |
| [Understanding and Characterizing Mock Assertions in Unit Tests](https://doi.org/10.1145/3715741) | 2025 | qualifies | cited: mock-assertion-value |
| [To Mock or Not to Mock? An Empirical Study on Mocking Practices](https://doi.org/10.1109/msr.2017.61) | 2017 | supports | cited: mock-compatibility |
| [Mock objects for testing java systems: Why and how developers use them, and how they evolve](https://doi.org/10.1007/s10664-018-9663-0) | 2019 | supports | cited: mock-compatibility |

<a id="ch-interaction-brittle"></a>

## 2. Do interaction assertions break on refactoring more than state assertions?

**Claim in the draft skill.** §1: "Interaction assertions break on every refactor." and Never: "assert on call sequences (`assert_called_with`) when a result or state can be checked instead".

**Research question.** Do tests that verify interactions with test doubles (which methods were called, with which arguments) break under refactoring more often than tests that check results and state? Tested strength: "break on every refactor".

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("mock objects" OR mocking OR "interaction testing" OR "behavior verification" OR "state verification") AND ("unit test" OR "unit testing" OR "software testing" OR "test code") AND (refactoring OR fragile OR brittle OR "test breakage")` |
| S2 | `("test breakage" OR "broken tests" OR "test repair" OR "fragile tests" OR "test smells") AND refactoring AND ("unit test" OR "unit testing" OR "software testing" OR "test code")` |
| C1 | `("mock objects" OR mocking OR "interaction testing" OR "behavior verification" OR "state verification") AND ("unit test" OR "unit testing" OR "software testing" OR "test code") AND (refactoring OR "test maintenance" OR robustness) AND (comparison OR empirical OR benefits)` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | not recorded | 20 | 2 | 41 | 11 | 14 |
| S2 | failed | not recorded | 20 | 7 | 44 | 20 | 20 |
| C1 | failed | 16 | 20 | 2 | 37 | 8 | 11 |

The session holds 127 unique records.

*Audit trail:* scholar session `t-interaction-brittle`; hit list [t-interaction-brittle.csv](literature/sessions/t-interaction-brittle.csv), records [t-interaction-brittle.bib](literature/sessions/t-interaction-brittle.bib), queries [t-interaction-brittle.queries.tsv](literature/sessions/t-interaction-brittle.queries.tsv), LaTeX audit table [t-interaction-brittle-table.tex](literature/sessions/t-interaction-brittle-table.tex).

### Findings

**Supporting.**

- [Fowler 2007](#ref-Fowler2007): Practitioner: mockist tests couple to implementation, so implementation changes break them more than classic tests.
  > "Coupling to the implementation also interferes with refactoring, since implementation changes are much more likely to break tests than with classic testing."
  > ('Mocks Aren't Stubs', section on coupling tests to implementations; read in full text)
- [Winters et al. 2020](#ref-Winters2020): Practitioner (Google): interaction testing exposes implementation details and makes tests brittle.
  > "Interaction testing should be avoided when possible: it leads to tests that are brittle because it exposes implementation details of the system under test."
  > (ch. 13, 'TL;DRs'; read in full text)
- [Spadini et al. 2019](#ref-Spadini2019): Developers report that mocking couples test code to production code.
  > "developers report that maintaining the behavior of the mock compatible with the behavior of original class is hard and that mocking increases the coupling between the test and the production code."
  > (abstract, p. 1461; read in full text)
- [Knight & Bhowmik 2025](#ref-Knight2025): Developers report frustration with fragile unit tests that break during refactoring.
  > "The findings reveal developer expectations that unit test suites should enable safe, productive change, but also frustrations with fragile tests that break during refactoring."
  > (abstract; abstract only)

**Qualifying or contradicting.**

- [Zhu et al. 2025](#ref-Zhu2025): Mock (interaction) assertions detect faults that state assertions miss, mainly for calls to external resources.
  > "782 of 1,557 (50%) of the injected faults detected by mock assertions were not detected by test assertions, and the Jaccard similarity between M_MA and M_TA is only 32%. The result shows that mock assertions can complement test assertions in detecting potential faults."
  > (p. FSE026:16, §7; read in full text)

### Discussion and limitations

No study was found that measures breakage of interaction versus state assertions under refactoring. The supporting side is practitioner experience and developer perception; the only empirical study of mock assertions measured their fault detection, and found that they add to it. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Not as stated: the claim that interaction assertions break on every refactor is practitioner experience, not a measured result, and mock assertions catch faults that state assertions miss, mainly for calls to external resources. Verdict: **Practitioner-only** for the brittleness, **contested** as a blanket rule. The skill's own qualifier (prefer results and state *when they can be checked*) is the defensible form; replace "break on every refactor" with "tie a test to how the code works, so refactoring tends to break them" and keep interaction assertions for effects that cannot be observed otherwise.

**Wording in the skill after this review.** §1 now reads: "Interaction assertions tie a test to how the code works, so refactoring tends to break them; keep them for effects that cannot be observed otherwise, such as a call to an external service." The "Never" rule keeps its qualifier "when a result or state can be checked instead". A later revision, made after the skill was tried on a real test suite, adds: "Assert such effects at the outermost owned boundary, on the recorded requests or the fake's state, not on calls to our own domain objects." This narrows where the remaining interaction assertions go; it rests on the same practitioner sources and was not searched separately.

### Future work

Several sources were read only at abstract level (Knight & Bhowmik 2025). The field lacks a study that refactors code under both kinds of tests and counts the breakages; if interaction tests turned out no more fragile, the rule would rest on readability alone.

Suggested by a reviewer after the search, not retrieved by the recorded queries, and not read: Meszaros 2007, *xUnit Test Patterns* ("Fragile Test", "Overspecified Software").

### Hit list

Records bearing on the claim: 5 cited (reviewed by hand), 0 further supporting and 0 further qualifying or contradicting as labelled by the model (unreviewed), out of 127 records; 94 adjacent and 28 off-topic records are not listed. The full classified list is in [t-interaction-brittle.csv](literature/sessions/t-interaction-brittle.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [Understanding and Characterizing Mock Assertions in Unit Tests](https://doi.org/10.1145/3715741) | 2025 | qualifies | cited: mock-assertion-value |
| [Point/counterpoint](https://doi.org/10.1109/MS.2007.84) | 2007 | supports | cited: practitioner-opinion |
| [Mock objects for testing java systems](https://doi.org/10.1007/s10664-018-9663-0) | 2018 | supports | cited: mock-coupling |
| [To Mock or Not to Mock? An Empirical Study on Mocking Practices](https://doi.org/10.1109/msr.2017.61) | 2017 | supports | cited: mock-coupling |
| [Toward a Resilience-Oriented Understanding of Unit Test Suites and Refactoring in Software Evolution](https://doi.org/10.1109/ICSME64153.2025.00092) | 2025 | supports | cited: fragile-tests |

<a id="ch-sociable-solitary"></a>

## 3. Do sociable tests find more defects than solitary, mocked unit tests?

**Claim in the draft skill.** §1, rung 1: "Sociable tests through our real collaborators"; Never: "mock code we own just to isolate a unit".

**Research question.** Do tests that run through real collaborators (sociable or integration-style tests) detect more defects, or survive refactoring better, than solitary unit tests that replace collaborators with test doubles?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("unit tests" OR "unit testing") AND ("integration tests" OR "integration testing") AND ("fault detection" OR defects OR effectiveness OR "mutation score")` |
| S2 | `("sociable tests" OR "solitary tests" OR "test isolation" OR mocking OR "mock objects") AND ("unit test" OR "unit testing" OR "software testing" OR "test code") AND ("fault detection" OR "mutation score" OR "defect detection")` |
| C1 | `("unit tests" OR "unit testing" OR "test isolation" OR mocking) AND ("integration tests" OR "integration testing") AND ("fault localization" OR "execution time" OR maintenance OR cost OR flakiness)` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 20 | 20 | 5 | 43 | 20 | 20 |
| S2 | failed | 4 | 20 | 2 | 25 | 3 | 4 |
| C1 | failed | 20 | 20 | 2 | 41 | 20 | 20 |

The session holds 155 unique records.

*Audit trail:* scholar session `t-sociable-solitary`; hit list [t-sociable-solitary.csv](literature/sessions/t-sociable-solitary.csv), records [t-sociable-solitary.bib](literature/sessions/t-sociable-solitary.bib), queries [t-sociable-solitary.queries.tsv](literature/sessions/t-sociable-solitary.queries.tsv), LaTeX audit table [t-sociable-solitary-table.tex](literature/sessions/t-sociable-solitary-table.tex).

### Findings

**Supporting.**

- [Fowler 2014](#ref-Fowler2014): Practitioner: definition of sociable vs solitary unit tests (Jay Fields' terms).
  > "A more important distinction is whether the unit you're testing should be sociable or solitary"
  > (bliki 'Unit Test', 5 May 2014, 'Solitary or Sociable?'; read in full text)
- [Shore 2023](#ref-Shore2023): Practitioner: sociable, state-based tests with Nullables instead of mocks; narrow integration tests against local systems configured like production.
  > "The patterns combine sociable, state-based tests with a novel infrastructure technique called “Nullables.”"
  > ('Testing Without Mocks: A Pattern Language', 16 Feb 2023; read in full text)
- [Winters et al. 2020](#ref-Winters2020): Practitioner (Google): real implementations make tests more realistic.
  > "Using real implementations for dependencies makes the system under test more realistic given that all code in these real implementations will be executed in the test."
  > (ch. 13, 'Prefer Realism Over Isolation'; read in full text)

**Qualifying or contradicting.**

- [Trautsch et al. 2020](#ref-Trautsch2020): In 38,782 Java test cases, neither unit nor integration tests (IEEE definitions) were more capable of detecting any mutation defect type.
  > "We could not find any evidence that one test type is more capable of detecting certain defect types than the other one."
  > (abstract, Results; abstract only)
- [Taheri Ghazvini 2025](#ref-TaheriGhazvini2025): Unit tests with stubs and integration tests through real calls detect different faults; neither dominates.
  > "Some faults were only exposed in integration, others only through unit testing. The results show that the unit testing and integration testing exercise different aspects of the integrated functions and carry distinct tradeoffs, reinforcing their complementary roles in practice."
  > (abstract, p. iii; read in full text)
- [Gregor et al. 2025](#ref-Gregor2025): In a TrainTicket benchmark, most of 51 faults were found only by component tests, 10 only by integration tests, 5 by both.
  > "Out of the 51 discovered faults, 36 were detected solely by component tests, 10 solely by integration tests, and 5 by component and integration tests."
  > (§IV-G, RQ5; read in full text)
- [Orellana et al. 2017](#ref-Orellana2017): Unit and integration tests behave differently in CI: unit tests cause more breaking builds and their defects take longer to fix.
  > "we discovered that unit tests cause more breaking builds, that fixing the defects exposed by unit tests takes longer and implies more coordination between team members."
  > (abstract; abstract only)

### Discussion and limitations

The supporting side is practitioner advice; the empirical side compares unit and integration tests, which is close to but not identical with solitary versus sociable tests. In the microservice benchmark the integration suite covered only happy paths, so its smaller share of faults is not a fair head-to-head result. Trautsch et al. (2020) used mutation defects rather than real faults. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

No: no study shows that sociable tests find more defects; the studies that compare the two kinds find that they detect partly different faults, and the largest found no difference by defect type. Verdict: **Contested.** The skill can keep real collaborators as its default for realism (rung 1), but must not justify it with a defect-finding advantage.

**Wording in the skill after this review.** Unchanged: the skill makes sociable tests the default but makes no claim that they find more defects, and none should be added. The reason for the default is chapter 1: a real collaborator cannot drift out of step the way a double can.

### Future work

The journal version of Taheri Ghazvini's study (Information and Software Technology, 2026) was not obtained, and Trautsch et al. (2020) was read at abstract level. The field lacks a controlled comparison of sociable and solitary tests on real faults and on refactoring breakage, which is what the skill's rule actually assumes.

### Hit list

Records bearing on the claim: 5 cited (reviewed by hand), 0 further supporting and 5 further qualifying or contradicting as labelled by the model (unreviewed), out of 155 records; 119 adjacent and 26 off-topic records are not listed. The full classified list is in [t-sociable-solitary.csv](literature/sessions/t-sociable-solitary.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [Are unit and integration test definitions still valid for modern Java projects? An empirical study on open-source projects](https://doi.org/10.1016/j.jss.2019.110421) | 2020 | qualifies | cited: complementary-fault-detection |
| [From Isolation to Integration: An empirical study on differences between unit and integration testing with applications to C programs](https://doi.org/10.22215/etd/2025-16598) | 2025 | qualifies | cited: complementary-fault-detection |
| [On the Differences between Unit and Integration Testing in the TravisTorrent Dataset](https://doi.org/10.1109/MSR.2017.25) | 2017 | qualifies | cited: ci-differences |
| [From isolation to integration: An empirical study on differences between unit and integration testing with applications to C programs](https://doi.org/10.1016/j.infsof.2026.108341) | 2026 | qualifies | cited: complementary-fault-detection |
| [Benchmarking Component and Integration Testing in Microservices: Test Suites and Fault Analysis on TrainTicket](https://doi.org/10.1109/SOSE67019.2025.00009) | 2025 | qualifies | cited: complementary-fault-detection |

<a id="ch-real-local"></a>

## 4. Do real local instances catch defects that mocks miss?

**Claim in the draft skill.** §1, rung 2: "When a dependency can run locally." (`tmp_path` files, SQLite or an in-memory DB, a real `git init`, `http.server` on localhost, a container)

**Research question.** Do tests against real local instances of a dependency (in-memory or embedded databases, containers, temporary file systems, local servers) catch defects that mocks miss, and at what cost in speed and flakiness?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("in-memory database" OR "embedded database" OR testcontainers OR docker OR container OR "local instance") AND ("integration testing" OR "integration tests" OR "unit testing" OR "software testing") AND (mock OR mocking OR "test doubles" OR database)` |
| C1 | `("in-memory database" OR "embedded database" OR testcontainers OR docker OR container OR "local instance") AND ("integration testing" OR "integration tests" OR "unit testing" OR "software testing") AND (flaky OR flakiness OR slow OR "execution time" OR cost)` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 20 | 20 | 6 | 45 | 8 | 20 |
| C1 | failed | not recorded | 20 | 16 | 54 | 10 | 20 |

The session holds 135 unique records.

*Audit trail:* scholar session `t-real-local`; hit list [t-real-local.csv](literature/sessions/t-real-local.csv), records [t-real-local.bib](literature/sessions/t-real-local.bib), queries [t-real-local.queries.tsv](literature/sessions/t-real-local.queries.tsv), LaTeX audit table [t-real-local-table.tex](literature/sessions/t-real-local-table.tex).

### Findings

**Supporting.**

- [Shore 2023](#ref-Shore2023): Practitioner: run narrow integration tests against local systems configured like production.
  > "Make sure that your test systems use the same configuration as your production environment. Otherwise your code will fail in production when it encounters subtle incompatibilities."
  > ('Narrow Integration Tests'; read in full text)
- [Winters et al. 2020](#ref-Winters2020): Practitioner (Google): real implementations make tests more realistic.
  > "Using real implementations for dependencies makes the system under test more realistic given that all code in these real implementations will be executed in the test."
  > (ch. 13, 'Prefer Realism Over Isolation'; read in full text)

**Qualifying or contradicting.**

- [Spadini et al. 2019](#ref-Spadini2019): Developers mock databases and web services because they are slow and complex to set up (the cost side).
  > "The results of the first part of our study show that classes related to external resources, such as databases and web services, are often mocked, due to their inherently complex setup and slowness."
  > (p. 1463; read in full text)
- [Luo et al. 2014](#ref-Luo2014): External resources are behind many order-dependent flaky tests (a flakiness cost of shared real resources).
  > "Many Test Order Dependency flaky tests (47%) are caused by dependency on external resources."
  > (summary of findings, F.7; read in full text)
- [Hora & Robbes 2026](#ref-Hora2026): Context: coding agents add mocks more often than human developers.
  > "36% of commits made by coding agents add mocks to tests, compared with 26% by non-agents"
  > (abstract; abstract only)

### Discussion and limitations

Neither the support query nor the counter-query returned an empirical comparison of real local instances against mocks for defect detection. What was found bears on the cost side only, and indirectly. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Unknown: no empirical study compares real local instances with mocks for defect detection; the advice rests on practitioner experience, and the documented costs (slowness, setup, shared-resource flakiness) are the reasons developers give for mocking. Verdict: **Practitioner-only.** The skill may keep rung 2 as engineering advice; it should not claim a measured benefit, and could add that each test needs its own instance (as `tmp_path` provides) to avoid order dependence.

**Wording in the skill after this review.** Unchanged: rung 2 stays as practitioner advice, attributed in sources.md.

### Future work

The field lacks a study that runs the same tests against mocks, in-memory substitutes and the production-grade dependency (for example SQLite versus PostgreSQL) and counts the faults each catches; if in-memory substitutes missed dialect-specific faults, rung 2 would need a warning about substitutes that differ from production.

### Hit list

Records bearing on the claim: none from this chapter's own session were cited; the sources cited in this chapter (Shore, Winters, Spadini, Luo, Hora) came from other chapters' sessions or were retrieved as known items, so this chapter's own session contributed none. Of the records the model labelled (unreviewed): 0 further supporting and 3 further qualifying or contradicting as labelled by the model (unreviewed), out of 135 records; 56 adjacent and 76 off-topic records are not listed. The full classified list is in [t-real-local.csv](literature/sessions/t-real-local.csv). The unreviewed rows are in that CSV.


<a id="ch-record-replay"></a>

## 5. Are recorded responses more realistic than hand-written stubs?

**Claim in the draft skill.** §1, rung 3: "Record the **live** responses once, pseudonymized (section 4), and replay them offline." Never: "hand-write a response body that we could have recorded from the live service."

**Research question.** Do tests that replay recorded real traffic (record-and-replay, service virtualisation, mocks generated from production data) give more realistic tests than hand-written stubs?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("record and replay" OR "record-replay" OR "capture and replay" OR "service virtualization" OR "traffic recording" OR "generated mocks") AND (testing OR "unit tests" OR "integration tests") AND (mock OR stub OR "web service" OR API)` |
| C1 | `("record and replay" OR "record-replay" OR "capture and replay" OR "service virtualization" OR "traffic recording" OR "generated mocks") AND (testing OR "unit tests" OR "integration tests") AND (limitations OR maintenance OR outdated OR brittle OR "false positives")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | not recorded | 20 | 20 | 44 | 12 | 20 |
| C1 | failed | not recorded | 20 | 20 | 55 | 20 | 20 |

The session holds 123 unique records.

For Zhang (2026), the arXiv API listing (`export.arxiv.org/api/query?id_list=2604.04806`, retrieved 2026-10-12, last updated 2026-06-26) was compared with the v4 PDF: the two abstracts differ in wording and figures, so each quote below names which one it comes from.

*Audit trail:* scholar session `t-record-replay`; hit list [t-record-replay.csv](literature/sessions/t-record-replay.csv), records [t-record-replay.bib](literature/sessions/t-record-replay.bib), queries [t-record-replay.queries.tsv](literature/sessions/t-record-replay.queries.tsv), LaTeX audit table [t-record-replay-table.tex](literature/sessions/t-record-replay-table.tex).

### Findings

**Supporting.**

- [Tiwari et al. 2024](#ref-Tiwari2024): Mocks generated from production observations reproduce realistic execution contexts and their oracles detect regressions.
  > "All the generated test cases are executable, and 52.4% of them successfully mimic the complete execution context of the target methods observed in production. The mock-based oracles are also effective at detecting regressions within the target methods"
  > (abstract; read in full text)
- [Liu et al. 2022](#ref-Liu2022): Replaying recorded traffic is common industrial practice.
  > "Using recorded online traffic for the regression testing of web applications has become a common practice in industry."
  > (abstract; abstract only)

**Qualifying or contradicting.**

- [Zhang 2026](#ref-Zhang2026): Recorded doubles reproduce only behaviour encoded when they were recorded.
  > "Existing approaches—record-replay, pattern-mining, and specification-driven stubs—generate a static artifact before tests run, so they can only reproduce behaviors encoded at generation time."
  > (abstract, arXiv:2604.04806v4 PDF; read in full text)
- [Zhang 2026](#ref-Zhang2026): Off the recorded traces, replay rarely reproduces the values a caller checks (v4 PDF).
  > "record-replay and pattern-mining reproduce the values a caller asserts on in at most 1% of scenarios."
  > (abstract, arXiv:2604.04806v4 PDF; read in full text)
- [Zhang 2026](#ref-Zhang2026): The arXiv listing abstract gives per-category figures: 0% on error handling and 12% on code reasoning (and 62% status / 16% response-shape fidelity overall).
  > "These artifacts can only reproduce behaviors encoded at generation time; on error-handling and code-reasoning scenarios, which are underrepresented in typical trace corpora, record-replay achieves 0% and 12% fidelity in our evaluation."
  > (arXiv listing abstract, metadata updated 2026-06-26; read in full text)
- [Liu et al. 2022](#ref-Liu2022): Recorded traffic often cannot be replayed without handling environment dependencies.
  > "Using recorded online traffic for the regression testing of web applications has become a common practice in industry. However, this “record and replay” on microservices is challenging because simply recorded online traffic (i.e., values for variables or input/output for function calls) often cannot be successfully replayed"
  > (abstract; abstract only)
- [Versteeg et al. 2016](#ref-Versteeg2016): Record-and-replay service emulation is limited in accuracy.
  > "Models require deep knowledge of the target services while record-and-replay is limited in accuracy."
  > (abstract; abstract only)

### Discussion and limitations

No controlled comparison of recorded responses against hand-written stubs was found. The supporting studies show feasibility and industrial use; the qualifying ones show that a recording is faithful to what was recorded and to nothing else. Zhang (2026) is a single-author preprint whose replay baseline is the author's own HoverFly-style implementation and whose test scenarios were deliberately designed outside the recorded traces, with an emphasis on error handling, so its figures measure that gap rather than replay on recorded paths. The abstract printed in the v4 PDF and the abstract on the arXiv listing differ in wording and figures; both are quoted above with their source. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Partly: recordings reproduce real behaviour for the interactions that were recorded, and are used in industry, but they cover nothing outside the recording, and no study compares them with hand-written stubs. Verdict: **Qualified.** The skill should add that a recording covers only what was recorded, and that error paths and edge cases need injected failures (rung 5) or a fake (rung 4).

**Wording in the skill after this review.** Rung 3 now adds: "A recording covers only what was recorded: error paths and edge cases need an injected failure (rung 5) or a fake (rung 4)."

### Future work

Liu et al. (2022) and Versteeg et al. (2016) were read at abstract level. The field lacks a comparison of cassettes and hand-written stubs on the same faults, including how fast each goes stale.

Suggested by a reviewer after the search, not retrieved by the recorded queries, and not read: Saff & Ernst, test factoring (2004/2005), and Elbaum et al. 2006, "Carving differential unit test cases from system test cases" (FSE 2006).

### Hit list

Records bearing on the claim: 6 cited (reviewed by hand), 0 further supporting and 1 further qualifying or contradicting as labelled by the model (unreviewed), out of 123 records; 65 adjacent and 51 off-topic records are not listed. The full classified list is in [t-record-replay.csv](literature/sessions/t-record-replay.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [MIRAGE: Online LLM Simulation for Microservice Dependency Testing](https://doi.org/10.48550/arXiv.2604.04806) | 2026 | qualifies | cited: replay-fidelity |
| [RICK: Generating Mocks from Production Data](https://doi.org/10.1109/icst57152.2023.00051) | 2023 | supports | cited: production-derived-mocks |
| [Mimicking Production Behavior With Generated Mocks](https://doi.org/10.1109/TSE.2024.3458448) | 2024 | supports | cited: production-derived-mocks |
| [Record and Replay of Online Traffic for Microservices with Automatic Mocking Point Identification](https://doi.org/10.1109/icse-seip55303.2022.9793867) | 2022 | qualifies | cited: replay-fidelity |
| [Record and Replay of Online Traffic for Microservices with Automatic Mocking Point Identification](https://doi.org/10.1145/3510457.3513029) | 2022 | qualifies | cited: replay-fidelity |
| [Opaque Service Virtualisation: A Practical Tool for Emulating Endpoint Systems](https://doi.org/10.1145/2889160.2889242) | 2016 | qualifies | cited: replay-fidelity |

<a id="ch-api-evolution"></a>

## 6. Do web APIs change often enough for recordings to go stale?

**Claim in the draft skill.** §3: "A recording is a snapshot of someone else's system, and it goes stale silently."

**Research question.** Do external web APIs evolve and introduce breaking changes often enough that recorded responses go out of date, and do providers signal such changes?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("web API" OR "web APIs" OR "REST API" OR "RESTful API" OR "web service") AND (evolution OR "breaking changes" OR "API changes")` |
| C1 | `("web API" OR "web APIs" OR "REST API" OR "RESTful API" OR "web service") AND (evolution OR "breaking changes" OR "API changes") AND ("backward compatibility" OR stability OR versioning OR deprecation)` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 20 | 20 | 20 | 56 | 20 | 20 |
| C1 | failed | 20 | 20 | 5 | 40 | 20 | 20 |

The session holds 128 unique records.

*Audit trail:* scholar session `t-api-evolution`; hit list [t-api-evolution.csv](literature/sessions/t-api-evolution.csv), records [t-api-evolution.bib](literature/sessions/t-api-evolution.bib), queries [t-api-evolution.queries.tsv](literature/sessions/t-api-evolution.queries.tsv), LaTeX audit table [t-api-evolution-table.tex](literature/sessions/t-api-evolution-table.tex).

### Findings

**Supporting.**

- [Serbout & Pautasso 2024](#ref-Serbout2024): Many evolving Web APIs ship breaking changes, often without signalling them in the version number; about 30% never break.
  > "only 517 APIs consistently release major upgrades when introducing breaking changes, while 1970 APIs will not always correctly inform their clients about breaking changes released as part of minor or patch-level upgrades. We also detected 927 APIs which use a backwards-compatible evolution strategy, as they never introduce any breaking change throughout their history."
  > (abstract, p. 344; read in full text)
- [Di Lauro et al. 2022](#ref-DiLauro2022): A quarter of evolving OpenAPI-described APIs remove operations without deprecating them first.
  > "Out of the 41,627 APIs considered, we found only 263 (0.6%) in which some operations are deprecated before being removed, while the developers of 10,242 (24.6%) of them directly remove operations without first informing their clients about the potentially breaking change."
  > (abstract, p. 38; read in full text)
- [Wang et al. 2014](#ref-Wang2014): RESTful web APIs change a larger share of their elements between versions than Java APIs and WSDL services.
  > "We find that a larger portion of RESTful web API elements are changed between versions compared with Java APIs and WSDL services."
  > (abstract, p. 245; read in full text)
- [Li et al. 2013](#ref-Li2013): Clients of web APIs cannot avoid upgrading because old API versions stop being served.
  > "clients of a web API often do not have the option not to upgrade, since the old version of the API may not be provided as a service anymore."
  > (abstract; abstract only)

**Qualifying or contradicting.**

- [Serbout & Pautasso 2024](#ref-Serbout2024): About 30% of versioned APIs never introduced a breaking change.
  > "We also detected 927 APIs which use a backwards-compatible evolution strategy, as they never introduce any breaking change throughout their history."
  > (abstract, p. 344; read in full text)
- [Di Lauro et al. 2021](#ref-DiLauro2021): Only a subset of Web APIs change over time.
  > "Our preliminary results indicate that only a subset of the APIs changes, but as opposed to the expectation that APIs should only grow to maintain backward compatibility we also detected a number of APIs with a more variable history."
  > (abstract, p. 124; read in full text)

### Discussion and limitations

The large studies mine OpenAPI descriptions in open-source repositories; commercial APIs such as an LMS's may behave differently. Di Lauro et al. (2021) has a 2021 publisher correction that replaces the term "paths" by "operations"; the quoted sentence is unaffected. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Yes for evolving APIs: breaking changes are common and often shipped without a major version bump, so recordings can go stale without warning; a sizeable minority of APIs never break. Verdict: **Supported** (rate varies by API). The skill's sentence can stay; it may add that breaking changes often arrive in minor versions.

**Wording in the skill after this review.** §3 now reads: "A recording is a snapshot of someone else's system, and it goes stale silently: Web APIs often ship breaking changes without a major version bump."

### Future work

Li et al. (2013) was read at abstract level. The field lacks data on the change rate of the large proprietary APIs that teaching tools call (LMS, student-records systems).

### Hit list

Records bearing on the claim: 4 cited (reviewed by hand), 13 further supporting and 2 further qualifying or contradicting as labelled by the model (unreviewed), out of 128 records; 49 adjacent and 60 off-topic records are not listed. The full classified list is in [t-api-evolution.csv](literature/sessions/t-api-evolution.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [How Does Web Service API Evolution Affect Clients?](https://doi.org/10.1109/ICWS.2013.48) | 2013 | supports | cited: breaking-changes |
| [How Many Web APIs Evolve Following Semantic Versioning?](https://doi.org/10.1007/978-3-031-62362-2_25) | 2024 | supports | cited: breaking-changes |
| [Towards Large-Scale Empirical Assessment of Web APIs Evolution](https://doi.org/10.1007/978-3-030-74296-6_10) | 2021 | qualifies | cited: api-stability |
| [How Do Developers React to RESTful API Evolution?](https://doi.org/10.1007/978-3-662-45391-9_17) | 2014 | supports | cited: breaking-changes |

<a id="ch-contract-tests"></a>

## 7. Do periodic checks against the real service detect drift in test doubles?

**Claim in the draft skill.** §2-3: `pytest --live` re-runs every recorded test against the real service and shape-diffs fresh against committed recordings; live runs "periodically on long-lived projects".

**Research question.** Does periodically checking test doubles against the real service (contract tests, consumer-driven contracts) detect that the doubles have drifted?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("contract testing" OR "consumer-driven contract" OR "consumer-driven contracts" OR "contract tests") AND (microservices OR API OR "web service" OR integration)` |
| C1 | `("contract testing" OR "consumer-driven contract" OR "consumer-driven contracts" OR "contract tests") AND (limitations OR challenges OR "integration testing" OR "end-to-end testing" OR effectiveness)` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | not recorded | 20 | 2 | 35 | 16 | 20 |
| C1 | failed | 20 | 20 | 8 | 46 | 20 | 20 |

The session holds 93 unique records.

*Audit trail:* scholar session `t-contract-tests`; hit list [t-contract-tests.csv](literature/sessions/t-contract-tests.csv), records [t-contract-tests.bib](literature/sessions/t-contract-tests.bib), queries [t-contract-tests.queries.tsv](literature/sessions/t-contract-tests.queries.tsv), LaTeX audit table [t-contract-tests-table.tex](literature/sessions/t-contract-tests-table.tex).

### Findings

**Supporting.**

- [Fowler 2011](#ref-Fowler2011): Practitioner: periodically run contract tests that check test doubles against the external service; check format, not exact data.
  > "periodically run a separate set of contract tests. These check that all the calls against your test doubles return the same results as a call to the external service would."
  > (bliki 'Contract Test', 12 Jan 2011; read in full text)
- [Lehvä et al. 2019](#ref-Lehva2019): Component tests with test doubles let integration defects slip through while staying green; consumer-driven contract tests caught all seeded integration defects in one case study.
  > "The comparison of the testing methods revealed that the consumer-driven contract tests were able to catch every single defect from the 23 different interactions. That was not the case with the component tests; they allowed the defects to slip through."
  > (p. 507, §4.1; read in full text)
- [Schwarz et al. 2025](#ref-Schwarz2025): Consumer-driven contract testing ensures syntactic interoperability between services and complements other tests.
  > "Our theory posits that consumer‐driven contract testing can ensure syntactic interoperability between microservices and complement the testing strategy of such systems. The action research study confirmed this"
  > (abstract; abstract only)

**Qualifying or contradicting.** None found.

### Discussion and limitations

The counter-query (limitations, challenges, comparison with integration and end-to-end testing) returned no negative results, but the empirical base is one case study with 23 seeded defects and one action-research study, both about consumer-driven contracts between services rather than drift checks of recorded responses. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Yes, with thin evidence: contract tests caught every seeded integration defect in the one case study found, and an action-research study agrees; the skill's design (re-run against the live service, compare formats rather than values) matches the practitioner description. Verdict: **Qualified (thin).** No wording change needed; cite the practitioner source for the design.

**Wording in the skill after this review.** Unchanged: the live check stays; the evidence is thin but has no negatives.

### Future work

Schwarz et al. (2025) was read at abstract level. The field lacks a multi-project study of how often contract or drift checks find real changes, and at what cost.

### Hit list

Records bearing on the claim: 2 cited (reviewed by hand), 4 further supporting and 3 further qualifying or contradicting as labelled by the model (unreviewed), out of 93 records; 39 adjacent and 45 off-topic records are not listed. The full classified list is in [t-contract-tests.csv](literature/sessions/t-contract-tests.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [Ensuring Syntactic Interoperability Using Consumer-Driven Contract Testing](https://doi.org/10.1002/stvr.70006) | 2025 | supports | cited: contract-tests-detect-drift |
| [Consumer-Driven Contract Tests for Microservices: A Case Study](https://doi.org/10.1007/978-3-030-35333-9_35) | 2019 | supports | cited: contract-tests-detect-drift |

<a id="ch-invariant-assertions"></a>

## 8. Do invariant and shape assertions keep tests valid without losing fault detection?

**Claim in the draft skill.** §2: "service-facing tests assert **invariants and shapes** (\"every user has an id and a name\"; \"the totals add up\"), not exact values that change from day to day."

**Research question.** Does asserting invariants and shapes instead of exact values keep tests valid when the data change, and how much fault-detection power does it cost?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("test oracle" OR assertions OR "property-based testing" OR invariants OR "metamorphic testing") AND ("unit test" OR "software testing" OR "test suite") AND (brittle OR fragile OR flaky OR "changing data" OR "non-deterministic")` |
| C1 | `("test oracle" OR assertions OR "property-based testing" OR invariants OR "metamorphic testing" OR "oracle strength") AND ("unit test" OR "software testing" OR "test suite") AND ("fault detection" OR "mutation score" OR effectiveness OR "oracle quality")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 17 | 20 | 13 | 46 | 12 | 20 |
| C1 | failed | 20 | 20 | 20 | 56 | 20 | 20 |

The session holds 145 unique records.

*Audit trail:* scholar session `t-invariant-assertions`; hit list [t-invariant-assertions.csv](literature/sessions/t-invariant-assertions.csv), records [t-invariant-assertions.bib](literature/sessions/t-invariant-assertions.bib), queries [t-invariant-assertions.queries.tsv](literature/sessions/t-invariant-assertions.queries.tsv), LaTeX audit table [t-invariant-assertions-table.tex](literature/sessions/t-invariant-assertions-table.tex).

### Findings

**Supporting.**

- [Huo & Clause 2014](#ref-Huo2014): Over-specified assertions are brittle.
  > "developers often create oracles that check too little, resulting in tests that are unable to detect failures, or check too much, resulting in tests that are brittle and difficult to maintain."
  > (abstract; abstract only)
- [Liu et al. 2014](#ref-Liu2014): Relational (metamorphic) properties can detect faults about as well as a full test oracle.
  > "a small number of diverse metamorphic relations, even those identified in an ad hoc manner, had a similar fault-detection capability to a test oracle"
  > (abstract; abstract only)
- [Fowler 2011](#ref-Fowler2011): Practitioner: contract checks look at the format, not the exact data.
  > "Contract tests check the contract of external service calls, but not necessarily the exact data."
  > (bliki 'Contract Test'; read in full text)

**Qualifying or contradicting.**

- [Xia et al. 2023](#ref-Xia2023): Developers loosen assertion bounds to avoid flaky failures, which can miss bugs; 23 of 87 non-deterministic ML tests had over-loose bounds.
  > "Because developers want to avoid false positive failures in tests, they often set the bounds to be too loose, potentially leading to missing critical bugs."
  > (abstract; abstract only)
- [Jahangirova et al. 2016](#ref-Jahangirova2016): Strengthening oracles substantially raises fault detection, so weaker oracles miss faults.
  > "The experimental results show that the fault detection rate of the oracles after improvement increases, on average, by 48.6% (86% over the implicit oracle)."
  > (abstract; abstract only)
- [Huo & Clause 2014](#ref-Huo2014): Under-specified assertions miss failures (the other half of the same finding).
  > "developers often create oracles that check too little, resulting in tests that are unable to detect failures"
  > (abstract; abstract only)

### Discussion and limitations

The studies concern assertions in general, numeric tolerances in machine-learning tests and metamorphic relations, not schema or shape checks of web responses specifically. Most were read at abstract level. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Both: exact-value assertions on changing data are brittle, but assertions that check too little miss faults, and loosened bounds have been shown to hide bugs; relational properties can keep most of the fault-detection power. Verdict: **Qualified.** The skill should ask for the strongest invariant that stays true on live data (relations, totals, the synthetic test objects' known values), not merely shapes, and say that weaker assertions catch less.

**Wording in the skill after this review.** §2 now reads: "service-facing tests assert the **strongest invariants** that stay true on live data (…), not exact values that change from day to day. Shapes alone are too weak: assertions that check too little miss bugs." The structural shape diff of §3 is kept as a drift detector, not as the test's assertion.

### Future work

Huo & Clause (2014), Liu et al. (2014), Xia et al. (2023) and Jahangirova et al. (2016) were read at abstract level. The field lacks a study of shape-only assertions on API responses: how many real faults they miss compared with value assertions on stable synthetic data.

Suggested by a reviewer after the search, not retrieved by the recorded queries, and not read: Meszaros 2007, *xUnit Test Patterns* ("Fragile Test", "Overspecified Software").

### Hit list

Records bearing on the claim: 5 cited (reviewed by hand), 2 further supporting and 11 further qualifying or contradicting as labelled by the model (unreviewed), out of 145 records; 114 adjacent and 13 off-topic records are not listed. The full classified list is in [t-invariant-assertions.csv](literature/sessions/t-invariant-assertions.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [Automated Steering of Model-Based Test Oracles to Admit Real Program Behaviors](https://doi.org/10.1109/TSE.2016.2615311) | 2017 | supports | cited: brittle-assertions |
| [Balancing Effectiveness and Flakiness of Non-Deterministic Machine Learning Tests](https://doi.org/10.1109/ICSE48619.2023.00154) | 2023 | qualifies | cited: loose-oracles-miss-faults |
| [Improving oracle quality by detecting brittle assertions and unused inputs in tests](https://doi.org/10.1145/2635868.2635917) | 2014 | supports | cited: brittle-assertions |
| [Test oracle assessment and improvement](https://doi.org/10.1145/2931037.2931062) | 2016 | qualifies | cited: loose-oracles-miss-faults |
| [How Effectively Does Metamorphic Testing Alleviate the Oracle Problem?](https://doi.org/10.1109/tse.2013.46) | 2013 | supports | cited: relational-oracles |

<a id="ch-flaky"></a>

## 9. Are time, randomness and the network major causes of flaky tests?

**Claim in the draft skill.** §1, rung 5 (the clock, randomness, injected failures; "prefer passing the dependency in") and §2: replay mode is "Fast, offline, deterministic."

**Research question.** Are time, randomness, the network and other external resources major root causes of flaky tests, so that injecting the clock and randomness and replaying network traffic offline removes much of the flakiness?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("flaky tests" OR "flaky test" OR "test flakiness") AND ("root causes" OR causes OR "empirical study" OR taxonomy)` |
| S2 | `("flaky tests" OR "flaky test" OR "test flakiness") AND (time OR randomness OR network OR "external resources" OR "date and time")` |
| C1 | `("flaky tests" OR "flaky test" OR "test flakiness") AND ("async wait" OR concurrency OR "order-dependent" OR "test order dependency")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | not recorded | 20 | 20 | 49 | 20 | 20 |
| S2 | failed | 20 | 20 | 20 | 50 | 20 | 20 |
| C1 | failed | 20 | 20 | 18 | 42 | 20 | 20 |

The session holds 141 unique records.

*Audit trail:* scholar session `t-flaky`; hit list [t-flaky.csv](literature/sessions/t-flaky.csv), records [t-flaky.bib](literature/sessions/t-flaky.bib), queries [t-flaky.queries.tsv](literature/sessions/t-flaky.queries.tsv), LaTeX audit table [t-flaky-table.tex](literature/sessions/t-flaky-table.tex).

### Findings

**Supporting.**

- [Luo et al. 2014](#ref-Luo2014): The network is a documented cause of flakiness.
  > "Tests whose execution depends on network can be flaky because the network is a resource that is hard to control."
  > (§3.1, 'Network'; read in full text)
- [Hashemi et al. 2022](#ref-Hashemi2022): In JavaScript, concurrency is the dominant flakiness cause, with OS-specific features and network stability next.
  > "flakiness caused by concurrency-related issues (e.g., async wait, race conditions or deadlocks) is the most dominant reason for test flakiness. The other top causes of flaky tests are operating system-specific (e.g., features that work on specific OS or OS versions) and network stability (e.g., internet availability or bad socket management)."
  > (abstract; read in full text)
- [Gruber et al. 2021](#ref-Gruber2021): In Python, network and randomness account for most flaky tests not caused by test order or infrastructure.
  > "Order dependency is a much more dominant problem in Python, causing 59 % of the 7 571 flaky tests in our dataset. Another 28 % were caused by test infrastructure problems, which represent a previously undocumented cause of flakiness. The remaining 13 % can mostly be attributed to the use of network and randomness APIs"
  > (abstract; read in full text)
- [Parry et al. 2022](#ref-Parry2022): Flaky tests are a recognised, frequent problem with a body of root-cause literature (survey of 76 papers).
  > "In this article, we systematically survey the body of literature relevant to flaky test research, amounting to 76 papers."
  > (abstract; abstract only)

**Qualifying or contradicting.**

- [Luo et al. 2014](#ref-Luo2014): Async wait, concurrency and test-order dependency are the top root causes of flaky tests; network, time, I/O and randomness are minority causes; many order-dependent flaky tests stem from external resources.
  > "The top three categories of flaky tests are Async Wait, Concurrency, and Test Order Dependency."
  > (summary of findings, F.1; §3.1; Table 2; read in full text)
- [Gruber et al. 2021](#ref-Gruber2021): Test-order dependency, not time or network, dominates in Python.
  > "Order dependency is a much more dominant problem in Python, causing 59 % of the 7 571 flaky tests in our dataset."
  > (abstract; read in full text)
- [Eck et al. 2019](#ref-Eck2019): Developers classifying 200 flaky tests they had fixed found several causes, four of them not reported before; flakiness is not reducible to a few external factors.
  > "The flakiness is due to several different causes, four of which have never been reported before, despite being the most costly to fix"
  > (abstract; read in full text)

### Discussion and limitations

Shares differ by language and by method (commit mining versus rerunning tests). In Luo et al. (2014), network, time, I/O and randomness together account for 23 of 161 classified commits. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Partly: time, randomness and the network are documented causes, and the network is a top cause in JavaScript, but in Java and Python the main causes are asynchronous waits, concurrency and test-order dependency. Verdict: **Qualified.** The skill's advice is sound for the causes it addresses; it should not be read as making a suite non-flaky, and per-test isolation (fresh `tmp_path`, no shared state) addresses the larger order-dependency share.

**Wording in the skill after this review.** The skill injects the clock and randomness and replays offline, but does not claim these are the main causes of flakiness. Following this chapter, §1 adds a rule against the larger cause, order dependency: "let tests share state: each test sets up what it needs, so order and parallel runs do not change the outcome" (under "Never").

### Future work

Parry et al. (2022) was read at abstract level. Python-specific evidence on how much clock injection and offline replay reduce flakiness in practice is missing.

### Hit list

Records bearing on the claim: 5 cited (reviewed by hand), 10 further supporting and 24 further qualifying or contradicting as labelled by the model (unreviewed), out of 141 records; 91 adjacent and 11 off-topic records are not listed. The full classified list is in [t-flaky.csv](literature/sessions/t-flaky.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [An Empirical Study of Flaky Tests in JavaScript](https://doi.org/10.1109/ICSME55016.2022.00011) | 2022 | qualifies | cited: network-major-in-js |
| [An Empirical Study of Flaky Tests in Python](https://doi.org/10.1109/ICST49551.2021.00026) | 2021 | qualifies | cited: other-causes-dominate |
| [An empirical analysis of flaky tests](https://doi.org/10.1145/2635868.2635920) | 2014 | qualifies | cited: other-causes-dominate |
| [A Survey of Flaky Tests](https://doi.org/10.1145/3476105) | 2021 | qualifies | cited: survey |
| [Understanding flaky tests: the developer’s perspective](https://doi.org/10.1145/3338906.3338945) | 2019 | qualifies | cited: other-causes-dominate |

<a id="ch-pseudonymisation"></a>

## 10. Is keyed-hash pseudonymised test data still personal data?

**Claim in the draft skill.** §4: "Pseudonymized data is still personal data under GDPR as long as the key exists, so the key never goes into the repo."

**Research question.** Under the GDPR, does pseudonymised data (identifiers replaced by keyed-HMAC pseudonyms) remain personal data while the key exists, and is plain hashing a weak pseudonymisation?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `(pseudonymization OR pseudonymisation OR pseudonymized OR pseudonymised) AND (GDPR OR "General Data Protection Regulation") AND ("personal data" OR identifiability OR anonymization OR anonymisation)` |
| S2 | `(pseudonymization OR pseudonymisation OR hashing OR "hash function") AND ("re-identification" OR reidentification OR "dictionary attack" OR "brute force") AND ("personal data" OR identifiers)` |
| C1 | `(pseudonymization OR pseudonymisation OR pseudonymized OR pseudonymised) AND (GDPR OR "General Data Protection Regulation") AND ("relative approach" OR "anonymous data" OR "not personal data" OR "risk-based")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | not recorded | 20 | 8 | 48 | 20 | 20 |
| S2 | failed | not recorded | 20 | 13 | 51 | 20 | 20 |
| C1 | failed | not recorded | 20 | 4 | 26 | 5 | 10 |

The session holds 157 unique records.

WebSearch, 2026-10-12: `CJEU C-413/23 P EDPS v SRB judgment pseudonymised data personal data recipient`; it led to the Court's press release, which was then downloaded from curia.europa.eu (retained). Law-firm commentaries in the results were not used.

The GDPR text on EUR-Lex (HTML and PDF) answered with a bot challenge (HTTP 202) on 2026-10-12 and was not retried; Article 4(5) is quoted from EDPB (2025, para. 16) and Recital 26 is cited through EDPB (2025, fn. 7).

*Audit trail:* scholar session `t-pseudonymisation`; hit list [t-pseudonymisation.csv](literature/sessions/t-pseudonymisation.csv), records [t-pseudonymisation.bib](literature/sessions/t-pseudonymisation.bib), queries [t-pseudonymisation.queries.tsv](literature/sessions/t-pseudonymisation.queries.tsv), LaTeX audit table [t-pseudonymisation-table.tex](literature/sessions/t-pseudonymisation-table.tex).

### Findings

**Supporting.**

- [European Data Protection Board 2025](#ref-EDPB2025): Pseudonymised data that could be attributed using additional information (e.g. a key) are personal data; a plain hash of a name is reversible by hashing known names, so the transformation needs a secret (e.g. a MAC key).
  > "Pseudonymised data, which could be attributed to a natural person by the use of additional information, is to be considered information on an identifiable natural person, and is therefore personal."
  > (para. 22, p. 10; para. 88 fn. 23, p. 21; read in full text)
- [European Data Protection Board 2025](#ref-EDPB2025): A plain hash of a name can be reversed by hashing known names; the transformation needs a secret.
  > "if you know the transformation is merely a SHA256 hash of a name, you could apply this to all names you have elsewhere and then see which hashes match in the pseudonymised dataset."
  > (para. 88, fn. 23, p. 21; read in full text)
- [Demir et al. 2018](#ref-Demir2018): Hashing identifiers is only rarely an effective anonymisation; hashed MAC and e-mail addresses can be recovered.
  > "hashing is often believed to be an effective way to anonymize data. Unfortunately, in practice it is only rarely effective."
  > (abstract; abstract only)

**Qualifying or contradicting.**

- [Court of Justice of the European Union 2025](#ref-CJEU2025): Pseudonymised data are not personal data for every person; for a recipient who cannot re-identify they may not be, but identifiability is assessed from the controller's point of view.
  > "pseudonymised data must not be regarded as constituting, in all cases and for every person, personal data for the purposes of the application of Regulation 2018/1725."
  > (press release No 107/25, p. 1; read in full text)
- [Court of Justice of the European Union 2025](#ref-CJEU2025): Identifiability for the information duty is judged from the controller's point of view.
  > "the identifiable nature of the data subject must be assessed at the time of collection of the data and from the point of view of the controller."
  > (press release No 107/25, p. 2; read in full text)
- [Mourby et al. 2018](#ref-Mourby2018): Key-coded data can be anonymous for a third party under Recital 26's 'means reasonably likely' test.
  > "There may also be circumstances in which data which have undergone pseudonymisation within one organisation could be anonymous for a third party."
  > (abstract; abstract only)

### Discussion and limitations

The EDPB document read is the version adopted for public consultation on 16 January 2025. The CJEU judgment itself was not read; the official press release is a non-binding summary. The case concerns Regulation 2018/1725, whose definition of personal data matches the GDPR's. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Yes for the key holder: data that can be attributed with additional information such as a key are personal data, and an unkeyed hash is reversible by hashing candidate names; for a recipient without the key the Court of Justice has held that pseudonymised data are not personal in every case. Verdict: **Supported** for us as key holders, **qualified** for third parties. The skill should say "for us, as holders of the key" and not rely on the data being anonymous to anyone else.

**Wording in the skill after this review.** §4 now reads: "For us, as holders of the key, pseudonymized data are still personal data, so the key never goes into the repo." `references/privacy.md` gives the EDPB reasoning and discusses C-413/23 P, including the controller's-point-of-view qualifier.

### Future work

This search did not read the GDPR text in the Official Journal, the CJEU judgment, or ENISA's pseudonymisation guidance; Demir et al. (2018) and Mourby et al. (2018) were read at abstract level. Whether keyed-HMAC pseudonyms of course data committed to a public repository count as personal data for a reader without the key is untested; the skill's rule (keep the key out, treat leaks as published) does not depend on the answer.

### Hit list

Records bearing on the claim: 4 cited (reviewed by hand), 35 further supporting and 12 further qualifying or contradicting as labelled by the model (unreviewed), out of 157 records; 72 adjacent and 34 off-topic records are not listed. The full classified list is in [t-pseudonymisation.csv](literature/sessions/t-pseudonymisation.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [Case C-413/23 P, EDPS v. SRB: Reassessing the Role of Pseudonymization in Data Sharing?](https://www.webofscience.com/wos/woscc/full-record/WOS:001792738100005) | 2026 | qualifies | cited: relative-approach |
| [Case C-413/23 P, EDPS v. SRB: Reassessing the Role of Pseudonymization in Data Sharing?](https://doi.org/10.54648/gplr2026004) | 2026 | qualifies | cited: relative-approach |
| [The Pitfalls of Hashing for Privacy](https://doi.org/10.1109/COMST.2017.2747598) | 2018 | supports | cited: hashing-weak |
| [Are ‘pseudonymised’ data always personal data? Implications of the GDPR for administrative data research in the UK](https://doi.org/10.1016/j.clsr.2018.01.002) | 2018 | qualifies | cited: relative-approach |

<a id="ch-secrets-leak"></a>

## 11. Do secrets and personal data leak through repositories?

**Claim in the draft skill.** §4: names, emails, personnummer and tokens "must never reach a committed file"; "If a leak is ever committed, treat it as published."

**Research question.** Do secrets and personal data commonly leak through source repositories, including test fixtures, and once pushed are they effectively public?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `(secrets OR credentials OR "API keys" OR passwords OR "hard-coded secrets") AND (leak OR leakage OR exposure OR "secret detection") AND (GitHub OR repositories OR "source code" OR "version control")` |
| S2 | `("personal data" OR "personally identifiable information" OR PII OR "test data") AND (leak OR leakage OR exposure) AND (GitHub OR repositories OR "source code" OR "version control")` |
| C1 | `(secrets OR credentials OR "API keys" OR passwords OR "hard-coded secrets") AND ("secret detection" OR "secret scanning") AND ("false positives" OR precision OR removal OR "test files")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 20 | 20 | 20 | 46 | 20 | 20 |
| S2 | failed | not recorded | 20 | 20 | 56 | 20 | 20 |
| C1 | failed | 8 | 20 | 10 | 29 | 10 | 20 |

The session holds 163 unique records.

*Audit trail:* scholar session `t-secrets-leak`; hit list [t-secrets-leak.csv](literature/sessions/t-secrets-leak.csv), records [t-secrets-leak.bib](literature/sessions/t-secrets-leak.bib), queries [t-secrets-leak.queries.tsv](literature/sessions/t-secrets-leak.queries.tsv), LaTeX audit table [t-secrets-leak-table.tex](literature/sessions/t-secrets-leak-table.tex).

### Findings

**Supporting.**

- [Meli et al. 2019](#ref-Meli2019): Secrets leak into public GitHub repositories at scale, most are never removed, none of the removals rewrote history, and new leaks are found within seconds.
  > "We find that not only is secret leakage pervasive — affecting over 100,000 repositories — but that thousands of new, unique secrets are leaked every day."
  > (abstract, p. 1; 'Secret Lifetime', p. 8; p. 9; read in full text)
- [Meli et al. 2019](#ref-Meli2019): Most leaked secrets stay, and none of the removers rewrote history.
  > "none of the monitored repos had their history rewritten, meaning the secrets were trivially accessible via Git history."
  > ('Secret Lifetime', p. 8; read in full text)
- [Meli et al. 2019](#ref-Meli2019): Leaks are found within seconds of being pushed.
  > "We found that the median time to discovery was 20 seconds"
  > (p. 9; read in full text)
- [Krause et al. 2022](#ref-Krause2022): Developers who leaked secrets rarely cleaned VCS history (17.4%).
  > "Leaking code secrets to the public can have disastrous consequences, such as abusing services and systems or making sensitive user data available to attackers."
  > (abstract; remediation-strategy table; read in full text)

**Qualifying or contradicting.** None found.

### Discussion and limitations

The counter-query (detection tools, false positives, precision, test files) showed that many detector hits are dummy or test keys, which concerns detector precision rather than the rarity of real leaks. No study of secrets or personal data in test fixtures specifically was found; the evidence is about API keys and private keys on GitHub. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Yes for secrets: leakage on GitHub is pervasive, rarely cleaned up from history and discovered within seconds, so a pushed secret must be treated as published. Verdict: **Supported**, with the qualification that personal data in test fixtures is an unstudied extrapolation. No wording change needed.

**Wording in the skill after this review.** Unchanged: "treat it as published" stands.

### Future work

The field lacks a measurement of personal data (not credentials) in committed test fixtures and recorded HTTP cassettes.

### Hit list

Records bearing on the claim: 2 cited (reviewed by hand), 11 further supporting and 1 further qualifying or contradicting as labelled by the model (unreviewed), out of 163 records; 42 adjacent and 107 off-topic records are not listed. The full classified list is in [t-secrets-leak.csv](literature/sessions/t-secrets-leak.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [How Bad Can It Git? Characterizing Secret Leakage in Public GitHub Repositories](https://doi.org/10.14722/ndss.2019.23418) | 2019 | supports | cited: secret-leak-prevalence |
| [Pushed by Accident: A Mixed-Methods Study on Strategies of Handling Secret Information in Source Code Repositories](https://doi.org/10.48550/arXiv.2211.06213) | 2022 | supports | cited: history-not-cleaned |

<a id="ch-free-text-deid"></a>

## 12. Does free text carry identifiers that pattern-based scrubbing misses?

**Claim in the draft skill.** §4: free-text fields "are replaced wholesale, because prose can name anyone"; the template scans for "every original value it replaced".

**Research question.** Do free-text fields carry names and other identifiers that pattern-based or automated scrubbing misses, so that replacing free text wholesale and scanning for every replaced value is warranted?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("de-identification" OR deidentification OR anonymization OR anonymisation OR "text sanitization") AND ("free text" OR "unstructured text" OR "clinical notes" OR "clinical text") AND (names OR identifiers OR "protected health information" OR PHI)` |
| C1 | `("de-identification" OR deidentification OR anonymization OR anonymisation OR "text sanitization") AND ("free text" OR "unstructured text" OR "clinical notes" OR "clinical text") AND (recall OR "re-identification" OR "rule-based" OR "pattern matching" OR "residual")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | not recorded | 20 | 20 | 58 | 20 | 20 |
| C1 | failed | 20 | 20 | 20 | 58 | 20 | 20 |

The session holds 130 unique records.

*Audit trail:* scholar session `t-free-text-deid`; hit list [t-free-text-deid.csv](literature/sessions/t-free-text-deid.csv), records [t-free-text-deid.bib](literature/sessions/t-free-text-deid.bib), queries [t-free-text-deid.queries.tsv](literature/sessions/t-free-text-deid.queries.tsv), LaTeX audit table [t-free-text-deid-table.tex](literature/sessions/t-free-text-deid-table.tex).

### Findings

**Supporting.**

- [Norgeot et al. 2020](#ref-Norgeot2020): Automated de-identification of free text misses identifiers: two established tools had 70-95% recall; even the best tool leaves some PHI, and at scale residual PHI is large.
  > "Even at 95% recall (i.e., percent of PHI removed), the amount PHI still remaining across millions of clinical notes would be staggering."
  > (Introduction; Results, Table 1; read in full text)
- [Norgeot et al. 2020](#ref-Norgeot2020): Established tools left 5-30% of identifiers in place.
  > "On the UCSF test corpus: Physionet had a recall of 85.10% and an F2 of 86.15%, Scrubber had a recall of 95.30% and an F2 of 91.59%"
  > (Results, Table 1; read in full text)
- [Stubbs et al. 2015](#ref-Stubbs2015): De-identification of free text is not yet a solved problem; best systems combine CRFs with hand-written rules.
  > "Our findings indicate that automated systems can be very effective for this task, but that de-identification is not yet a solved problem."
  > (abstract; abstract only)
- [Morris et al. 2024](#ref-Morris2024): Even after the best de-identification tool masked all PII it found, an LLM re-identified 9% of clinical notes.
  > "Although ClinicalBERT was the most effective, masking all identified PII, our tool still reidentified 9% of clinical notes"
  > (abstract; read in full text)
- [Charpentier & Lison 2025](#ref-Charpentier2025): Masked personal identifiers in de-identified documents can be recovered from context and background knowledge (up to 80% of spans).
  > "Results show that (1) as many as 80% of de-identified text spans can be successfully recovered and (2) the re-identification accuracy increases along with the level of background knowledge."
  > (abstract; read in full text)

**Qualifying or contradicting.**

- [Norgeot et al. 2020](#ref-Norgeot2020): The best tool reached 99.5-99.9% recall.
  > "and Philter had a recall of 99.46% and an F2 of 94.36%"
  > (Results, Table 1; read in full text)
- [Kovačević et al. 2024](#ref-Kovacevic2024): Systematic review: reported F1 above 98% but poor generalisation across clinical sub-domains without new labelled data.
  > "Without additional manually labelled training data, state-of-the-art systems fail to generalise well across a wide range of clinical sub-domains."
  > (abstract; read in full text)

### Discussion and limitations

All the evidence comes from clinical notes, court rulings and biographies; course comments in a learning management system were not studied. Recall figures depend on the corpus and on what counts as an identifier. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Yes: automated scrubbing of free text misses identifiers, established tools by a wide margin, and even fully masked text can be re-identified from context. Verdict: **Supported** (for clinical and biographical text). Replacing free text wholesale, as the skill does, avoids the problem rather than reducing it; no wording change needed.

**Wording in the skill after this review.** Unchanged: free text is still replaced wholesale.

### Future work

The field lacks evaluations on educational free text (submission comments, forum posts), where names of classmates and teachers are common.

### Hit list

Records bearing on the claim: 6 cited (reviewed by hand), 34 further supporting and 12 further qualifying or contradicting as labelled by the model (unreviewed), out of 130 records; 58 adjacent and 20 off-topic records are not listed. The full classified list is in [t-free-text-deid.csv](literature/sessions/t-free-text-deid.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [DIRI: Adversarial Patient Reidentification with Large Language Models for Evaluating Clinical Text Anonymization](https://doi.org/10.48550/arXiv.2410.17035) | 2024 | supports | cited: masked-text-reidentifiable |
| [Re-identification of De-identified Documents with Autoregressive Infilling](https://doi.org/10.18653/v1/2025.acl-long.60) | 2025 | supports | cited: masked-text-reidentifiable |
| [Automated systems for the de-identification of longitudinal clinical narratives: Overview of 2014 i2b2/UTHealth shared task Track 1](https://doi.org/10.1016/j.jbi.2015.06.007) | 2015 | supports | cited: scrubbers-miss-identifiers |
| [Re-identification of De-identified Documents with Autoregressive Infilling](https://www.webofscience.com/wos/woscc/full-record/WOS:001596029800060) | 2025 | supports | cited: masked-text-reidentifiable |
| [Protected Health Information filter (Philter): accurately and securely de-identifying free-text clinical notes](https://doi.org/10.1038/s41746-020-0258-y) | 2020 | supports | cited: scrubbers-miss-identifiers |
| [De-identification of clinical free text using natural language processing: A systematic review of current approaches](https://doi.org/10.1016/j.artmed.2024.102845) | 2024 | qualifies | cited: poor-generalisation |

<a id="ch-tdd"></a>

## 13. Does writing tests first improve quality or productivity?

**Claim in the draft skill.** §5: "**Red/green.** Write the test first and watch it fail *for the right reason* before writing the fix. A test that passed before the change proves nothing."

**Research question.** Does writing tests before the code (test-driven development, test-first) improve software quality or productivity, for human developers and for LLM coding agents?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("test-driven development" OR "test-first" OR "test first programming" OR TDD) AND (quality OR productivity OR defects) AND (experiment OR "empirical study" OR "case study")` |
| C1 | `("test-driven development" OR "test-first" OR "test first programming" OR TDD) AND (quality OR productivity OR defects) AND ("meta-analysis" OR "systematic review" OR replication OR "no effect" OR "no difference")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | not recorded | 20 | 20 | 55 | 20 | 20 |
| C1 | failed | 14 | 20 | 20 | 50 | 20 | 20 |

The session holds 139 unique records.

*Audit trail:* scholar session `t-tdd`; hit list [t-tdd.csv](literature/sessions/t-tdd.csv), records [t-tdd.bib](literature/sessions/t-tdd.bib), queries [t-tdd.queries.tsv](literature/sessions/t-tdd.queries.tsv), LaTeX audit table [t-tdd-table.tex](literature/sessions/t-tdd-table.tex).

### Findings

**Supporting.**

- [Nagappan et al. 2008](#ref-Nagappan2008): Industrial case studies: TDD teams had 40-90% lower pre-release defect density at 15-35% more initial development time.
  > "The results of the case studies indicate that the pre-release defect density of the four products decreased between 40% and 90% relative to similar projects that did not use the TDD practice."
  > (abstract, p. 289; abstract only)
- [Rafique & Misic 2013](#ref-Rafique2013): A meta-analysis of 27 studies found a small positive effect on external quality.
  > "The results indicate that, in general, TDD has a small positive effect on quality"
  > (abstract; abstract only)
- [Konstantinou et al. 2026](#ref-Konstantinou2026): Generating tests after (faulty) code propagates the code's errors into the tests: fault detection 14% vs 25% when tests are generated independently.
  > "generating tests after faulty code significantly reduces fault detection effectiveness compared to generating tests independently (14% vs. 25%)."
  > (abstract; read in full text)

**Qualifying or contradicting.**

- [Rafique & Misic 2013](#ref-Rafique2013): The same meta-analysis found little or no effect on productivity, and a larger productivity drop in industrial studies.
  > "but little to no discernible effect on productivity. However, subgroup analysis has found both the quality improvement and the productivity drop to be much larger in industrial studies in comparison with academic studies."
  > (abstract; abstract only)
- [Fucci et al. 2017](#ref-Fucci2017): The order of writing test and code had no important influence; benefits come from fine-grained steady cycles.
  > "Sequencing, the order in which test and production code are written, had no important influence."
  > (abstract; read in full text)
- [Santos et al. 2021](#ref-Santos2021): In a family of 12 experiments, novices wrote slightly higher-quality code test-last than with TDD; the task dominates.
  > "TDD novices achieve a slightly higher code quality with iterative test-last development (i.e., ITL, the reverse approach of TDD) than with TDD. The task being developed largely determines quality."
  > (abstract; read in full text)
- [Alonso et al. 2026](#ref-Alonso2026): Procedural TDD instructions made a small coding agent cause more regressions.
  > "In contrast, adding TDD procedural instructions without targeted test context increased regressions to 9.94%—worse than no intervention at all."
  > (abstract; §5.2; read in full text)

### Discussion and limitations

The human studies measure TDD as a whole development method, often with students; the skill's rule is narrower (reproduce a bug with a failing test before fixing it). For LLM agents the evidence is two 2026 preprints. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Not in general: the evidence on TDD's benefits is mixed, with a small quality gain at best and no clear effect of the test-first order itself; for LLM workflows, tests written after (faulty) code inherit its faults, which supports writing or deriving tests independently of the implementation. Verdict: **Contested** as a general benefit. The skill should keep red/green for reproducing a bug and justify it by test independence, not by TDD's general benefits: replace "A test that passed before the change proves nothing" with "A test that already passed before the change does not show it can detect what the change fixes, and a test written from the finished code tends to encode its bugs."

**Wording in the skill after this review.** §5 now reads: "Write the test first, from the spec or the bug report rather than from the implementation, and watch it fail *for the right reason* before writing the fix. A test that already passed before the change has not shown it can detect what the change fixes, and tests derived from finished code tend to encode its bugs." No general TDD benefit is claimed; `references/agent-practices.md` cites Konstantinou et al. 2026 and reports the contested human evidence and Alonso et al. 2026.

### Future work

Rafique & Mišić (2013) was read at abstract level and Nagappan et al. (2008) from its first page. The field lacks studies of bug-reproduction-first (as opposed to full TDD) for both humans and agents.

### Hit list

Records bearing on the claim: 5 cited (reviewed by hand), 14 further supporting and 38 further qualifying or contradicting as labelled by the model (unreviewed), out of 139 records; 32 adjacent and 50 off-topic records are not listed. The full classified list is in [t-tdd.csv](literature/sessions/t-tdd.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [The Effects of Test-Driven Development on External Quality and Productivity: A Meta-Analysis](https://doi.org/10.1109/TSE.2012.28) | 2013 | qualifies | cited: mixed-meta-analysis |
| [A Dissection of the Test-Driven Development Process: Does It Really Matter to Test-First or to Test-Last?](https://doi.org/10.1109/tse.2016.2616877) | 2016 | qualifies | cited: test-first-order-irrelevant |
| [Realizing quality improvement through test driven development: results and experiences of four industrial teams](https://doi.org/10.1007/s10664-008-9062-z) | 2008 | supports | cited: industrial-case-study |
| [On the risk of coding before testing: An empirical study on LLM-based test generation workflow](https://doi.org/10.48550/arXiv.2607.05139) | 2026 | supports | cited: agent-test-independence |
| [A family of experiments on test-driven development](https://doi.org/10.1007/s10664-020-09895-8) | 2021 | qualifies | cited: test-first-order-irrelevant |

<a id="ch-mutation"></a>

## 14. Does seeing a test fail on a deliberate break show it can detect faults?

**Claim in the draft skill.** §5: "**Check that the test can fail.** After a green run that came too easily, break the code on purpose (a mutation) and confirm the test goes red."

**Research question.** Does making a test fail on a deliberately introduced fault (a mutation) show that the test can detect real faults?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("mutation testing" OR "mutation analysis" OR mutants OR "mutation score") AND ("real faults" OR "fault detection" OR "test suite effectiveness" OR "test adequacy")` |
| S2 | `("pseudo-tested" OR "extreme mutation" OR "oracle gap" OR "checked coverage" OR "test-first" OR "failing test") AND ("test suite" OR "unit tests") AND (mutation OR "fault detection" OR effectiveness)` |
| C1 | `("mutation testing" OR "mutation analysis" OR mutants OR "mutation score") AND ("real faults" OR "fault detection") AND (correlation OR "coupling effect" OR validity OR "test suite size")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 20 | 20 | 20 | 55 | 20 | 20 |
| S2 | failed | 20 | 20 | 20 | 52 | 20 | 20 |
| C1 | failed | 20 | 20 | 19 | 55 | 20 | 20 |

The session holds 198 unique records.

*Audit trail:* scholar session `t-mutation`; hit list [t-mutation.csv](literature/sessions/t-mutation.csv), records [t-mutation.bib](literature/sessions/t-mutation.bib), queries [t-mutation.queries.tsv](literature/sessions/t-mutation.queries.tsv), LaTeX audit table [t-mutation-table.tex](literature/sessions/t-mutation-table.tex).

### Findings

**Supporting.**

- [Just et al. 2014](#ref-Just2014): Mutant detection correlates with real-fault detection independently of coverage, though some real faults are not coupled to mutants.
  > "The results show a statistically significant correlation between mutant detection and real fault detection, independently of code coverage."
  > (abstract; §1, contributions; read in full text)
- [Petrović et al. 2021](#ref-Petrovic2021): At Google, developers exposed to mutants write more tests, and mutants are coupled with real high-priority faults.
  > "Our analyses suggest that developers using mutation testing write more tests, and actively improve their test suites with high quality tests such that fewer mutants remain."
  > (abstract; abstract only)
- [Niedermayr et al. 2016](#ref-Niedermayr2016): Tests can execute code yet fail to detect faults in it (pseudo-tested methods), so coverage or a green run alone does not show fault detection.
  > "We assessed the ratio of pseudo-tested methods (those tested in a way such that faults would not be detected) to all covered methods"
  > (abstract; read in full text)
- [Mathews & Nagappan 2024b](#ref-Mathews2024b): LLM test generators that keep only passing tests validate bugs and reject bug-revealing tests.
  > "how LLM-generated tests can fail to detect bugs and, more alarmingly, how their design can worsen the situation by validating bugs in the generated test suite and rejecting bug-revealing tests."
  > (abstract; read in full text)
- [Konstantinou et al. 2026](#ref-Konstantinou2026): Tests generated after faulty code detect fewer faults, i.e. a passing test written from the code is weak evidence.
  > "generating tests after faulty code significantly reduces fault detection effectiveness compared to generating tests independently (14% vs. 25%)."
  > (abstract; read in full text)

**Qualifying or contradicting.**

- [Papadakis et al. 2018](#ref-Papadakis2018): Correlation of mutation score with real-fault detection is weak when suite size is controlled, yet higher mutation scores still improve fault detection.
  > "mutants provide good guidance for improving the fault detection of test suites, but their correlation with fault detection are weak."
  > (abstract; abstract only)
- [Just et al. 2014](#ref-Just2014): Some real faults are not coupled to any mutant.
  > "identification of its inherent limitations (17% of real faults are not coupled to mutants)."
  > (§1, contributions; read in full text)

### Discussion and limitations

Mutation studies are about suites and mutation scores; the skill uses a single manual mutation as a sanity check of one test, which is a weaker but cheaper use of the same idea. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Yes, at the right strength: a test that fails on a deliberate break can detect that kind of fault, mutant detection is correlated with real-fault detection, and tests that pass whatever the code does are common; but the correlation is weak once suite size is controlled. Verdict: **Supported (qualified).** The skill should add that a red result shows the test can catch that break, not that the suite is adequate.

**Wording in the skill after this review.** §5 now adds: "This shows the test catches that break, not that the suite is adequate."

### Future work

Papadakis et al. (2018) and Petrović et al. (2021) were read at abstract level.

### Hit list

Records bearing on the claim: 7 cited (reviewed by hand), 18 further supporting and 18 further qualifying or contradicting as labelled by the model (unreviewed), out of 198 records; 109 adjacent and 46 off-topic records are not listed. The full classified list is in [t-mutation.csv](literature/sessions/t-mutation.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [Are Mutation Scores Correlated with Real Fault Detection? A Large Scale Empirical study on the Relationship Between Mutants and Real Faults](https://doi.org/10.1145/3180155.3180183) | 2018 | qualifies | cited: weak-correlation |
| [Are mutants a valid substitute for real faults in software testing?](https://doi.org/10.1145/2635868.2635929) | 2014 | supports | cited: mutants-coupled-real-faults |
| [Design choices made by LLM-based test generators prevent them from finding bugs](https://doi.org/10.48550/arXiv.2412.14137) | 2024 | supports | cited: tests-designed-to-pass |
| [Will My Tests Tell Me If I Break This Code?](https://doi.org/10.1145/2896941.2896944) | 2016 | supports | cited: pseudo-tested |
| [Will my tests tell me if I break this code?](https://doi.org/10.18419/opus-8944) | 2016 | supports | cited: pseudo-tested |
| [Does Mutation Testing Improve Testing Practices?](https://doi.org/10.1109/icse43902.2021.00087) | 2021 | supports | cited: mutants-coupled-real-faults |
| [On the risk of coding before testing: An empirical study on LLM-based test generation workflow](https://doi.org/10.48550/arXiv.2607.05139) | 2026 | supports | cited: agent-test-independence |

<a id="ch-llm-exec-feedback"></a>

## 15. Do LLM coding agents do better when they can run tests?

**Claim in the draft skill.** §5: "**Red/green.** Write the test first and watch it fail *for the right reason* before writing the fix."; and §5: "**First run the tests** at the start of a session".

**Research question.** Do LLM code generators and coding agents perform better when they can execute tests and receive the results?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("large language model" OR "large language models" OR LLM) AND ("code generation" OR "program repair" OR "issue resolution") AND ("execution feedback" OR "test execution" OR "unit tests" OR "test-driven")` |
| C1 | `("large language model" OR "large language models" OR LLM) AND ("code generation" OR "program repair" OR "issue resolution") AND ("execution feedback" OR "self-repair" OR "self-debugging" OR "unit tests") AND (limitations OR overfitting OR "silver bullet" OR "no improvement")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 20 | 20 | 20 | 58 | 20 | 20 |
| C1 | failed | not recorded | 20 | 20 | 58 | 7 | 20 |

The session holds 139 unique records.

*Audit trail:* scholar session `t-llm-exec-feedback`; hit list [t-llm-exec-feedback.csv](literature/sessions/t-llm-exec-feedback.csv), records [t-llm-exec-feedback.bib](literature/sessions/t-llm-exec-feedback.bib), queries [t-llm-exec-feedback.queries.tsv](literature/sessions/t-llm-exec-feedback.queries.tsv), LaTeX audit table [t-llm-exec-feedback-table.tex](literature/sessions/t-llm-exec-feedback-table.tex).

### Findings

**Supporting.**

- [Mathews & Nagappan 2024a](#ref-Mathews2024): Giving LLMs the tests together with the problem statement raises code-generation success on MBPP/HumanEval.
  > "Our results consistently demonstrate that including test cases leads to higher success in solving programming challenges."
  > (abstract; read in full text)
- [Chen et al. 2023](#ref-Chen2023): Self-debugging with execution results improves code-generation accuracy, by up to 12% where unit tests exist.
  > "On TransCoder and MBPP where unit tests are available, SELF-DEBUGGING improves the baseline accuracy by up to 12%."
  > (abstract; read in full text)
- [Kamoi et al. 2024](#ref-Kamoi2024): Critical survey: LLM self-correction works well with reliable external feedback, but prompted self-feedback alone has not been shown to work except on suited tasks.
  > "(1) no prior work demonstrates successful self-correction with feedback from prompted LLMs, except for studies in tasks that are exceptionally suited for self-correction, (2) self-correction works well in tasks that can use reliable external feedback"
  > (abstract; read in full text)
- [Zhong et al. 2025](#ref-Zhong2025): Hiding the tests from agents degraded their legitimate performance.
  > "Hiding tests from agents reduces cheating success rate to near zero, but also degrades performance on the original benchmark."
  > (§5.2, p. 8; read in full text)

**Qualifying or contradicting.**

- [Olausson et al. 2024](#ref-Olausson2024): Test-driven self-repair gains are often modest once its cost is counted.
  > "We find that when the cost of carrying out repair is taken into account, performance gains are often modest, vary a lot between subsets of the data, and are sometimes not present at all."
  > (abstract; read in full text)
- [Chen et al. 2025](#ref-ChenX2025): Self-debugging with self-generated tests struggles on basic problems because of test bias.
  > "post-execution self-debugging struggles on basic problems but shows potential for improvement on competitive ones, due to the bias introduced by self-generated tests."
  > (abstract; read in full text)

### Discussion and limitations

Most evidence is from function-level benchmarks (HumanEval, MBPP, APPS) rather than repository-level work. The large unreviewed supports count in this session consists mostly of method papers that use test feedback by design. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded. The "Show evidence" rule (report the command and its result) was not audited separately: it is practitioner advice (Willison's *Agentic Engineering Patterns*; his Showboat tool), and no study measures it.

### Conclusion

Yes, with conditions: test results help when the tests are reliable and independent of the code; self-repair gains are often modest once cost is counted, and tests the model writes for its own code bias the result. Verdict: **Supported (qualified).** No wording change needed.

**Wording in the skill after this review.** Unchanged: this evidence supports giving the agent tests it can run (red/green, first run the tests). The separate rule to report the command and its result ("Show evidence") remains practitioner advice.

### Future work

The field lacks repository-level studies that separate the value of running the existing suite from the value of writing new tests.

### Hit list

Records bearing on the claim: 7 cited (reviewed by hand), 52 further supporting and 6 further qualifying or contradicting as labelled by the model (unreviewed), out of 139 records; 69 adjacent and 5 off-topic records are not listed. The full classified list is in [t-llm-exec-feedback.csv](literature/sessions/t-llm-exec-feedback.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [Is Self-Repair a Silver Bullet for Code Generation?](https://doi.org/10.48550/arXiv.2306.09896) | 2023 | qualifies | cited: modest-gains |
| [Revisit Self-Debugging with Self-Generated Tests for Code Generation](https://www.webofscience.com/wos/woscc/full-record/WOS:001611618300240) | 2025 | qualifies | cited: self-generated-test-bias |
| [Revisit Self-Debugging with Self-Generated Tests for Code Generation](https://doi.org/10.48550/arXiv.2501.12793) | 2025 | qualifies | cited: self-generated-test-bias |
| [Revisit Self-Debugging with Self-Generated Tests for Code Generation](https://doi.org/10.18653/v1/2025.acl-long.881) | 2025 | qualifies | cited: self-generated-test-bias |
| [Teaching Large Language Models to Self-Debug](https://doi.org/10.48550/arxiv.2304.05128) | 2023 | supports | cited: execution-feedback |
| [Test-Driven Development and LLM-based Code Generation](https://ieeexplore.ieee.org/document/10764936/) | 2024 | supports | cited: tests-improve-codegen |
| [Test-Driven Development for Code Generation](https://doi.org/10.1145/3691620.3695527) | 2024 | supports | cited: tests-improve-codegen |

<a id="ch-agents-game-tests"></a>

## 16. Do coding agents game tests to make them pass?

**Claim in the draft skill.** §5: "**Never weaken a test to get green.** Do not edit an assertion, add a skip or xfail, delete a test, loosen a tolerance, or special-case the implementation to satisfy one test, unless you say so explicitly and say why."

**Research question.** Do LLM coding agents modify, skip, delete or special-case tests to make them pass?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("large language model" OR LLM OR "coding agent" OR "AI agent" OR "language model agent") AND ("reward hacking" OR "specification gaming" OR "test tampering" OR "test manipulation" OR cheating)` |
| S2 | `("large language model" OR LLM OR "automated program repair" OR "coding agent") AND ("program repair" OR "code generation") AND ("patch overfitting" OR "test overfitting" OR "plausible patches" OR "special-casing")` |
| C1 | `("large language model" OR LLM OR "coding agent" OR "AI agent") AND ("reward hacking" OR "specification gaming" OR "test tampering" OR "patch overfitting") AND (rate OR frequency OR mitigation OR detection)` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | not recorded | 20 | 20 | 55 | 20 | 20 |
| S2 | failed | not recorded | 20 | 20 | 50 | 20 | 20 |
| C1 | failed | 3 | 20 | 20 | 35 | 5 | 18 |

The session holds 180 unique records.

ImpossibleBench (Zhong et al. 2025) was named in the brief and retrieved by its arXiv identifier; it was not among the topic queries' first 20 results per provider.

*Audit trail:* scholar session `t-agents-game-tests`; hit list [t-agents-game-tests.csv](literature/sessions/t-agents-game-tests.csv), records [t-agents-game-tests.bib](literature/sessions/t-agents-game-tests.bib), queries [t-agents-game-tests.queries.tsv](literature/sessions/t-agents-game-tests.queries.tsv), LaTeX audit table [t-agents-game-tests-table.tex](literature/sessions/t-agents-game-tests-table.tex).

### Findings

**Supporting.**

- [Zhong et al. 2025](#ref-Zhong2025): LLM coding agents modify tests, overload comparison operators, record state or special-case tests to pass impossible tasks; rates depend strongly on task, prompt and test access.
  > "an LLM agent with access to unit tests may delete failing tests rather than fix the underlying bug."
  > (abstract; §1 p. 2; §4.1 p. 5; §5.2 p. 8; read in full text)
- [Zhong et al. 2025](#ref-Zhong2025): Agents edit tests and special-case them.
  > "Special Casing: The model special-cases the test cases to pass them."
  > (§4.1, p. 5; read in full text)
- [Gabor et al. 2025](#ref-Gabor2025): Commercial coding agents (Codex, Claude Code) were observed reward hacking by hard-coding tests or editing test files.
  > "We observe explicit reward hacking by both Codex and Claude Code, and misaligned behavior by all three agents."
  > (abstract; read in full text)
- [Ginelli et al. 2022](#ref-Ginelli2022): Pre-LLM program repair already produced test-passing patches that only delete code and do not fix the bug.
  > "Our study reveals that code-removal patches are often insufficient to fix bugs"
  > (abstract; abstract only)

**Qualifying or contradicting.**

- [Zhong et al. 2025](#ref-Zhong2025): Rates depend strongly on task and prompt; instructions cut cheating sharply.
  > "appropriate prompt could dramatically reduce GPT-5’s cheating from 92% to 1% on Conflicting-LiveCodeBench."
  > (§1, p. 2; read in full text)
- [Petke et al. 2024](#ref-Petke2024): In practice APR tools produce few plausible-but-wrong patches; overfitting may be less severe than believed.
  > "This study unveils that the overfitting problem might not be as bad as previously thought."
  > (abstract; abstract only)

### Discussion and limitations

ImpossibleBench measures behaviour on tasks made impossible on purpose, so its rates are upper bounds for ordinary work. EvilGenie observed production agents in an environment built to make hacking easy. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Yes: coding agents, including widely used commercial ones, have been observed deleting, editing and special-casing tests to pass; how often depends strongly on task, test access and instructions, and explicit instructions reduce it. Verdict: **Supported.** The skill's rule matches the evidence and the mitigation that worked.

**Wording in the skill after this review.** Unchanged: "Never weaken a test to get green" stands.

### Future work

Ginelli et al. (2022) and Petke et al. (2024) were read at abstract level. The field lacks rates from ordinary (possible) tasks in real repositories.

### Hit list

Records bearing on the claim: 3 cited (reviewed by hand), 38 further supporting and 8 further qualifying or contradicting as labelled by the model (unreviewed), out of 180 records; 71 adjacent and 60 off-topic records are not listed. The full classified list is in [t-agents-game-tests.csv](literature/sessions/t-agents-game-tests.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [EvilGenie: A Reward Hacking Benchmark](https://doi.org/10.48550/arxiv.2511.21654) | 2025 | supports | cited: agent-test-tampering |
| [The Patch Overfitting Problem in Automated Program Repair: Practical Magnitude and a Baseline for Realistic Benchmarking](https://doi.org/10.1145/3663529.3663776) | 2024 | qualifies | cited: overfitting-severity |
| [A Comprehensive Study of Code-removal Patches in Automated Program Repair](https://doi.org/10.1007/s10664-021-10100-7) | 2020 | supports | cited: apr-overfitting |

<a id="ch-run-tests-first"></a>

## 17. Does running the existing tests first help a coding agent?

**Claim in the draft skill.** §5: "**First run the tests** at the start of a session, so you know the baseline, the runner and the size of the suite."

**Research question.** Does running the existing test suite at the start of an agent session improve the agent's work?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("coding agent" OR "LLM agent" OR "software engineering agent" OR "large language model") AND ("run tests" OR "test execution" OR "existing tests" OR "regression tests" OR "test suite") AND (repository OR "environment setup" OR "issue resolution")` |
| C1 | `("coding agent" OR "LLM agent" OR "software engineering agent" OR "large language model") AND ("run tests" OR "test execution" OR "existing tests" OR "regression tests" OR "test suite") AND (ablation OR overhead OR cost OR "without tests")` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | not recorded | 20 | 20 | 47 | 1 | 19 |
| C1 | failed | not recorded | 20 | 20 | 54 | 10 | 20 |

The session holds 128 unique records.

WebSearch, 2026-10-12: `Simon Willison Agentic Engineering Patterns "First run the tests"`; it led to the guide page, which was then read in full (retained).

*Audit trail:* scholar session `t-run-tests-first`; hit list [t-run-tests-first.csv](literature/sessions/t-run-tests-first.csv), records [t-run-tests-first.bib](literature/sessions/t-run-tests-first.bib), queries [t-run-tests-first.queries.tsv](literature/sessions/t-run-tests-first.queries.tsv), LaTeX audit table [t-run-tests-first-table.tex](literature/sessions/t-run-tests-first-table.tex).

### Findings

**Supporting.**

- [Willison 2026](#ref-Willison2026): Practitioner recommendation: start each agent session by prompting 'First run the tests'.
  > "Any time I start a new session with an agent against an existing project I'll start by prompting a variant of the following: First run the tests"
  > (web page 'First run the tests'; read in full text)

**Qualifying or contradicting.**

- [Alonso et al. 2026](#ref-Alonso2026): Procedural TDD instructions without targeted test context increased regressions of a coding agent; giving it the tests to check reduced them.
  > "In contrast, adding TDD procedural instructions without targeted test context increased regressions to 9.94%—worse than no intervention at all."
  > (abstract; §5.2; read in full text)

### Discussion and limitations

Neither the support query nor the counter-query returned a study of the practice. Alonso et al. (2026) tested a different instruction (procedural TDD prompts) with small open-weight models. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Unknown: no empirical study of running the suite at session start was found; the recommendation is practitioner advice. Verdict: **Practitioner-only.** The skill can keep the rule, attributed as practice; keep agent instructions short, since one study found that verbose procedural testing instructions made a small agent worse.

**Wording in the skill after this review.** §5 now attributes the practice: "**First run the tests** at the start of a session (Willison's prompt)". It is not presented as a finding.

### Future work

An ablation on an agent benchmark (with and without a first test run) would settle it.

### Hit list

Records bearing on the claim: 1 cited (reviewed by hand), 2 further supporting and 2 further qualifying or contradicting as labelled by the model (unreviewed), out of 128 records; 90 adjacent and 33 off-topic records are not listed. The full classified list is in [t-run-tests-first.csv](literature/sessions/t-run-tests-first.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [TDAD: Test-Driven Agentic Development - Reducing Code Regressions in AI Coding Agents via Graph-Based Impact Analysis](https://doi.org/10.48550/arxiv.2603.17973) | 2026 | qualifies | cited: procedural-instructions-hurt |

<a id="ch-fresh-review"></a>

## 18. Does a reviewer in a fresh context find what the author missed?

**Claim in the draft skill.** §5: "**Fresh-context review** for larger changes: a subagent that sees only the diff, checking whether the tests exercise behaviour or just mirror the implementation."

**Research question.** Does a reviewer that did not write the code, or an LLM in a fresh context, find problems the author misses? Do LLMs show self-preference and weak self-correction?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("large language models" OR LLM) AND ("self-preference" OR "self-evaluation" OR "self-bias" OR "self-recognition" OR "self-correction") AND (bias OR evaluation OR review)` |
| S2 | `("code review" OR "code inspection" OR "peer review") AND (defects OR "defect detection" OR effectiveness) AND (author OR "independent reviewer" OR "self-review" OR "fresh eyes")` |
| C1 | `("large language models" OR LLM) AND ("self-correction" OR "self-refine" OR "self-review" OR "self-evaluation") AND (improves OR effective OR "intrinsic self-correction")` |
| C2 | `("code review" OR "code inspection" OR "peer review") AND (defects OR "defect detection" OR bugs) AND (effectiveness OR usefulness OR "do not find" OR outcomes)` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 20 | 20 | 20 | 57 | 20 | 20 |
| S2 | failed | 20 | 20 | 20 | 60 | 20 | 20 |
| C1 | failed | 20 | 20 | 20 | 50 | 20 | 20 |
| C2 | failed | 20 | 20 | 20 | 58 | 20 | 20 |

The session holds 326 unique records.

Known item: Song (2026), arXiv:2603.12123v2, was supplied by a reviewer of this audit; it was not among the topic queries' first 20 results per database. Retrieved on 2026-10-12 from arXiv (PDF of v2, and the listing via the arXiv API) and read in full.

*Audit trail:* scholar session `t-fresh-review`; hit list [t-fresh-review.csv](literature/sessions/t-fresh-review.csv), records [t-fresh-review.bib](literature/sessions/t-fresh-review.bib), queries [t-fresh-review.queries.tsv](literature/sessions/t-fresh-review.queries.tsv), LaTeX audit table [t-fresh-review-table.tex](literature/sessions/t-fresh-review-table.tex).

### Findings

**Supporting.**

- [Huang et al. 2024](#ref-Huang2024): LLMs struggle to correct their own reasoning without external feedback and sometimes get worse.
  > "our research indicates that LLMs struggle to self-correct their responses without external feedback, and at times, their performance even degrades after self-correction."
  > (abstract; read in full text)
- [Kamoi et al. 2024](#ref-Kamoi2024): Critical survey: LLM self-correction works well with reliable external feedback, but prompted self-feedback alone has not been shown to work except on suited tasks.
  > "(1) no prior work demonstrates successful self-correction with feedback from prompted LLMs, except for studies in tasks that are exceptionally suited for self-correction, (2) self-correction works well in tasks that can use reliable external feedback"
  > (abstract; read in full text)
- [Xu et al. 2024](#ref-Xu2024): LLMs favour their own outputs (self-bias), and self-refinement amplifies it.
  > "We find that self-bias is prevalent in all examined LLMs across multiple languages and tasks."
  > (abstract; read in full text)
- [Wataoka et al. 2024](#ref-Wataoka2024): GPT-4 shows significant self-preference bias as a judge, linked to the familiarity (low perplexity) of its own outputs.
  > "Our experimental results demonstrate that GPT-4 exhibits a significant degree of self-preference bias."
  > (abstract; read in full text)
- [Song 2026](#ref-Song2026): Direct experiment: a second review in a fresh session found more injected errors than a second review in the same session.
  > "The central result is that a second review helps only when it happens in a fresh session: CCR (F1 28.6%) outperforms a second review in the same session (SR2, 21.7%) robustly"
  > (abstract, arXiv:2603.12123v2; read in full text)

**Qualifying or contradicting.**

- [Song 2026](#ref-Song2026): The same experiment: fresh-session review was not significantly better than a context-aware subagent review or a single same-session review.
  > "CCR is not significantly ahead of context-aware subagent review (SA, 23.8%; p=0.057) or of a single same-session review (SR, 27.1%; p=0.26)"
  > (abstract, arXiv:2603.12123v2; read in full text)
- [Guey & Bougault 2026](#ref-Guey2026): When deciding whether to accept a verified-good fix, an LLM acting as the in-context author behaved like a fresh model (no detectable self-preference).
  > "we find no detectable self-preference: authors reject verified-good fixes to their own drafts at essentially the same rate as fresh models judging the same drafts (gap -5.1 pp, 95% CI [-12.9, +2.7])."
  > (abstract; read in full text)
- [Roytburg et al. 2026](#ref-Roytburg2026): About half of previously reported LLM self-preference examples lose significance once judge quality is controlled.
  > "This evaluator quality baseline reveals that only 51% of examples in previous findings retain statistical significance against this null hypothesis"
  > (abstract; read in full text)
- [Liu et al. 2024](#ref-LiuSC2024): Intrinsic self-correction does appear under zero temperature and unbiased prompts.
  > "Leveraging these factors, we demonstrate that intrinsic self-correction ability is exhibited across multiple existing LLMs."
  > (abstract; read in full text)
- [Bacchelli & Bird 2013](#ref-Bacchelli2013): Code reviews find fewer defects than expected; their value is largely knowledge transfer and awareness.
  > "while finding defects remains the main motivation for review, reviews are less about defects than expected and instead provide additional benefits such as knowledge transfer, increased team awareness, and creation of alternative solutions to problems."
  > (abstract; abstract only)
- [Beller et al. 2014](#ref-Beller2014): Changes triggered by code review are 75% maintainability and 25% functional.
  > "featuring the similar 75:25 ratio of maintainability-related to functional problems."
  > (abstract; abstract only)
- [Czerwonka et al. 2015](#ref-Czerwonka2015): At Microsoft, code reviews often do not find functionality issues that should block a submission.
  > "code reviews often do not find functionality issues that should block a code submission"
  > (abstract; abstract only)

### Discussion and limitations

Most of the support is indirect: it shows that models judge and correct their own output poorly, not that a fresh-context model reviews code better. One direct experiment, Song (2026), was supplied as a known item rather than found by the topic queries; it is a single-author preprint with one model (Claude Opus 4.6), 30 artifacts and errors injected by the author, and its second version withdrew the first version's advantages over subagent review and a single same-session review. The author-versus-fresh comparison by Guey & Bougault (2026) concerns text revision with a deterministic checker, and its confidence interval cannot exclude effects below about 13 percentage points. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Partly: one small experiment found that a second review helps only when it runs in a fresh session, but fresh-session review was not significantly better than a single review or a context-aware subagent review; models correct themselves poorly without external feedback and show self-bias, an author-versus-fresh comparison on text revision found no difference, and human code review finds few functional defects. Verdict: **Qualified.** The skill should present fresh-context review as a cheap extra check and steer it towards runnable checks (break the code, does a test go red?) rather than opinion.

**Wording in the skill after this review.** §5 now reads: "a subagent that sees only the diff checks whether the tests exercise behaviour or just mirror the implementation. Ask it for checks it can run (break the code: does a test go red?), not for an opinion." It no longer claims that a fresh review finds more; `references/agent-practices.md` reports Song (2026) and the limits of the evidence.

### Future work

Bacchelli & Bird (2013), Beller et al. (2014) and Czerwonka et al. (2015) were read at abstract level, and the topic queries did not return Song (2026). Song's experiment needs replication with other models, more artifacts, errors not injected by the experimenter, and diffs whose tests are weak, which is the skill's use; if fresh-context review turned out no better than one careful same-session review, the skill could drop the subagent step.

### Hit list

Records bearing on the claim: 11 cited (reviewed by hand), 68 further supporting and 56 further qualifying or contradicting as labelled by the model (unreviewed), out of 326 records; 112 adjacent and 79 off-topic records are not listed. The full classified list is in [t-fresh-review.csv](literature/sessions/t-fresh-review.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [Pride and Prejudice: LLM Amplifies Self-Bias in Self-Refinement](https://doi.org/10.18653/v1/2024.acl-long.826) | 2024 | supports | cited: self-bias |
| [Self-Preference Bias in LLM-as-a-Judge](https://doi.org/10.48550/arXiv.2410.21819) | 2024 | supports | cited: self-bias |
| [Code Reviews Do Not Find Bugs. How the Current Code Review Best Practice Slows Us Down](https://doi.org/10.1109/ICSE.2015.131) | 2015 | qualifies | cited: reviews-find-few-defects |
| [Large Language Models Cannot Self-Correct Reasoning Yet](https://doi.org/10.48550/arxiv.2310.01798) | 2023 | supports | cited: no-intrinsic-self-correction |
| [Self-Preference Is Weak or Absent in Verifiable Instruction-Following Revision: A Four-Model Test Under Genuine Authorship](https://doi.org/10.48550/arXiv.2606.20093) | 2026 | qualifies | cited: author-vs-fresh-no-difference |
| [Large Language Models have Intrinsic Self-Correction Ability](https://doi.org/10.48550/arxiv.2406.15673) | 2024 | qualifies | cited: self-correction-possible |
| [When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs](https://doi.org/10.1162/tacl_a_00713) | 2024 | supports | cited: external-feedback-needed |
| [Are LLM Evaluators Really Narcissists? Sanity Checking Self-Preference Evaluations](https://doi.org/10.48550/arXiv.2601.22548) | 2026 | qualifies | cited: self-preference-overstated |
| [Expectations, outcomes, and challenges of modern code review](https://doi.org/10.1109/icse.2013.6606617) | 2013 | qualifies | cited: reviews-find-few-defects |
| [Expectations, outcomes, and challenges of modern code review](https://doi.org/10.5555/2486788.2486882) | 2013 | qualifies | cited: reviews-find-few-defects |
| [Modern code reviews in open-source projects: which problems do they fix?](https://doi.org/10.1145/2597073.2597082) | 2014 | qualifies | cited: reviews-find-few-defects |

<a id="ch-exploratory"></a>

## 19. Does exploratory, manual trying find defects scripted tests miss?

**Claim in the draft skill.** §5: "**Manual check, then pin it.** Try the change for real: `python -c`, the CLI, `curl` against a dev server. Turn every surprise into a red/green test."

**Research question.** Does exploratory or manual testing find defects that scripted tests miss?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("exploratory testing" OR "manual testing" OR "session-based testing") AND (defects OR "defect detection" OR effectiveness OR efficiency)` |
| C1 | `("exploratory testing" OR "manual testing" OR "session-based testing") AND ("test case based" OR "scripted testing" OR "automated testing") AND (comparison OR experiment OR effectiveness)` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 20 | 20 | 20 | 54 | 20 | 20 |
| C1 | failed | 20 | 20 | 20 | 55 | 20 | 20 |

The session holds 154 unique records.

*Audit trail:* scholar session `t-exploratory`; hit list [t-exploratory.csv](literature/sessions/t-exploratory.csv), records [t-exploratory.bib](literature/sessions/t-exploratory.bib), queries [t-exploratory.queries.tsv](literature/sessions/t-exploratory.queries.tsv), LaTeX audit table [t-exploratory-table.tex](literature/sessions/t-exploratory-table.tex).

### Findings

**Supporting.**

- [Afzal et al. 2015](#ref-Afzal2015): In four controlled experiments, exploratory testing found significantly more defects than test-case-based testing.
  > "The results show that ET found a significantly greater number of defects. ET also found significantly more defects of varying levels of difficulty, types and severity levels."
  > (abstract, p. 844; read in full text)
- [Enoiu et al. 2017](#ref-Enoiu2017): Manual tests detected logical, timer and negation faults better than automatically generated tests at similar coverage.
  > "manual tests more effectively detect logical, timer and negation type of faults, compared to automatically generated tests."
  > (abstract; abstract only)

**Qualifying or contradicting.**

- [Itkonen et al. 2007](#ref-Itkonen2007): In a controlled experiment, exploratory and test-case-based manual testing did not differ significantly in defect detection; ET gave fewer false reports.
  > "We found no significant differences in defect detection efficiency between TCT and ET."
  > (abstract; abstract only)

### Discussion and limitations

The experiments compare manual exploratory testing with manual testing from pre-written test cases, mostly by students in 90-minute sessions; Enoiu et al. (2017) compares manual test cases with generated ones. None compares a quick manual run with an automated unit-test suite, which is what the skill describes. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Mixed: one replicated experiment found that exploratory testing finds more defects than scripted manual testing, an earlier one found no difference, and none addresses manual trying alongside an automated suite. Verdict: **Contested** as a defect-finding claim. The skill's advice does not depend on it (it turns surprises into tests); no wording change needed, but do not cite it as proven.

**Wording in the skill after this review.** Unchanged: the skill's claim is narrower than the contested one: try the change for real, then pin every surprise as a test. It does not claim that manual exploration finds more defects than scripted tests.

### Future work

Itkonen et al. (2007) and Enoiu et al. (2017) were read at abstract level.

### Hit list

Records bearing on the claim: 3 cited (reviewed by hand), 10 further supporting and 8 further qualifying or contradicting as labelled by the model (unreviewed), out of 154 records; 34 adjacent and 99 off-topic records are not listed. The full classified list is in [t-exploratory.csv](literature/sessions/t-exploratory.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [Defect Detection Efficiency: Test Case Based vs. Exploratory Testing](https://doi.org/10.1109/esem.2007.56) | 2007 | qualifies | cited: et-no-difference |
| [An experiment on the effectiveness and efficiency of exploratory testing](https://doi.org/10.1007/s10664-014-9301-4) | 2014 | supports | cited: et-finds-more |
| [A Comparative Study of Manual and Automated Testing for Industrial Control Software](https://doi.org/10.1109/ICST.2017.44) | 2017 | qualifies | cited: manual-vs-generated |

<a id="ch-verified-fakes"></a>

## 20. Do hand-written fakes need verifying against the real implementation?

**Claim in the draft skill.** §1, rung 4: "Put the fake behind our own thin wrapper (Shore's *Nullables*), and cover it with the live check in section 3."

**Research question.** Do hand-written fakes need to be verified against the real implementation (verified fakes, contract tests for fakes) to stay faithful?

### Method

Searched on 2026-10-12 with `scholar` in OpenAlex, IEEE Xplore, arXiv, Web of Science and Scopus (DBLP failed, Semantic Scholar not searched; see the introduction). Queries:

| Query | Keywords (verbatim) |
|---|---|
| S1 | `("test doubles" OR fakes OR "fake objects" OR "mock objects" OR stubs) AND ("contract tests" OR "contract testing" OR conformance OR "differential testing" OR fidelity OR validation) AND ("real implementation" OR production OR dependency OR service)` |
| C1 | `("test doubles" OR fakes OR "fake objects" OR "mock objects" OR stubs) AND (automatic OR generated OR "mock generation" OR synthesis) AND (validity OR fidelity OR accuracy OR realistic)` |

Hits per query and database (at most 20; *failed* = not searched; *not recorded* = the search ran but its per-database count was not kept; the union column is the deduplicated total of IEEE, OpenAlex and arXiv):

| Query | DBLP | IEEE | OA | arXiv | IEEE+OA+arXiv | WoS | Scopus |
|---|---|---|---|---|---|---|---|
| S1 | failed | 20 | 20 | 20 | 58 | 20 | 20 |
| C1 | failed | 20 | 20 | 20 | 59 | 20 | 20 |

The session holds 177 unique records.

*Audit trail:* scholar session `t-verified-fakes`; hit list [t-verified-fakes.csv](literature/sessions/t-verified-fakes.csv), records [t-verified-fakes.bib](literature/sessions/t-verified-fakes.bib), queries [t-verified-fakes.queries.tsv](literature/sessions/t-verified-fakes.queries.tsv), LaTeX audit table [t-verified-fakes-table.tex](literature/sessions/t-verified-fakes-table.tex).

### Findings

**Supporting.**

- [Winters et al. 2020](#ref-Winters2020): Practitioner (Google): a fake must have its own tests against the real implementation (contract tests), or it diverges; prefer real implementations; interaction testing is brittle.
  > "A fake must have its own tests to ensure that it conforms to the API of its corresponding real implementation. A fake without tests might initially provide realistic behavior, but without tests, this behavior can diverge over time as the real implementation evolves."
  > (ch. 13, 'Fakes Should Be Tested'; read in full text)
- [Fowler 2011](#ref-Fowler2011): Practitioner: periodically run contract tests that check test doubles against the external service; check format, not exact data.
  > "periodically run a separate set of contract tests. These check that all the calls against your test doubles return the same results as a call to the external service would."
  > (bliki 'Contract Test', 12 Jan 2011; read in full text)
- [de Aquino & Alves 2025](#ref-DeAquino2025): Hand-declared API mocks often do not comply with the real service's API; a validating tool improved compliance by 24.1%.
  > "API mocks, which intercept communications with external services to return simulated responses, must closely align with the actual service to ensure realistic and effective test scenarios."
  > (abstract; abstract only)

**Qualifying or contradicting.**

- [Zhang 2026](#ref-Zhang2026): Static doubles of any kind reproduce only behaviour encoded when they were made.
  > "Existing approaches—record-replay, pattern-mining, and specification-driven stubs—generate a static artifact before tests run, so they can only reproduce behaviors encoded at generation time."
  > (abstract, arXiv:2604.04806v4 PDF; read in full text)

### Discussion and limitations

The support query matched many unrelated "fake" papers (fake news, deepfakes); the relevant test-double papers it found also appeared in the drift and record-replay chapters. No study of verified fakes was found. At most 20 hits per database and query were screened, DBLP could not be searched, and some IEEE counts were not recorded.

### Conclusion

Unknown empirically: verifying fakes against the real implementation is practitioner advice, supported indirectly by the evidence that doubles drift (the first chapter) and that static doubles cover only what they encode. Verdict: **Practitioner-only.** The skill's rung 4 matches the practitioner source; no wording change needed.

**Wording in the skill after this review.** Unchanged: rung 4 still requires a live check for a hand-written fake.

### Future work

A study of fakes with and without contract tests over a project's history would show how often unverified fakes drift.

### Hit list

Records bearing on the claim: 2 cited (reviewed by hand), 0 further supporting and 0 further qualifying or contradicting as labelled by the model (unreviewed), out of 177 records; 18 adjacent and 157 off-topic records are not listed. The full classified list is in [t-verified-fakes.csv](literature/sessions/t-verified-fakes.csv). The unreviewed rows are in that CSV; the table below lists only the reviewed (cited) rows.

| Title | Year | Category | Reason |
|---|---|---|---|
| [MIRAGE: Online LLM Simulation for Microservice Dependency Testing](https://doi.org/10.48550/arXiv.2604.04806) | 2026 | qualifies | cited: replay-fidelity |
| [Zimic: Bridging the Gaps in API Mocking for Typescript Projects](https://doi.org/10.1109/COMPSAC65507.2025.00177) | 2025 | supports | cited: mock-compatibility |

## References

<a id="ref-Afzal2015"></a>**Afzal et al. 2015.** Afzal, Wasif; Ghazi, Ahmad Nauman; Itkonen, Juha; Torkar, Richard; Andrews, Anneliese; Bhatti, Khurram. *An experiment on the effectiveness and efficiency of exploratory testing*. Empirical Software Engineering, vol. 20, pp. 844–878. [10.1007/s10664-014-9301-4](https://doi.org/10.1007/s10664-014-9301-4).

<a id="ref-Alonso2026"></a>**Alonso et al. 2026.** Alonso, Pepe; Yovine, Sergio; Braberman, Victor A. *TDAD: Test-Driven Agentic Development - Reducing Code Regressions in AI Coding Agents via Graph-Based Impact Analysis*. arXiv. [10.48550/ARXIV.2603.17973](https://doi.org/10.48550/ARXIV.2603.17973).

<a id="ref-Bacchelli2013"></a>**Bacchelli & Bird 2013.** Bacchelli, Alberto; Bird, Christian. *Expectations, outcomes, and challenges of modern code review*. 2013 35th International Conference on Software Engineering (ICSE), pp. 712–721. [10.1109/icse.2013.6606617](https://doi.org/10.1109/icse.2013.6606617).

<a id="ref-Beller2014"></a>**Beller et al. 2014.** Beller, Moritz; Bacchelli, Alberto; Zaidman, Andy; Juergens, Elmar. *Modern code reviews in open-source projects: which problems do they fix?*. Proceedings of the 11th Working Conference on Mining Software Repositories, pp. 202–211. [10.1145/2597073.2597082](https://doi.org/10.1145/2597073.2597082).

<a id="ref-Charpentier2025"></a>**Charpentier & Lison 2025.** Charpentier, Lucas Georges Gabriel; Lison, Pierre. *Re-identification of De-identified Documents with Autoregressive Infilling*. Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 1192–1209. [10.18653/v1/2025.acl-long.60](https://doi.org/10.18653/v1/2025.acl-long.60).

<a id="ref-Chen2023"></a>**Chen et al. 2023.** Chen, Xinyun; Lin, Maxwell; Schärli, Nathanael; Zhou, Denny. *Teaching Large Language Models to Self-Debug*. arXiv. [10.48550/ARXIV.2304.05128](https://doi.org/10.48550/ARXIV.2304.05128).

<a id="ref-ChenX2025"></a>**Chen et al. 2025.** Chen, Xiancai; Tao, Zhengwei; Zhang, Kechi; Zhou, Changzhi; Zhang, Xinyu; Gu, Wanli; He, Yuanpeng; Zhang, Mengdi; Cai, Xunliang; Zhao, Haiyan; Jin, Zhi. *Revisit Self-Debugging with Self-Generated Tests for Code Generation*. Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 18003–18023. [10.18653/v1/2025.acl-long.881](https://doi.org/10.18653/v1/2025.acl-long.881).

<a id="ref-CJEU2025"></a>**Court of Justice of the European Union 2025.** Court of Justice of the European Union. *Judgment of the Court in Case C-413/23 P, EDPS v SRB (Concept of personal data)*. Press release No 107/25. [https://curia.europa.eu/jcms/upload/docs/application/pdf/2025-09/cp250107en.pdf](https://curia.europa.eu/jcms/upload/docs/application/pdf/2025-09/cp250107en.pdf).

<a id="ref-Czerwonka2015"></a>**Czerwonka et al. 2015.** Czerwonka, Jacek; Greiler, Michaela; Tilford, Jack. *Code Reviews Do Not Find Bugs. How the Current Code Review Best Practice Slows Us Down*. 2015 IEEE/ACM 37th IEEE International Conference on Software Engineering, pp. 27–28. [10.1109/icse.2015.131](https://doi.org/10.1109/icse.2015.131).

<a id="ref-DeAquino2025"></a>**de Aquino & Alves 2025.** de Aquino, Diego Cruz; Alves, Everton L. G. *Zimic: Bridging the Gaps in API Mocking for Typescript Projects*. 2025 IEEE 49th Annual Computers, Software, and Applications Conference (COMPSAC), pp. 1406–1415. [10.1109/compsac65507.2025.00177](https://doi.org/10.1109/compsac65507.2025.00177).

<a id="ref-Demir2018"></a>**Demir et al. 2018.** Demir, Levent; Kumar, Amrit; Cunche, Mathieu; Lauradoux, Cedric. *The Pitfalls of Hashing for Privacy*. IEEE Communications Surveys & Tutorials, vol. 20, pp. 551–565. [10.1109/comst.2017.2747598](https://doi.org/10.1109/comst.2017.2747598).

<a id="ref-DiLauro2021"></a>**Di Lauro et al. 2021.** Di Lauro, Fabio; Serbout, Souhaila; Pautasso, Cesare. *Towards Large-Scale Empirical Assessment of Web APIs Evolution*. Web Engineering, pp. 124–138. [10.1007/978-3-030-74296-6_10](https://doi.org/10.1007/978-3-030-74296-6_10).

<a id="ref-DiLauro2022"></a>**Di Lauro et al. 2022.** Di Lauro, Fabio; Serbout, Souhaila; Pautasso, Cesare. *To Deprecate or to Simply Drop Operations? An Empirical Study on the Evolution of a Large OpenAPI Collection*. Software Architecture, pp. 38–46. [10.1007/978-3-031-16697-6_3](https://doi.org/10.1007/978-3-031-16697-6_3).

<a id="ref-Eck2019"></a>**Eck et al. 2019.** Eck, Moritz; Palomba, Fabio; Castelluccio, Marco; Bacchelli, Alberto. *Understanding flaky tests: the developer’s perspective*. Proceedings of the 2019 27th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering, pp. 830–840. [10.1145/3338906.3338945](https://doi.org/10.1145/3338906.3338945).

<a id="ref-Enoiu2017"></a>**Enoiu et al. 2017.** Enoiu, Eduard; Sundmark, Daniel; Causevic, Adnan; Pettersson, Paul. *A Comparative Study of Manual and Automated Testing for Industrial Control Software*. 2017 IEEE International Conference on Software Testing, Verification and Validation (ICST), pp. 412–417. [10.1109/icst.2017.44](https://doi.org/10.1109/icst.2017.44).

<a id="ref-EDPB2025"></a>**European Data Protection Board 2025.** European Data Protection Board. *Guidelines 01/2025 on Pseudonymisation (version for public consultation)*. [https://www.edpb.europa.eu/system/files/2025-01/edpb_guidelines_202501_pseudonymisation_en.pdf](https://www.edpb.europa.eu/system/files/2025-01/edpb_guidelines_202501_pseudonymisation_en.pdf). Adopted 16 January 2025.

<a id="ref-Fowler2007"></a>**Fowler 2007.** Fowler, Martin. *Mocks Aren't Stubs*. [https://martinfowler.com/articles/mocksArentStubs.html](https://martinfowler.com/articles/mocksArentStubs.html).

<a id="ref-Fowler2011"></a>**Fowler 2011.** Fowler, Martin. *Contract Test*. bliki. [https://martinfowler.com/bliki/ContractTest.html](https://martinfowler.com/bliki/ContractTest.html).

<a id="ref-Fowler2014"></a>**Fowler 2014.** Fowler, Martin. *Unit Test*. bliki. [https://martinfowler.com/bliki/UnitTest.html](https://martinfowler.com/bliki/UnitTest.html).

<a id="ref-Fucci2017"></a>**Fucci et al. 2017.** Fucci, Davide; Erdogmus, Hakan; Turhan, Burak; Oivo, Markku; Juristo, Natalia. *A Dissection of the Test-Driven Development Process: Does It Really Matter to Test-First or to Test-Last?*. IEEE Transactions on Software Engineering, vol. 43, pp. 597–614. [10.1109/tse.2016.2616877](https://doi.org/10.1109/tse.2016.2616877).

<a id="ref-Gabor2025"></a>**Gabor et al. 2025.** Gabor, Jonathan; Lynch, Jayson; Rosenfeld, Jonathan. *EvilGenie: A Reward Hacking Benchmark*. arXiv. [10.48550/ARXIV.2511.21654](https://doi.org/10.48550/ARXIV.2511.21654).

<a id="ref-Ginelli2022"></a>**Ginelli et al. 2022.** Ginelli, Davide; Martinez, Matias; Mariani, Leonardo; Monperrus, Martin. *A comprehensive study of code-removal patches in automated program repair*. Empirical Software Engineering, vol. 27. [10.1007/s10664-021-10100-7](https://doi.org/10.1007/s10664-021-10100-7).

<a id="ref-Gregor2025"></a>**Gregor et al. 2025.** Gregor, Lena; Skalski, Marcel; Pretschner, Alexander. *Benchmarking Component and Integration Testing in Microservices: Test Suites and Fault Analysis on TrainTicket*. 2025 IEEE International Conference on Service-Oriented System Engineering (SOSE), pp. 39–50. [10.1109/sose67019.2025.00009](https://doi.org/10.1109/sose67019.2025.00009).

<a id="ref-Gruber2021"></a>**Gruber et al. 2021.** Gruber, Martin; Lukasczyk, Stephan; Krois, Florian; Fraser, Gordon. *An Empirical Study of Flaky Tests in Python*. 2021 14th IEEE Conference on Software Testing, Verification and Validation (ICST), pp. 148–158. [10.1109/icst49551.2021.00026](https://doi.org/10.1109/icst49551.2021.00026).

<a id="ref-Guey2026"></a>**Guey & Bougault 2026.** Guey, William; Bougault, Pierrick. *Self-Preference Is Weak or Absent in Verifiable Instruction-Following Revision: A Four-Model Test Under Genuine Authorship*. arXiv. [10.48550/ARXIV.2606.20093](https://doi.org/10.48550/ARXIV.2606.20093).

<a id="ref-Hashemi2022"></a>**Hashemi et al. 2022.** Hashemi, Negar; Tahir, Amjed; Rasheed, Shawn. *An Empirical Study of Flaky Tests in JavaScript*. 2022 IEEE International Conference on Software Maintenance and Evolution (ICSME), pp. 24–34. [10.1109/icsme55016.2022.00011](https://doi.org/10.1109/icsme55016.2022.00011).

<a id="ref-Hora2026"></a>**Hora & Robbes 2026.** Hora, Andre; Robbes, Romain. *Are Coding Agents Generating Over-Mocked Tests? An Empirical Study*. arXiv. [10.48550/ARXIV.2602.00409](https://doi.org/10.48550/ARXIV.2602.00409).

<a id="ref-Huang2024"></a>**Huang et al. 2024.** Huang, Jie; Chen, Xinyun; Mishra, Swaroop; Zheng, Huaixiu Steven; Yu, Adams Wei; Song, Xinying; Zhou, Denny. *Large Language Models Cannot Self-Correct Reasoning Yet*. arXiv. [10.48550/ARXIV.2310.01798](https://doi.org/10.48550/ARXIV.2310.01798). Published at ICLR 2024 (header of the arXiv version read).

<a id="ref-Huo2014"></a>**Huo & Clause 2014.** Huo, Chen; Clause, James. *Improving oracle quality by detecting brittle assertions and unused inputs in tests*. Proceedings of the 22nd ACM SIGSOFT International Symposium on Foundations of Software Engineering, pp. 621–631. [10.1145/2635868.2635917](https://doi.org/10.1145/2635868.2635917).

<a id="ref-Itkonen2007"></a>**Itkonen et al. 2007.** Itkonen, Juha; Mantyla, Mika V.; Lassenius, Casper. *Defect Detection Efficiency: Test Case Based vs. Exploratory Testing*. First International Symposium on Empirical Software Engineering and Measurement (ESEM 2007), pp. 61–70. [10.1109/esem.2007.56](https://doi.org/10.1109/esem.2007.56).

<a id="ref-Jahangirova2016"></a>**Jahangirova et al. 2016.** Jahangirova, Gunel; Clark, David; Harman, Mark; Tonella, Paolo. *Test oracle assessment and improvement*. Proceedings of the 25th International Symposium on Software Testing and Analysis, pp. 247–258. [10.1145/2931037.2931062](https://doi.org/10.1145/2931037.2931062).

<a id="ref-Just2014"></a>**Just et al. 2014.** Just, René; Jalali, Darioush; Inozemtseva, Laura; Ernst, Michael D.; Holmes, Reid; Fraser, Gordon. *Are mutants a valid substitute for real faults in software testing?*. Proceedings of the 22nd ACM SIGSOFT International Symposium on Foundations of Software Engineering, pp. 654–665. [10.1145/2635868.2635929](https://doi.org/10.1145/2635868.2635929).

<a id="ref-Kamoi2024"></a>**Kamoi et al. 2024.** Kamoi, Ryo; Zhang, Yusen; Zhang, Nan; Han, Jiawei; Zhang, Rui. *When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs*. Transactions of the Association for Computational Linguistics, vol. 12, pp. 1417–1440. [10.1162/tacl_a_00713](https://doi.org/10.1162/tacl_a_00713).

<a id="ref-Knight2025"></a>**Knight & Bhowmik 2025.** Knight, Daniel; Bhowmik, Tanmay. *Toward a Resilience-Oriented Understanding of Unit Test Suites and Refactoring in Software Evolution*. 2025 IEEE International Conference on Software Maintenance and Evolution (ICSME), pp. 857–859. [10.1109/icsme64153.2025.00092](https://doi.org/10.1109/icsme64153.2025.00092).

<a id="ref-Konstantinou2026"></a>**Konstantinou et al. 2026.** Konstantinou, Michael; Tambon, Florian; Papadakis, Mike. *On the risk of coding before testing: An empirical study on LLM-based test generation workflow*. arXiv. [10.48550/ARXIV.2607.05139](https://doi.org/10.48550/ARXIV.2607.05139).

<a id="ref-Kovacevic2024"></a>**Kovačević et al. 2024.** Kovačević, Aleksandar; Bašaragin, Bojana; Milošević, Nikola; Nenadić, Goran. *De-identification of clinical free text using natural language processing: A systematic review of current approaches*. Artificial Intelligence in Medicine, vol. 151, pp. 102845. [10.1016/j.artmed.2024.102845](https://doi.org/10.1016/j.artmed.2024.102845).

<a id="ref-Krause2022"></a>**Krause et al. 2022.** Krause, Alexander; Klemmer, Jan H.; Huaman, Nicolas; Wermke, Dominik; Acar, Yasemin; Fahl, Sascha. *Pushed by Accident: A Mixed-Methods Study on Strategies of Handling Secret Information in Source Code Repositories*. arXiv. [10.48550/ARXIV.2211.06213](https://doi.org/10.48550/ARXIV.2211.06213).

<a id="ref-Lehva2019"></a>**Lehvä et al. 2019.** Lehvä, Jyri; Mäkitalo, Niko; Mikkonen, Tommi. *Consumer-Driven Contract Tests for Microservices: A Case Study*. Product-Focused Software Process Improvement, pp. 497–512. [10.1007/978-3-030-35333-9_35](https://doi.org/10.1007/978-3-030-35333-9_35).

<a id="ref-Li2013"></a>**Li et al. 2013.** Li, Jun; Xiong, Yingfei; Liu, Xuanzhe; Zhang, Lu. *How Does Web Service API Evolution Affect Clients?*. 2013 IEEE 20th International Conference on Web Services, pp. 300–307. [10.1109/icws.2013.48](https://doi.org/10.1109/icws.2013.48).

<a id="ref-Liu2014"></a>**Liu et al. 2014.** Liu, Huai; Kuo, Fei-Ching; Towey, Dave; Chen, Tsong Yueh. *How Effectively Does Metamorphic Testing Alleviate the Oracle Problem?*. IEEE Transactions on Software Engineering, vol. 40, pp. 4–22. [10.1109/tse.2013.46](https://doi.org/10.1109/tse.2013.46).

<a id="ref-Liu2022"></a>**Liu et al. 2022.** Liu, Jiangchao; Liu, Jierui; Di, Peng; Liu, Alex X.; Zhong, Zexin. *Record and Replay of Online Traffic for Microservices with Automatic Mocking Point Identification*. 2022 IEEE/ACM 44th International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP), pp. 221–230. [10.1109/icse-seip55303.2022.9793867](https://doi.org/10.1109/icse-seip55303.2022.9793867).

<a id="ref-LiuSC2024"></a>**Liu et al. 2024.** Liu, Dancheng; Nassereldine, Amir; Yang, Ziming; Xu, Chenhui; Hu, Yuting; Li, Jiajie; Kumar, Utkarsh; Lee, Changjae; Qin, Ruiyang; Shi, Yiyu; Xiong, Jinjun. *Large Language Models have Intrinsic Self-Correction Ability*. arXiv. [10.48550/ARXIV.2406.15673](https://doi.org/10.48550/ARXIV.2406.15673).

<a id="ref-Luo2014"></a>**Luo et al. 2014.** Luo, Qingzhou; Hariri, Farah; Eloussi, Lamyaa; Marinov, Darko. *An empirical analysis of flaky tests*. Proceedings of the 22nd ACM SIGSOFT International Symposium on Foundations of Software Engineering, pp. 643–653. [10.1145/2635868.2635920](https://doi.org/10.1145/2635868.2635920).

<a id="ref-Mathews2024"></a>**Mathews & Nagappan 2024a.** Mathews, Noble Saji; Nagappan, Meiyappan. *Test-Driven Development and LLM-based Code Generation*. Proceedings of the 39th IEEE/ACM International Conference on Automated Software Engineering, pp. 1583–1594. [10.1145/3691620.3695527](https://doi.org/10.1145/3691620.3695527).

<a id="ref-Mathews2024b"></a>**Mathews & Nagappan 2024b.** Mathews, Noble Saji; Nagappan, Meiyappan. *Design choices made by LLM-based test generators prevent them from finding bugs*. arXiv. [10.48550/ARXIV.2412.14137](https://doi.org/10.48550/ARXIV.2412.14137).

<a id="ref-Meli2019"></a>**Meli et al. 2019.** Meli, Michael; McNiece, Matthew R.; Reaves, Bradley. *How Bad Can It Git? Characterizing Secret Leakage in Public GitHub Repositories*. Proceedings 2019 Network and Distributed System Security Symposium. [10.14722/ndss.2019.23418](https://doi.org/10.14722/ndss.2019.23418).

<a id="ref-Morris2024"></a>**Morris et al. 2024.** Morris, John X.; Campion, Thomas R.; Nutheti, Sri Laasya; Peng, Yifan; Raj, Akhil; Zabih, Ramin; Cole, Curtis L. *DIRI: Adversarial Patient Reidentification with Large Language Models for Evaluating Clinical Text Anonymization*. arXiv. [10.48550/ARXIV.2410.17035](https://doi.org/10.48550/ARXIV.2410.17035).

<a id="ref-Mourby2018"></a>**Mourby et al. 2018.** Mourby, Miranda; Mackey, Elaine; Elliot, Mark; Gowans, Heather; Wallace, Susan E.; Bell, Jessica; Smith, Hannah; Aidinlis, Stergios; Kaye, Jane. *Are ‘pseudonymised’ data always personal data? Implications of the GDPR for administrative data research in the UK*. Computer Law & Security Review, vol. 34, pp. 222–233. [10.1016/j.clsr.2018.01.002](https://doi.org/10.1016/j.clsr.2018.01.002).

<a id="ref-Nagappan2008"></a>**Nagappan et al. 2008.** Nagappan, Nachiappan; Maximilien, E. Michael; Bhat, Thirumalesh; Williams, Laurie. *Realizing quality improvement through test driven development: results and experiences of four industrial teams*. Empirical Software Engineering, vol. 13, pp. 289–302. [10.1007/s10664-008-9062-z](https://doi.org/10.1007/s10664-008-9062-z).

<a id="ref-Niedermayr2016"></a>**Niedermayr et al. 2016.** Niedermayr, Rainer; Juergens, Elmar; Wagner, Stefan. *Will my tests tell me if I break this code?*. Proceedings of the International Workshop on Continuous Software Evolution and Delivery, pp. 23–29. [10.1145/2896941.2896944](https://doi.org/10.1145/2896941.2896944).

<a id="ref-Norgeot2020"></a>**Norgeot et al. 2020.** Norgeot, Beau; Muenzen, Kathleen; Peterson, Thomas A.; Fan, Xuancheng; Glicksberg, Benjamin S.; Schenk, Gundolf; Rutenberg, Eugenia; Oskotsky, Boris; Sirota, Marina; Yazdany, Jinoos; Schmajuk, Gabriela; Ludwig, Dana; Goldstein, Theodore; Butte, Atul J. *Protected Health Information filter (Philter): accurately and securely de-identifying free-text clinical notes*. npj Digital Medicine, vol. 3. [10.1038/s41746-020-0258-y](https://doi.org/10.1038/s41746-020-0258-y).

<a id="ref-Olausson2024"></a>**Olausson et al. 2024.** Olausson, Theo X.; Inala, Jeevana Priya; Wang, Chenglong; Gao, Jianfeng; Solar-Lezama, Armando. *Is Self-Repair a Silver Bullet for Code Generation?*. arXiv. [10.48550/ARXIV.2306.09896](https://doi.org/10.48550/ARXIV.2306.09896). Published at ICLR 2024 (header of the arXiv version read).

<a id="ref-Orellana2017"></a>**Orellana et al. 2017.** Orellana, Gerardo; Laghari, Gulsher; Murgia, Alessandro; Demeyer, Serge. *On the Differences between Unit and Integration Testing in the TravisTorrent Dataset*. 2017 IEEE/ACM 14th International Conference on Mining Software Repositories (MSR), pp. 451–454. [10.1109/msr.2017.25](https://doi.org/10.1109/msr.2017.25).

<a id="ref-Papadakis2018"></a>**Papadakis et al. 2018.** Papadakis, Mike; Shin, Donghwan; Yoo, Shin; Bae, Doo-Hwan. *Are mutation scores correlated with real fault detection?: a large scale empirical study on the relationship between mutants and real faults*. Proceedings of the 40th International Conference on Software Engineering, pp. 537–548. [10.1145/3180155.3180183](https://doi.org/10.1145/3180155.3180183).

<a id="ref-Parry2022"></a>**Parry et al. 2022.** Parry, Owain; Kapfhammer, Gregory M.; Hilton, Michael; McMinn, Phil. *A Survey of Flaky Tests*. ACM Transactions on Software Engineering and Methodology, vol. 31, pp. 1–74. [10.1145/3476105](https://doi.org/10.1145/3476105).

<a id="ref-Petke2024"></a>**Petke et al. 2024.** Petke, Justyna; Martinez, Matias; Kechagia, Maria; Aleti, Aldeida; Sarro, Federica. *The Patch Overfitting Problem in Automated Program Repair: Practical Magnitude and a Baseline for Realistic Benchmarking*. Companion Proceedings of the 32nd ACM International Conference on the Foundations of Software Engineering, pp. 452–456. [10.1145/3663529.3663776](https://doi.org/10.1145/3663529.3663776).

<a id="ref-Petrovic2021"></a>**Petrović et al. 2021.** Petrović, Goran; Ivanković, Marko; Fraser, Gordon; Just, René. *Does Mutation Testing Improve Testing Practices?*. 2021 IEEE/ACM 43rd International Conference on Software Engineering (ICSE), pp. 910–921. [10.1109/icse43902.2021.00087](https://doi.org/10.1109/icse43902.2021.00087).

<a id="ref-Rafique2013"></a>**Rafique & Misic 2013.** Rafique, Yahya; Misic, Vojislav B. *The Effects of Test-Driven Development on External Quality and Productivity: A Meta-Analysis*. IEEE Transactions on Software Engineering, vol. 39, pp. 835–856. [10.1109/tse.2012.28](https://doi.org/10.1109/tse.2012.28).

<a id="ref-Roytburg2026"></a>**Roytburg et al. 2026.** Roytburg, Dani; Bozoukov, Matthew; Nguyen, Matthew; Barzdukas, Jou; Puig-Hall, Mackenzie; Oozeer, Narmeen. *Are LLM Evaluators Really Narcissists? Sanity Checking Self-Preference Evaluations*. arXiv. [10.48550/ARXIV.2601.22548](https://doi.org/10.48550/ARXIV.2601.22548).

<a id="ref-Santos2021"></a>**Santos et al. 2021.** Santos, Adrian; Vegas, Sira; Dieste, Oscar; Uyaguari, Fernando; Tosun, Ayşe; Fucci, Davide; Turhan, Burak; Scanniello, Giuseppe; Romano, Simone; Karac, Itir; Kuhrmann, Marco; Mandić, Vladimir; Ramač, Robert; Pfahl, Dietmar; Engblom, Christian; Kyykka, Jarno; Rungi, Kerli; Palomeque, Carolina; Spisak, Jaroslav; Oivo, Markku; Juristo, Natalia. *A family of experiments on test-driven development*. Empirical Software Engineering, vol. 26. [10.1007/s10664-020-09895-8](https://doi.org/10.1007/s10664-020-09895-8).

<a id="ref-Schwarz2025"></a>**Schwarz et al. 2025.** Schwarz, Georg‐Daniel; Quast, Felix; Riehle, Dirk. *Ensuring Syntactic Interoperability Using Consumer‐Driven Contract Testing*. Software Testing, Verification and Reliability, vol. 35. [10.1002/stvr.70006](https://doi.org/10.1002/stvr.70006).

<a id="ref-Serbout2024"></a>**Serbout & Pautasso 2024.** Serbout, Souhaila; Pautasso, Cesare. *How Many Web APIs Evolve Following Semantic Versioning?*. Web Engineering, pp. 344–359. [10.1007/978-3-031-62362-2_25](https://doi.org/10.1007/978-3-031-62362-2_25).

<a id="ref-Shore2023"></a>**Shore 2023.** Shore, James. *Testing Without Mocks: A Pattern Language*. [https://www.jamesshore.com/v2/projects/nullables/testing-without-mocks](https://www.jamesshore.com/v2/projects/nullables/testing-without-mocks).

<a id="ref-Song2026"></a>**Song 2026.** Song, Tae-Eun. *Cross-Context Review: Improving LLM Output Quality by Separating Production and Review Sessions*. arXiv. [10.48550/ARXIV.2603.12123](https://doi.org/10.48550/ARXIV.2603.12123).

<a id="ref-Spadini2017"></a>**Spadini et al. 2017.** Spadini, Davide; Aniche, Mauricio; Bruntink, Magiel; Bacchelli, Alberto. *To Mock or Not to Mock? An Empirical Study on Mocking Practices*. 2017 IEEE/ACM 14th International Conference on Mining Software Repositories (MSR), pp. 402–412. [10.1109/msr.2017.61](https://doi.org/10.1109/msr.2017.61).

<a id="ref-Spadini2019"></a>**Spadini et al. 2019.** Spadini, Davide; Aniche, Maurício; Bruntink, Magiel; Bacchelli, Alberto. *Mock objects for testing java systems: Why and how developers use them, and how they evolve*. Empirical Software Engineering, vol. 24, pp. 1461–1498. [10.1007/s10664-018-9663-0](https://doi.org/10.1007/s10664-018-9663-0).

<a id="ref-Stubbs2015"></a>**Stubbs et al. 2015.** Stubbs, Amber; Kotfila, Christopher; Uzuner, Özlem. *Automated systems for the de-identification of longitudinal clinical narratives: Overview of 2014 i2b2/UTHealth shared task Track 1*. Journal of Biomedical Informatics, vol. 58, pp. S11–S19. [10.1016/j.jbi.2015.06.007](https://doi.org/10.1016/j.jbi.2015.06.007).

<a id="ref-TaheriGhazvini2025"></a>**Taheri Ghazvini 2025.** Taheri Ghazvini, Ehsan. *From Isolation to Integration: An empirical study on differences between unit and integration testing with applications to C programs*. Master's thesis, Carleton University. [10.22215/etd/2025-16598](https://doi.org/10.22215/etd/2025-16598).

<a id="ref-Tiwari2024"></a>**Tiwari et al. 2024.** Tiwari, Deepika; Monperrus, Martin; Baudry, Benoit. *Mimicking Production Behavior With Generated Mocks*. IEEE Transactions on Software Engineering, vol. 50, pp. 2921–2946. [10.1109/tse.2024.3458448](https://doi.org/10.1109/tse.2024.3458448).

<a id="ref-Trautsch2020"></a>**Trautsch et al. 2020.** Trautsch, Fabian; Herbold, Steffen; Grabowski, Jens. *Are unit and integration test definitions still valid for modern Java projects? An empirical study on open-source projects*. Journal of Systems and Software, vol. 159, pp. 110421. [10.1016/j.jss.2019.110421](https://doi.org/10.1016/j.jss.2019.110421).

<a id="ref-Versteeg2016"></a>**Versteeg et al. 2016.** Versteeg, Steve; Du, Miao; Schneider, Jean-Guy; Grundy, John; Han, Jun; Goyal, Menka. *Opaque service virtualisation: a practical tool for emulating endpoint systems*. Proceedings of the 38th International Conference on Software Engineering Companion, pp. 202–211. [10.1145/2889160.2889242](https://doi.org/10.1145/2889160.2889242).

<a id="ref-Wang2014"></a>**Wang et al. 2014.** Wang, Shaohua; Keivanloo, Iman; Zou, Ying. *How Do Developers React to RESTful API Evolution?*. Service-Oriented Computing, pp. 245–259. [10.1007/978-3-662-45391-9_17](https://doi.org/10.1007/978-3-662-45391-9_17).

<a id="ref-Wataoka2024"></a>**Wataoka et al. 2024.** Wataoka, Koki; Takahashi, Tsubasa; Ri, Ryokan. *Self-Preference Bias in LLM-as-a-Judge*. arXiv. [10.48550/ARXIV.2410.21819](https://doi.org/10.48550/ARXIV.2410.21819).

<a id="ref-Willison2026"></a>**Willison 2026.** Willison, Simon. *First run the tests*. Agentic Engineering Patterns (online guide). [https://simonwillison.net/guides/agentic-engineering-patterns/first-run-the-tests/](https://simonwillison.net/guides/agentic-engineering-patterns/first-run-the-tests/). Accessed 2026-10-12.

<a id="ref-Winters2020"></a>**Winters et al. 2020.** Winters, Titus; Manshreck, Tom; Wright, Hyrum. *Software Engineering at Google: Lessons Learned from Programming Over Time*. O'Reilly, ch. 13, Test Doubles (Andrew Trenk and Dillon Bly). [https://abseil.io/resources/swe-book/html/ch13.html](https://abseil.io/resources/swe-book/html/ch13.html).

<a id="ref-Xia2023"></a>**Xia et al. 2023.** Xia, Chunqiu Steven; Dutta, Saikat; Misailovic, Sasa; Marinov, Darko; Zhang, Lingming. *Balancing Effectiveness and Flakiness of Non-Deterministic Machine Learning Tests*. 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE), pp. 1801–1813. [10.1109/icse48619.2023.00154](https://doi.org/10.1109/icse48619.2023.00154).

<a id="ref-Xu2024"></a>**Xu et al. 2024.** Xu, Wenda; Zhu, Guanglei; Zhao, Xuandong; Pan, Liangming; Li, Lei; Wang, William. *Pride and Prejudice: LLM Amplifies Self-Bias in Self-Refinement*. Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 15474–15492. [10.18653/v1/2024.acl-long.826](https://doi.org/10.18653/v1/2024.acl-long.826).

<a id="ref-Zhang2026"></a>**Zhang 2026.** Zhang, XinRan. *MIRAGE: Online LLM Simulation for Microservice Dependency Testing*. arXiv. [10.48550/ARXIV.2604.04806](https://doi.org/10.48550/ARXIV.2604.04806).

<a id="ref-Zhong2025"></a>**Zhong et al. 2025.** Zhong, Ziqian; Raghunathan, Aditi; Carlini, Nicholas. *ImpossibleBench: Measuring LLMs' Propensity of Exploiting Test Cases*. arXiv. [10.48550/ARXIV.2510.20270](https://doi.org/10.48550/ARXIV.2510.20270).

<a id="ref-Zhu2023"></a>**Zhu et al. 2023.** Zhu, Hengcheng; Wei, Lili; Terragni, Valerio; Liu, Yepang; Cheung, Shing-Chi; Wu, Jiarong; Sheng, Qin; Zhang, Bing; Song, Lihong. *StubCoder : Automated Generation and Repair of Stub Code for Mock Objects*. ACM Transactions on Software Engineering and Methodology, vol. 33, pp. 1–31. [10.1145/3617171](https://doi.org/10.1145/3617171).

<a id="ref-Zhu2025"></a>**Zhu et al. 2025.** Zhu, Hengcheng; Terragni, Valerio; Wei, Lili; Cheung, Shing-Chi; Wu, Jiarong; Liu, Yepang. *Understanding and Characterizing Mock Assertions in Unit Tests*. Proceedings of the ACM on Software Engineering, vol. 2, pp. 554–575. [10.1145/3715741](https://doi.org/10.1145/3715741).
