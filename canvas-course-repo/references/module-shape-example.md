# Worked example: applying a week-module shape

From a course where the author hand-arranged one module and asked for five
more "like that". The shape, written in the course's `CLAUDE.md`:

1. Page `Veckoöversikt: <week>`
2. Page `Föreläsning: <week>`
3. lecture notes (LTI, author-made), or the text header
   `Föreläsningsanteckningar kommer`
4. `<Deck> (videoföreläsning)` per deck that has a video (LTI)
5. Page `Övning: <week>`
6. tutorial notes, or the text header `Övningsanteckningar kommer`
7. `Laboration (N) …`

## 0. Read what the author did

```bash
canvaslms --no-cache modules view -c '^COURSE$' --show-position '^Model module$'
canvaslms --no-cache assignments list -c '^COURSE$' -a 'word from an old item'
canvaslms --no-cache assignments view -c '^COURSE$' -a '^Old item$' | sed -n 1,12p
```

The last two showed how the author had removed the old items: `published:
false`, `modules: []`, assignment kept. That became the detach rule. It also
showed that the two pages pushed earlier as `published: false` were now
published and one had moved, so their files were corrected first.

## 1. Inventory (and backup)

```bash
PY=$(head -1 "$(readlink -f "$(command -v canvaslms)")" | sed 's/^#!//')
$PY ~/.claude/skills/canvas-course-repo/scripts/canvas_snapshot.py \
    module 63874 'Klasser och objekt' > inventory-classes.json
```

The description lengths decided the method: the videos had empty
descriptions (front-matter-only file is safe), the old exercise assignments
had 3–6 kB (HTML round trip required).

## 2. Sandbox rehearsal

On an LTI assignment in the sandbox: snapshot, push, snapshot, `diff`,
restore, snapshot, `diff`. What it showed: `name` is required; the body is
always sent; `external_tool_tag_attributes` survive; `modules: []` detaches
and keeps the assignment; omitting `modules:` changes nothing.

## 3. Apply, top to bottom

```bash
# the two pages, unpublished, at positions 2 and 3
canvaslms --no-cache pages edit --create -c '^COURSE$' -f modules/classes/lecture.md
canvaslms --no-cache pages edit --create -c '^COURSE$' -f modules/classes/tutorial.md
```

Rename and place a video (front matter only, empty description):

```yaml
---
name: 'Klasser och objekt (videoföreläsning)'
regex: '^390257$'
modules:
  - module: '^Klasser och objekt$'
    position: 3
---
```

Detach an old assignment that has a description (`--html
--no-link-translation`, body is the `description` from the inventory):

```yaml
---
name: 'Fördjupande övning  klasser och objekt'
regex: '^390242$'
published: false
modules: []
---
<p>…the description HTML, verbatim…</p>
```

A video that sat in the wrong week's module moved by listing only the right
module in its `modules:`; the authoritative list removed it from the old one.

## 4. Audit and write back

```bash
canvaslms --no-cache modules view -c '^COURSE$' --show-position '^Klasser och objekt$'
```

Then the tutorial page's `position:` in the repository was set to where it
now sits, and the lecture page's prose was changed to the videos' new names.
Re-pushing one page and seeing `modules view` unchanged confirmed that the
files and Canvas agree.
