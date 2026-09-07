# cleveref reference-type names: terminology first, localization second

The names `\cref` prints ("Section", "item", "Figure") are cleveref's
defaults, not the document's. Two distinct reasons to change them:

1. **Terminology** — the prose consistently uses a different word for the
   referent than cleveref's default, *in any language*.
2. **Localization** — the document is not in English and cleveref was never
   told.

Terminology is the general principle; localization is the special case where
*every* name is wrong at once.

## Match the printed name to the document's own terminology (any language)

**When you `\cref` a type, check that the name cleveref prints is the word the
prose itself uses — if not, override it.** A generic name that clashes with
the document's terminology reads as an inconsistency to the reader, even in
plain English:

- A tutorial presents an algorithm as numbered *steps* ("the steps run top to
  bottom…") but `\cref` of an `enumerate` item prints "item 5":
  `\crefname{enumi}{step}{steps}`.
- A style guide numbers *rules* in a theorem-style environment declared as
  `remark`: the reference prints "Remark 3" where the prose says "rule 3" —
  either declare a dedicated `rule` environment or `\crefname{remark}{rule}{rules}`.
- A methods paper calls its numbered floats *protocols*, not "figures".

Worked example in Swedish (the case that prompted this file): a teaching text
presents algorithms as enumerated *steg* ("stegen utförs i tur och
ordning…") and cross-references individual steps ("Repetera
\cref{mjöl,vispa-mjöl}"). cleveref's Swedish default for `enumi` is "punkt",
so the reference would render "Repetera punkt 5 och 6" — clashing with the
prose. Override:

```latex
\AtBeginDocument{%
  % The only \cref'd list items in this document are algorithm steps; the
  % prose consistently calls them "steg", not cleveref's default "punkt".
  \crefname{enumi}{steg}{steg}%
  \Crefname{enumi}{Steg}{Steg}%
}
```

Now "Repetera \cref{mjöl,vispa-mjöl}" renders "Repetera steg 5 och 6" — and a
bare hand-written "Repetera 5 och 6" (no type word at all) is avoided too.

**Scope caveat**: a `\crefname` override is per-type and document-wide, so it
is only the whole answer when every `\cref`'d instance of that type is the
same kind of thing (above: all referenced `enumi` items are algorithm steps).

## Several kinds at the same time

When one document mixes kinds — some enumerated lists are steps, others
survey questions — two mechanisms give each its own reference name (verified
to coexist in one document, with hyperref loaded):

**Per-label type override — cleveref's `\label[⟨type⟩]{⟨key⟩}`.** Declare the
extra type's name once, then tag individual labels with it; untagged labels
keep the counter's default type:

```latex
\crefname{step}{step}{steps}   % a type that exists only via \label[...]
...
\begin{enumerate}
  \item \label[step]{whisk} …   % \cref{whisk}  -> "step 2"
  \item \label{other} …         % \cref{other}  -> "item 3" (default)
\end{enumerate}
```

Works anywhere `\label` works — including beamer frames, where the enumitem
route below is unavailable. Best when the kinds are interleaved or the
exception is rare.

**A dedicated list environment — enumitem's `\newlist`.** `\newlist` creates
a *distinct counter per list* (list name + level: `steps` at depth 1 counts
with `stepsi`), and cleveref attaches names to counters — so each environment
gets its own reference name with plain `\label`:

```latex
\newlist{steps}{enumerate}{1}
\setlist[steps,1]{label=\arabic*., ref=\arabic*}  % ref= strips the label dot
\crefname{stepsi}{step}{steps}                    % counter = listname + i
...
\begin{steps}
  \item \label{whisk} …   % \cref{whisk} -> "step 2"
\end{steps}
```

(Without `ref=`, `\cref` inherits the label's formatting dot: "step 2.".)
Best when a kind is systematic enough to deserve its own environment — the
semantic-markup answer. **But not in beamer**: enumitem conflicts with
beamer's list internals (see the dual-build rules in SKILL.md — load it in
the article driver only), so in slide decks and dual beamer/article sources
use the `\label[type]` route inside frames instead.

## Types with no usable name: unnumbered environments, and beamer

Two cases where the override pattern above cannot help, because the printed
name is wrong for a reason other than terminology.

**An unnumbered environment prints `??`.** cleveref names a *counter*, so a
theorem-style environment declared without one has nothing to reference. The
didactic package's `remark`, `summary` and `solution` are unnumbered by design,
and `\cref` to a label inside one renders `??` (the `\label` picks up whatever
counter was last stepped, or none). Refer to such a block in prose by what it
says, and reserve `\cref` for the numbered types (`example`, `exercise`,
`definition`, figures, tables, sections).

**A dual beamer/article build prints the wrong word on slides.** An environment
that is a numbered theorem in the article is a beamer *block* in the slides, and
the beamer job resolves the type against its own theorem set: `\cref` to an
`example` prints "sats" (theorem) there while the article correctly prints
"exempel". Since the number means nothing on a slide anyway, emit the
cross-reference in the article only:

```latex
... som i det tidigare exemplet\only<article>{ (\cref{ex:division})}.
```

`\only<article>` (not `\mode<article>`) keeps this inline, so the sentence reads
correctly in both outputs. Same treatment for a `\cref` to any environment whose
type name differs between the two jobs.

## Overriding a shipped name: \AtBeginDocument, registered after cleveref's

cleveref's language options install their names in an `\AtBeginDocument`
hook. In a document using such an option, a top-level `\crefname` in the
preamble is therefore **silently overwritten** when that hook runs. Put
overrides inside your own `\AtBeginDocument`, registered *after*
`\usepackage[...]{cleveref}`, so yours runs later and wins:

```latex
\usepackage[swedish]{cleveref}
\AtBeginDocument{%
  % cleveref's Swedish set hardcodes the appendix type as "Appendix", but
  % memoir and babel call it "Bilaga".
  \crefname{appendix}{bilaga}{bilagor}%
  \Crefname{appendix}{Bilaga}{Bilagor}%
}
```

(Without a language option, a plain top-level `\crefname` works — but the
hook placement is always safe, so use it as the habit.)

(Combine with `\crefalias{chapter}{appendix}` after `\appendix` so appendix
chapters use the `appendix` type at all.)

## Localization: cleveref does not read babel's package options

cleveref picks its language from **its own package options or the global
document-class options** — *not* from `\usepackage[...]{babel}`. A document
whose babel main language is Swedish still gets English "Section 2.1" /
"Appendix A" from a bare `\usepackage{cleveref}`.

Fix in the preamble, either way:

```latex
\usepackage[swedish]{cleveref}
% or equivalently, a global class option cleveref will pick up:
\documentclass[swedish]{memoir}
```

cleveref ships name sets for many languages (check with
`awk '/DeclareOption{<lang>}/,/^\}/' $(kpsewhich cleveref.sty)`), so verify a
language exists before hand-rolling a `\crefname` list — hand-rolling is the
fallback, not the first move. Even a shipped set may need spot-fixes via the
override pattern above (the Swedish set's "Appendix", for example), and the
terminology principle applies on top of it.

Capitalization: do **not** add `[capitalize]` for Swedish — Swedish typography
wants lowercase mid-sentence references ("i avsnitt 2.1"); use `\Cref` for
sentence-initial ones.

## Verifying

Render and read the actual output (`pdftotext -layout`), grepping for the
reference sites: the type word, number, and conjunctions ("steg 5 och 6",
"avsnitt A.1") should match the prose's language and terminology. English
"Section"/"Appendix" in a localized document, or a type word the surrounding
prose never uses, means one of the rules above was missed.
