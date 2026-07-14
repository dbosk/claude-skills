# LaTeX patterns for questions, hypotheses and contributions

Worked out in the vt-debug paper (companion: vt-prog-misconceptions);
assumes the didactic package and the dual article/slides setup of
latex-writing's `references/dual-beamer-article.md` (which documents the
restatable environments and the beamer shim — read that first).

## Environments: three, separately numbered

- `question` — substantive research questions (didactic provides it).
- `mquestion` — methodological research questions, own counter.
- `hypothesis` — predicted answers, own counter.

`hypothesis` and `mquestion` are declared in the paper's preamble via
didactic's `\ProvideSemanticEnv`; the translations must be declared
first:

```latex
\DeclareTranslation{English}{Hypothesis}{Hypothesis}
\DeclareTranslation{English}{hypothesis}{hypothesis}
\DeclareTranslation{English}{hypotheses}{hypotheses}
\DeclareTranslation{English}{Hypotheses}{Hypotheses}
\ProvideSemanticEnv{hypothesis}[block]{Hypothesis}
  {hypothesis}{hypotheses}{Hypothesis}{Hypotheses}

\DeclareTranslation{English}{Methodological question}{Methodological question}
\DeclareTranslation{English}{methodological question}{methodological question}
\DeclareTranslation{English}{methodological questions}{methodological questions}
\DeclareTranslation{English}{Methodological questions}{Methodological questions}
\ProvideSemanticEnv{mquestion}[orangeblock]{Methodological question}
  {methodological question}{methodological questions}
  {Methodological question}{Methodological questions}
```

The optional bracket argument is the beamer block type; in the article
each becomes a `\declaretheorem` with its own counter, so methodological
questions number 1, 2, … independently of the substantive ones.

## Statement and restatement

First statement, wrapped restatable (inside a frame so the slides show
it too):

```latex
\begin{restatable}{mquestion}{mqcoding}\label{mq:coding}
  Do the patterns coded from the recorded edit--run cycles correspond
  to the patterns in the debugger's reasoning?
\end{restatable}
```

Restatements (`\mqcoding*` — keeps the original number) go in exactly
two places:

1. **Method overview**, followed immediately by *how* it is answered:
   which instrument/data (`\cref` the data-collection subsection), which
   test, and — for substantive questions — `Answered by testing
   \cref{h:...}:` followed by the hypothesis restatement.
2. **Conclusions**, followed immediately by the answer as far as the
   findings allow (or by what exactly is pending).

Verify counts after building: each statement appears exactly the
expected number of times with the same number
(`pdftotext file.pdf - | grep -oE "(Question|Methodological question|Hypothesis) [0-9]+\." | sort | uniq -c`).

## The contributions list

At the end of the introduction, after the questions:

```latex
\subsection{Contributions}

Summarising the above, this paper contributes the following; each
contribution is held to account by a research question.
\begin{itemize}
  \item A ... (\cref{...}); \cref{rq:...} tests it.
  \item A method for ... , validated against ... (\cref{mq:...}).
\end{itemize}
```

Rules:

- One question per contribution; name it with `\cref` in the item.
- Methodological contributions (instruments, coding schemes,
  triangulations) cite methodological questions; substantive ones cite
  substantive questions.
- Keep a slides-only frame with the contributions as short bullets.
