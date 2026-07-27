# cleveref localization: language options and reference-type names

How to get `\cref` output in the document's language, and how to make the
printed type names match the document's own terminology.

## cleveref does not read babel's package options

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
fallback, not the first move.

Capitalization: do **not** add `[capitalize]` for Swedish — Swedish typography
wants lowercase mid-sentence references ("i avsnitt 2.1"); use `\Cref` for
sentence-initial ones.

## Overriding a shipped name: \AtBeginDocument, registered after cleveref's

cleveref's language option installs its names in an `\AtBeginDocument` hook.
A top-level `\crefname` in the preamble is therefore **silently overwritten**
when that hook runs. Override inside your own `\AtBeginDocument`, registered
*after* `\usepackage[...]{cleveref}`, so yours runs later and wins:

```latex
\usepackage[swedish]{cleveref}
\AtBeginDocument{%
  % cleveref's Swedish set hardcodes the appendix type as "Appendix", but
  % memoir and babel call it "Bilaga".
  \crefname{appendix}{bilaga}{bilagor}%
  \Crefname{appendix}{Bilaga}{Bilagor}%
}
```

(Combine with `\crefalias{chapter}{appendix}` after `\appendix` so appendix
chapters use the `appendix` type at all.)

## Match the printed name to the document's own terminology

cleveref's shipped names are generic; the surrounding prose may consistently
use a different word for the same referent. **When you `\cref` a type, check
that the name cleveref prints is the word the prose itself uses — if not,
override it.** A generic name that clashes with the document's terminology
reads as an inconsistency to the reader ("steg 5" in one sentence, "punkt 5"
in the next).

Worked example: a Swedish teaching text presents algorithms as enumerated
*steg* ("stegen utförs i tur och ordning…") and cross-references individual
steps ("Repetera \cref{mjöl,vispa-mjöl}"). cleveref's Swedish default for
`enumi` is "punkt", so the reference would render "Repetera punkt 5 och 6" —
clashing with the prose. Override in the same `\AtBeginDocument` hook:

```latex
\AtBeginDocument{%
  % The only \cref'd list items in this document are algorithm steps; the
  % prose consistently calls them "steg", not cleveref's default "punkt".
  \crefname{enumi}{steg}{steg}%
  \Crefname{enumi}{Steg}{Steg}%
}
```

Now "Repetera \cref{mjöl,vispa-mjöl}" renders "Repetera steg 5 och 6", and a
bare hand-written "Repetera 5 och 6" (no type word at all) is avoided too.

The override is per-type and document-wide, so it is only safe when every
`\cref`'d instance of that type is the same kind of thing (here: all
referenced `enumi` items are algorithm steps). If one document mixes kinds,
prefer a dedicated counter/type for one of them instead of renaming the
shared type.

## Verifying

Render and read the actual output (`pdftotext -layout`), grepping for the
reference sites: the type word, number, and conjunctions ("steg 5 och 6",
"avsnitt A.1") should match the prose's language and terminology. English
"Section"/"Appendix" or a clashing type word in an otherwise-localized
document means one of the rules above was missed.
