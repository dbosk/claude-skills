-- Turn literature-review.md into a plain LaTeX article:
-- H1 -> title; "## N. Question" -> \section{Question} (LaTeX numbers it);
-- <a id> anchors -> header identifiers; [Author Year](#ref-KEY) -> \cite{KEY};
-- the hand-written reference list -> \printbibliography; bold lead-ins of
-- top-level paragraphs -> \paragraph; links to local files -> plain text;
-- table column widths from the average cell length.

local stringify = pandoc.utils.stringify

local function latex(inlines)
  return pandoc.write(pandoc.Pandoc({ pandoc.Plain(inlines) }), "latex")
end

-- inline code that may break at spaces (\texttt{a\ b} cannot)
function Code(el)
  if not el.text:match("%s") and #el.text > 25 and not el.text:match("[%%#{}\\]") then
    return pandoc.RawInline("latex", "\\nolinkurl{" .. el.text .. "}")
  end
  local words = pandoc.Inlines({})
  for word in el.text:gmatch("%S+") do
    if #words > 0 then words:insert(pandoc.Space()) end
    words:insert(pandoc.Str(word))
  end
  return pandoc.RawInline("latex", "\\texttt{" .. latex(words) .. "}")
end

-- the hit-count tables' widest header; the text calls it "the union column"
function Str(el)
  if el.text == "IEEE+OA+arXiv" then return pandoc.Str("Union") end
end

function Link(el)
  local key = el.target:match("^#ref%-(.+)$")
  if key then
    return pandoc.RawInline("latex", "\\cite{" .. key .. "}")
  end
  if not el.target:match("^#") and not el.target:match("^https?:") then
    return el.content -- a file in the repository: no use in a PDF
  end
end

local function widths(tbl)
  local ncol = #tbl.colspecs
  -- pandoc gives no widths when the source lines are short; keep that
  -- unless some row is too long for a line anyway
  local any = false
  for _, cs in ipairs(tbl.colspecs) do
    if type(cs[2]) == "number" then any = true end
  end
  if not any then
    local longest = 0
    for _, body in ipairs(tbl.bodies) do
      for _, row in ipairs(body.body) do
        local n = 0
        for _, cell in ipairs(row.cells) do n = n + #stringify(cell.contents) end
        longest = math.max(longest, n)
      end
    end
    if longest < 70 then return tbl end
  end
  local total, count = {}, 0
  for i = 1, ncol do total[i] = 0 end
  local word = {}
  for i = 1, ncol do word[i] = 0 end
  local function add(row)
    for i, cell in ipairs(row.cells) do
      if i <= ncol then
        local text = stringify(cell.contents)
        total[i] = total[i] + #text
        -- TeX may break after a hyphen, so hyphenated parts count apart
        for w in text:gmatch("[^%s%-]+%-?") do word[i] = math.max(word[i], #w) end
      end
    end
  end
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do add(row); count = count + 1 end
  end
  for _, row in ipairs(tbl.head.rows) do add(row) end
  -- each column first gets room for its longest word, then the rest of
  -- the line is shared by how much text the column holds beyond that
  local LINE = 75 -- characters per line of a 10pt article
  local min, extra, msum, esum = {}, {}, 0, 0
  for i = 1, ncol do
    min[i] = (word[i] + 2) / LINE
    extra[i] = math.max(total[i] / math.max(count, 1) - word[i], 0)
    msum, esum = msum + min[i], esum + extra[i]
  end
  for i = 1, ncol do
    local share = msum >= 1 and min[i] / msum
      or min[i] + (1 - msum) * (esum > 0 and extra[i] / esum or 1 / ncol)
    tbl.colspecs[i] = { tbl.colspecs[i][1], share }
  end
  return tbl
end

function Pandoc(doc)
  local out, pending, skip = {}, nil, false
  before_chapters = true
  for _, b in ipairs(doc.blocks) do
    local keep = true
    local raw = (b.t == "RawBlock" and b.format == "html" and b.text)
      or (b.t == "Para" and #b.content == 2 and b.content[1].t == "RawInline"
          and b.content[2].t == "RawInline"
          and b.content[1].text .. b.content[2].text)
    local id = raw and raw:match('^<a id="([^"]+)"></a>%s*$')
    if id then
      pending = id; keep = false
    elseif b.t == "Header" then
      if b.level == 1 then
        doc.meta.title = b.content
        keep = false
      else
        b.level = b.level - 1
        local c = b.content
        if c[1] and c[1].t == "Str" and c[1].text:match("^%d+%.$") then
          c:remove(1)
          if c[1] and c[1].t == "Space" then c:remove(1) end
        end
        if pending then b.identifier = pending; pending = nil end
        if b.level == 1 and not b.identifier:match("^ch%-") then
          before_chapters = before_chapters and true
        elseif b.level == 1 then
          before_chapters = false
        end
        if before_chapters then b.classes:insert("unnumbered") end
        if b.level == 1 and stringify(b) == "References" then
          skip = true
          table.insert(out, pandoc.RawBlock("latex", "\\printbibliography"))
          keep = false
        end
      end
    elseif b.t == "Para" and b.content[1] and b.content[1].t == "Strong"
        and stringify(b.content[1]):match("%.$") then
      local lead = b.content:remove(1)
      if b.content[1] and b.content[1].t == "Space" then b.content:remove(1) end
      b.content:insert(1, pandoc.RawInline("latex",
        "\\paragraph{" .. latex(lead.content) .. "} "))
    elseif b.t == "Para" and #out == 0 and b.content[1] and b.content[1].t == "Emph" then
      keep = false -- the "Searched and read on ..." line: goes into \date
    end
    if b.t == "Table" then b = widths(b) end
    if keep and not skip then table.insert(out, b) end
  end
  doc.blocks = out
  return doc
end

return {
  { Link = Link, Code = Code, Str = Str },
  { Pandoc = Pandoc },
}
