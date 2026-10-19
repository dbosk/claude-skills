# Canvas pages, assignments and quizzes of a course, kept as files here.
#
# Layout: NN-<module>/<page>.md and NN-<module>/assignments/<assignment>.md;
# a *.html.md file has an HTML body (pushed with --html).  The front matter
# is canvaslms's: `regex` identifies the item (assignments by Canvas id),
# `modules:` is authoritative for module membership and position.
#
# The files are the source of truth.  Canvas strips HTML comments, so a pull
# would lose them: `make pull` only exports items that have no file yet, and
# `make diff-canvas` shows what changed in Canvas (for instance edits in the
# web editor) so they can be carried into the files by hand.
#
# Push to another round:  make push COURSE=<next round>
# Rehearse in the sandbox: make push CANVAS_COURSE='^Sandbox dbosk$$'

COURSE?=		$(error set COURSE, e.g. COURSE=vetcyb26h)
CANVAS_COURSE?=		^${COURSE}$$

CANVASLMS?=		canvaslms --no-cache
CANVAS_PY?=		$(shell head -1 "$$(readlink -f "$$(command -v canvaslms)")" \
			  | sed 's/^\#!//')
EXPORT?=		${CANVAS_PY} -I bin/canvas_export.py

ASSIGNMENTS:=		$(wildcard */assignments/*.md)
PAGES:=			$(filter-out ${ASSIGNMENTS},$(wildcard */*.md))
# Quizzes are `canvaslms quizzes export -I` JSON; a push sends the settings
# and the description as HTML, never the questions (no --replace-items).
QUIZZES:=		$(wildcard */quizzes/*.json)

STAMPDIR:=		.pushed.d/$(shell printf '%s' '${CANVAS_COURSE}' \
			  | tr -c 'A-Za-z0-9' _)

.PHONY: push push-pages push-assignments push-quizzes
push: push-pages push-assignments push-quizzes
push-pages: $(addprefix ${STAMPDIR}/,${PAGES})
push-assignments: $(addprefix ${STAMPDIR}/,${ASSIGNMENTS})
push-quizzes: $(addprefix ${STAMPDIR}/,${QUIZZES})

${STAMPDIR}/%.json: %.json
	@mkdir -p $(dir $@)
	${CANVASLMS} quizzes edit -c "${CANVAS_COURSE}" --html -f "$<"
	@touch $@

${STAMPDIR}/%: %
	@mkdir -p $(dir $@)
	${CANVASLMS} $(if $(findstring /assignments/,$<),assignments,pages) \
	  edit -c "${CANVAS_COURSE}" $(if $(filter %.html.md,$<),--html) -f "$<"
	@touch $@

# Mark every file as pushed, e.g. right after an export, so that the next
# `make push` sends only what was edited since.
.PHONY: mark-pushed
mark-pushed:
	@for f in ${PAGES} ${ASSIGNMENTS} ${QUIZZES}; do \
	  mkdir -p "${STAMPDIR}/$$(dirname "$$f")"; touch "${STAMPDIR}/$$f"; \
	done

# The Canvas id of the course, which the export script needs.
COURSE_ID=		$$(canvaslms courses -a -i '${CANVAS_COURSE}' | cut -f1)

.PHONY: pull diff-canvas
pull:
	${EXPORT} "${COURSE_ID}" . | while read -r f; do \
	  echo "new: $$f"; mkdir -p "${STAMPDIR}/$$(dirname "$$f")"; \
	  touch "${STAMPDIR}/$$f"; \
	done

diff-canvas:
	@tmp=$$(mktemp -d) && ${EXPORT} "${COURSE_ID}" "$$tmp" >/dev/null && \
	  diff -ru -x bin -x quizzes -x '*.mk' -x Makefile -x .gitignore -x .pushed.d . "$$tmp"; \
	  rm -rf "$$tmp"
