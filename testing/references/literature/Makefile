# Typeset ../literature-review.md as a plain LaTeX article:
#
#   make            (needs pandoc, lualatex, biber and latexmk)
#
# article.lua turns the Markdown into an article (chapters numbered as the
# questions, \cite from testing-claims.bib); preamble.tex sets up biblatex.

REVIEW = ../literature-review.md
BUILD = build
DATE = Companion to the testing skill. Searched and read on 12 October 2026.

literature-review.pdf: ${REVIEW} article.lua preamble.tex testing-claims.bib
	mkdir -p ${BUILD}
	pandoc ${REVIEW} -s -o ${BUILD}/literature-review.tex \
	  --lua-filter=article.lua -H preamble.tex --toc -N \
	  -V secnumdepth=2 -V documentclass=article -V papersize=a4 \
	  -M date="${DATE}"
	cp testing-claims.bib ${BUILD}/
	cd ${BUILD} && latexmk -lualatex -interaction=nonstopmode -halt-on-error \
	  literature-review.tex
	cp ${BUILD}/literature-review.pdf $@

.PHONY: clean
clean:
	${RM} -r ${BUILD} literature-review.pdf
