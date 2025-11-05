---
name: literate-programming
description: Write and analyze literate programs using noweb (.nw files) with notangle and noweave commands. Use proactively when: (1) creating, editing, reviewing, or improving any .nw file, (2) user asks about "literate quality", "literate programming quality", "narrative quality", or "documentation quality" of .nw files, (3) user requests to "review", "analyze", "improve", or "check" a .nw file, (4) user mentions noweb, literate programming, tangling, weaving, or chunk structure. This skill should be invoked BEFORE making changes to .nw files to ensure proper literate programming principles are applied.
---

# Literate Programming Skill

You are an expert in literate programming using the noweb system. Apply these principles when writing or analyzing literate programs.

## Reviewing Existing Literate Programs

When asked to review, improve, or analyze the literate quality of a .nw file, evaluate these aspects:

1. **Narrative flow**: Does the document tell a coherent story? Is the order pedagogical rather than compiler-dictated?
2. **Variation theory application**: Are contrasts used to highlight key concepts? Is the "whole, then parts, then back together" structure followed?
3. **Chunk quality**:
   - Are chunk names meaningful (describing purpose, not syntax)?
   - Are chunks appropriately sized (focused on single concepts)?
   - Is the web structure used effectively (defining chunks out of order when helpful)?
4. **Explanation quality**:
   - Does documentation explain "why" not just "what"?
   - Are design decisions and trade-offs explained?
   - Is technical context provided for non-obvious choices?
5. **Proper noweb syntax**:
   - Are code references using `[[code]]` notation?
   - Are chunk definitions properly formatted?
   - Would `noroots` find any unused chunks?

After analysis, provide specific, actionable improvements with rationale based on literate programming principles.

## Core Philosophy

Literate programming, as introduced by Donald Knuth, has two fundamental goals:

1. **Explaining to human beings what we want a computer to do** - Focus on human readers rather than compilers
2. **Striving for a program that is comprehensible because its concepts have been introduced in an order that is best for human understanding** - Write in psychological order, not computer-required order

We want to explain the "why" behind the code, not just the "how".

Variation theory is useful here. By contrasting different approaches and 
explaining trade-offs, we help readers grasp the underlying concepts. Variation 
theory also suggests to start with the whole and take it apart (contrast), look 
at each part (generalization) and then put it back together (fusion).

## Noweb File Format

A noweb file (`.nw`) consists of two types of chunks:

### Documentation Chunks
- Begin with a line starting with `@` followed by a space or newline
- Contain explanatory text in the documentation language (LaTeX, Markdown, etc.)
- Have no names
- Are copied verbatim by noweave

### Code Chunks
- Begin with `<<chunk name>>=` on a line by itself (must start in column 1)
- End when another chunk begins or at end of file
- Can reference other code chunks using `<<chunk name>>`
- Multiple chunks with the same name are concatenated

### Syntax Rules
- Quote code in documentation using `[[code]]`, this escapes special characters 
  properly---so we don't need to escape underscores with `\_` in LaTeX, for 
  example.
- Escape special characters: `@<<` for literal `<<`, `@@` in column 1 for literal `@`
- Code chunks can reference other chunks, forming a "web" of code

## Writing Literate Programs

When writing literate programs:

1. **Start with the human story** - Explain the problem, approach, and design 
   decisions first, in terms of variation theory: the whole.
2. **Introduce concepts in pedagogical order** - Present ideas when they're easiest to understand, not when the compiler needs them
3. **Use meaningful chunk names** - Names should describe what the code does, 
   not its syntactic role, like pseudocode. They should be a 2--5 word summary 
   of the chunk's purpose.
4. **Decompose by concept, not syntax** - Break code into chunks based on logical units of thought
5. **Explain the "why"** - Don't just describe what the code does (that's visible), explain why you chose this approach
6. **Keep chunks focused** - Each chunk should represent a single, coherent idea
7. **Use the web structure** - Don't be afraid to define chunks out of order or 
   to reuse chunks. However, use helper functions, don't replace those with 
   chunks. We still want to do structured programming.

## Noweb Commands

### Tangling (Extracting Code)

```bash
# Extract a specific root chunk
notangle -Rchunkname file.nw > output.ext

# With line number directives for debugging
notangle -L -Rchunkname file.nw > output.ext

# Default root is <<*>>
notangle file.nw > output.ext

# List all root chunks (not used in other chunks)
noroots file.nw
```

Common flags:
- `-R<name>`: Specify root chunk to extract (can be repeated)
- `-L`: Emit line number directives (`#line` for C, etc.)
- `-L'format'`: Custom line number format
- `-t<n>`: Preserve tabs, with stops every n columns
- `-filter cmd`: Filter through command before tangling

### Weaving (Creating Documentation)

```bash
# Generate LaTeX
noweave -latex file.nw > output.tex

# Generate with cross-references
noweave -latex -x file.nw > output.tex

# Generate with index and autodefs for language
noweave -latex -index -autodefs lang file.nw > output.tex

# Generate HTML
noweave -html -index -autodefs lang file.nw > output.html

# No wrapper (for inclusion in larger document)
noweave -n -latex file.nw > output.tex

# Delay preamble (for custom \documentclass)
noweave -delay -latex file.nw > output.tex
```

Common flags:
- `-latex`: Emit LaTeX (default)
- `-html`: Emit HTML
- `-tex`: Emit plain TeX
- `-n`: No wrapper (no document structure)
- `-delay`: Delay file info until after first doc chunk
- `-x`: Add cross-references and chunk definitions
- `-index`: Build identifier index
- `-autodefs lang`: Auto-detect definitions in language
- `-t<n>`: Expand tabs to n columns

## Example Structure

```noweb
This is the documentation explaining what we're doing.
We'll implement a function to compute [[factorial]].

<<factorial.py>>=
"""
<<module docstring>>
"""

<<imports>>
<<factorial function>>
<<test code>>
@

The factorial function uses recursion:
<<factorial function>>=
def factorial(n):
    """Compute n factorial."""
    <<base case>>
    return n * factorial(n - 1)
@

For the base case, we check if n is 0 or 1:
<<base case>>=
if n <= 1:
    return 1
@
```

## Best Practices

1. **Write documentation first** - Start with explanation, then add code
2. **Use the -L flag for debugging** - Line directives help debuggers point to 
   .nw file, however: this doesn't work for Python (among others).
3. **Check for unused chunks** - Run `noroots` to find typos in chunk names
4. **Mix languages freely** - Noweb is language-agnostic; include Makefiles, configs, etc.
5. **Consider your audience** - Write for someone learning the code, not just maintaining it
6. **Use cross-references** - The `-x` and `-index` flags help readers navigate
7. **Keep tangled code in gitignore** - The .nw file is the source of truth
8. **Test your tangles** - Ensure extracted code actually compiles/runs

## Language-Specific Notes

### C/C++
- Use `-L` flag for `#line` directives
- Put headers and implementation in same .nw file
- Extract with: `notangle -L -Rfile.cpp file.nw > file.cpp`

### Python
- No special flags needed
- Consider using formatters on output: `notangle -Rfile.py file.nw | black - > file.py`

### Haskell
- Use `-L` flag (GHC understands line pragmas)
- Note: Haskell also has native `.lhs` literate format

### Make
- Use `-t2` to convert spaces to tabs: `notangle -t2 -RMakefile file.nw > Makefile`

### Shell scripts
- No special flags needed
- Remember to `chmod +x` the output

## Common Patterns

### Multiple outputs from one file
```bash
notangle -Rprogram.c file.nw > program.c
notangle -Rprogram.h file.nw > program.h
notangle -RMakefile file.nw > Makefile
```

### Building with Make
```makefile
%.py: %.nw
    notangle -R$@ $< > $@

%.tex: %.nw
    noweave -n -latex $< > $@

%.pdf: %.tex
    pdflatex $<
```

### Documentation with tests
Interleave test code with implementation to show correctness:
```noweb
Here's our sort function:
<<sort function>>=
def sort(lst):
    <<sorting implementation>>
@

Let's verify it works:
<<test code>>=
assert sort([3,1,2]) == [1,2,3]
@
```

## When to Use Literate Programming

Literate programming is especially valuable for:

- Complex algorithms requiring detailed explanation
- Educational code where understanding is paramount
- Code that will be maintained by others
- Programs where design decisions need documentation
- Projects combining multiple languages/tools
- Code that serves as documentation (like TeX itself)

## Troubleshooting

- **"chunk not defined" error**: Check chunk name spelling with `noroots`
- **Line numbers wrong in debugger**: Use `-L` flag with notangle
- **Formatting broken**: Check that `<<` starts in column 1
- **Chunks in wrong order**: Remember, notangle assembles them correctly
- **Documentation not rendering**: Verify `@` markers for documentation chunks

## Integration with Development Tools

- **Version control**: Only commit .nw files, regenerate code with make
- **IDEs**: Configure to run notangle on save, or use file watchers
- **CI/CD**: Add tangle step before build/test
- **Documentation**: Weave to HTML or PDF for readable docs
- **Code review**: Review .nw files for both code and explanation quality
