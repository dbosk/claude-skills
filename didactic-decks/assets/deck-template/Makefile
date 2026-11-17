# The unsuffixed PDFs are the course's main language.  A bilingual deck
# also has drivers for the other edition, notes-sv.tex and slides-sv.tex,
# and builds their PDFs too; a single-language deck deletes those two
# drivers, and the list below drops their PDFs by itself.
PDFS=		notes.pdf slides.pdf
PDFS+=		$(patsubst %.tex,%.pdf,$(wildcard notes-sv.tex slides-sv.tex))

.PHONY: all
all: ${PDFS}

LATEXFLAGS+=	-shell-escape
# The example programs' terminal sessions are run and embedded with
# PythonTeX (didactic's \runpython[transcript]), so code and output cannot
# drift apart.
TEX_PYTHONTEX=	yes
# The two jobs of an edition share an output directory, so the second
# job would otherwise reuse the first job's PythonTeX cache.
PYTHONTEXFLAGS=	--interpreter python:python3 --rerun=always

# The deck is a literate program: contents.nw is the single source.
# contents.tex is woven from it and the example programs are tangled from
# it (the examples/ directory is all generated files).  noweb.mk provides
# the weave (tominted, which finds its bundled Pygments lexer itself) and
# the tangle rules.

# noweb.mk knows tangle rules only for some suffixes; declare any others
# this deck uses before including it.  (default_tangling gives each of
# them empty NOTANGLEFLAGS, which is what a teaching example wants.)
# autolang infers the minted lexer from the chunk name.
# NOWEB_SUFFIXES+=	.s .js .lean

# Teaching examples must match the slides byte for byte: no #line
# directives in the tangled sources.  Add one line per compiled language
# the deck shows.
# NOTANGLEFLAGS.c=
# NOTANGLEFLAGS.cpp=
# NOTANGLEFLAGS.hs=

SRC+=		preamble.tex
SRC+=		abstract.tex contents.tex
SRC+=		sokprotokoll.tex
# The appendices \input the generated hit-list tables; a regenerated table
# must trigger a rebuild even when no .tex source changed.
SRC+=		$(wildcard litteratursokning/*-full.tex)
SRC+=		ltnotes.bib

# One line per tangled example program.  Recaps re-display these files
# with \inputminted, so they must be built before the PDFs.
EXAMPLES+=	examples/example.py

contents.tex: contents.nw

# The generic %.py: %.nw pattern does not match across the examples/
# directory boundary, so spell out one rule per suffix.
examples/%.py: contents.nw
	@mkdir -p ${@D}
	${NOTANGLE.py}

.PHONY: examples
examples: ${EXAMPLES}

# Each driver sets its edition and inputs the shared body.
notes.pdf notes-sv.pdf: notes-body.tex
slides.pdf slides-sv.pdf: slides-body.tex

# PythonTeX writes its outputs (pythontex_data.pkl, py_*.stdout) into the
# output directory under names that do not say which job made them, and
# the two editions run different programs under the same instance
# numbers.  In one shared ltxobj, a job that latexmk rebuilds without
# rerunning PythonTeX prints the other edition's transcripts, without an
# error.  So each edition has its own output directory; the two jobs of
# one edition share it, as the two jobs of a single-language deck do.
notes-sv.pdf slides-sv.pdf: TEX_OUTDIR=ltxobj-sv

${PDFS}: ${SRC} ${EXAMPLES}


.PHONY: clean
clean:
	${RM} notes.pdf slides.pdf notes-sv.pdf slides-sv.pdf
	${RM} -R ltxobj-sv
	${RM} contents.tex
	${RM} ${EXAMPLES}


# PROJECT: adjust the relative path to the shared makefiles submodule.
INCLUDE_MAKEFILES=../../../makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
include ${INCLUDE_MAKEFILES}/noweb.mk
