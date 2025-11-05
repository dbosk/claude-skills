---
name: skill-management
description: "IMPORTANT: Activate this skill BEFORE modifying any skill in ~/.claude/skills/. Guide for creating, updating, and maintaining Claude Code skills following best practices. Use proactively when: (1) creating a new skill, (2) modifying an existing skill in ~/.claude/skills/, (3) user requests to create, improve, update, review, or refactor a skill, (4) discussing skill quality or effectiveness. Always commit skill changes to the skills git repository after making modifications."
---

# Skill Management

**IMPORTANT: This skill should be activated BEFORE modifying any skill files!**

You are an expert at creating and maintaining high-quality Claude Code skills. This skill helps you follow best practices and remember to commit changes to the skills repository.

## When to Use This Skill (Read This First!)

### ✅ CORRECT Workflow

**ALWAYS activate this skill FIRST when:**
1. Creating a new skill in `~/.claude/skills/`
2. Editing any existing SKILL.md file
3. Modifying skill-related files (EXAMPLES.md, REFERENCE.md, scripts, etc.)
4. User requests to create, improve, update, review, or refactor a skill
5. Discussing skill quality or effectiveness

**The correct order is:**
```
1. User asks to modify a skill (or you identify need to update one)
2. YOU ACTIVATE THIS SKILL IMMEDIATELY
3. You review best practices and quality checklist
4. You make changes following the guidelines
5. You commit changes to the skills git repository
```

### ❌ INCORRECT Workflow (Anti-pattern)

**NEVER do this:**
```
1. User asks to modify a skill
2. You directly edit the SKILL.md file
3. You commit the changes
4. Later realize you didn't follow best practices
5. You have to redo the changes
```

### Examples of When to Activate

✅ "Can you update the literate-programming skill to be more emphatic?"
   → ACTIVATE THIS SKILL IMMEDIATELY, then plan changes

✅ "Create a new skill for handling API documentation"
   → ACTIVATE THIS SKILL IMMEDIATELY, then design skill

✅ "The code-review skill isn't triggering when it should"
   → ACTIVATE THIS SKILL IMMEDIATELY to review triggers

✅ Any task involving files in ~/.claude/skills/
   → ACTIVATE THIS SKILL IMMEDIATELY

### Remember

- Skills have specific quality requirements and best practices
- Following the checklist prevents having to redo work
- Git commits are REQUIRED after any skill modification
- Skill quality directly affects Claude Code effectiveness

## Original "When to Use" Section

Invoke this skill proactively when:

1. **Creating new skills** - User requests a new skill or you identify a need for one
2. **Modifying existing skills** - Any edit to SKILL.md or related files in `~/.claude/skills/`
3. **Reviewing skills** - User asks to review, improve, or refactor a skill
4. **Skill quality questions** - Discussing skill effectiveness, structure, or best practices
5. **After skill changes** - To verify git commit was performed

## Core Principles (from Claude Code Documentation)

### 1. Conciseness
- Assume Claude is already intelligent
- Only include context Claude doesn't already possess
- Challenge each piece of information for necessity
- Keep SKILL.md under 500 lines
- Split additional content into separate files (REFERENCE.md, EXAMPLES.md, etc.)

### 2. Degrees of Freedom
Match instruction specificity to task fragility:
- **High freedom** (text instructions): Multiple valid approaches exist
- **Medium freedom** (pseudocode/patterns): Preferred patterns with acceptable variation
- **Low freedom** (specific scripts): Operations are fragile, exact sequences required

### 3. Progressive Disclosure
Use referenced files to load content on-demand:
- Keep direct references one level deep from SKILL.md
- Use separate reference files for different domains/features
- Structure long references with table of contents

## Skill Structure Requirements

### YAML Frontmatter (Required)

```yaml
---
name: skill-name-here
description: What this skill does and when to use it. Max 1024 characters.
---
```

**Name requirements:**
- Maximum 64 characters
- Lowercase letters, numbers, and hyphens only
- No reserved words ("anthropic", "claude")

**Description requirements:**
- Maximum 1024 characters
- Non-empty, no XML tags
- Use third-person perspective
- State BOTH what the skill does AND when to use it
- Include specific trigger terms and contexts
- Be explicit about proactive invocation if applicable
- Avoid vague language ("helps with documents")

### Effective Description Pattern

```yaml
description: [What it does]. Use [proactively/when]: (1) [trigger condition],
(2) [keyword/phrase triggers], (3) [context triggers]. [Special instructions].
```

Example:
```yaml
description: Write and analyze literate programs using noweb. Use proactively
when: (1) creating, editing, or reviewing .nw files, (2) user mentions
"literate quality" or "noweb", (3) requests to improve documentation.
This skill should be invoked BEFORE making changes to .nw files.
```

## Three-Level Loading Architecture

**Level 1 - Metadata** (~100 tokens, always loaded):
- YAML frontmatter for discovery

**Level 2 - Instructions** (<5k tokens, loaded when triggered):
- Main SKILL.md body with procedures and best practices

**Level 3 - Resources** (unlimited, accessed as needed):
- Additional files: REFERENCE.md, EXAMPLES.md, FORMS.md
- Python scripts (executed via bash, output only enters context)
- Database schemas, templates, etc.

## Content Guidelines

### Organization Patterns

**Templates**: Provide strict format for critical outputs, flexible guidance for context-dependent work

**Examples**: Show input/output pairs demonstrating desired style and detail level

**Workflows**: Break complex operations into clear sequential steps with checklists

**Feedback loops**: Implement validate-fix-repeat cycles for quality-critical tasks

### Writing Guidelines

- **Avoid time-sensitive information** or use "Old Patterns" sections with details tags
- **Maintain consistent terminology** - select one term and use exclusively
- **Use forward slashes** in all paths (never Windows-style backslashes)
- **Provide defaults** for all options rather than excessive choices
- **Justify configuration parameters** - no "magic numbers"
- **Include error handling** in scripts with helpful messages
- **List required packages** and verify availability

### Anti-Patterns to Avoid

- Windows-style paths
- Excessive options without defaults
- Deeply nested file references (keep to one level)
- Assuming tools are pre-installed
- Time-sensitive information without caveats
- Vague activation language
- Loading everything upfront instead of progressive disclosure

## Skill Quality Checklist

Before considering a skill complete, verify:

### Core Requirements
- [ ] YAML frontmatter with valid `name` and `description`
- [ ] Description includes both "what" and "when"
- [ ] Description lists specific trigger terms/phrases
- [ ] Main content under 500 lines
- [ ] Appropriate file structure (separate REFERENCE.md, etc. if needed)

### Content Quality
- [ ] Only includes information Claude doesn't already know
- [ ] Consistent terminology throughout
- [ ] Forward slashes in all paths
- [ ] Defaults provided for all options
- [ ] Configuration parameters justified
- [ ] Error handling in any scripts
- [ ] No time-sensitive information (or clearly marked)

### Architecture
- [ ] Progressive disclosure used (not loading everything upfront)
- [ ] Referenced files kept one level deep from SKILL.md
- [ ] Long references have table of contents
- [ ] Scripts solve problems rather than punting to Claude

### Testing
- [ ] At least three test scenarios created
- [ ] Tested with real-world usage patterns
- [ ] Verified skill actually gets invoked when intended
- [ ] Works across target models (if applicable)

### Git Management
- [ ] Changes committed to skills repository
- [ ] Commit message describes what changed and why
- [ ] Working directory clean after commit

## Workflow for Creating/Updating Skills

### Creating a New Skill

1. **Identify the need**: What problem does this skill solve?
2. **Create directory**: `mkdir -p ~/.claude/skills/skill-name`
3. **Draft SKILL.md** with frontmatter:
   - Write clear description with triggers
   - Focus on what Claude doesn't already know
   - Include examples and workflows
   - Keep under 500 lines
4. **Test the skill**: Create test scenarios and verify invocation
5. **Refine based on testing**: Adjust triggers and content
6. **Commit to repository**:
   ```bash
   cd ~/.claude/skills
   git add skill-name/
   git commit -m "Add [skill-name] skill: [brief description]"
   ```

### Updating an Existing Skill

1. **Read current skill**: Review SKILL.md and related files
2. **Identify improvements**: Based on usage patterns or new requirements
3. **Make focused changes**: Edit specific sections, maintain structure
4. **Verify quality checklist**: Ensure still meets all criteria
5. **Test changes**: Verify skill still triggers correctly
6. **Commit to repository**:
   ```bash
   cd ~/.claude/skills
   git add [skill-directory]/
   git commit -m "Improve [skill-name]: [specific changes made]"
   ```

## Git Repository Management

**CRITICAL**: Skills are version-controlled in a git repository at `~/.claude/skills/`.

### After ANY skill modification:

1. Navigate to skills directory: `cd ~/.claude/skills`
2. Check status: `git status`
3. Add changes: `git add [skill-directory]/`
4. Commit with descriptive message:
   ```bash
   git commit -m "Action [skill-name]: brief description

   Detailed explanation of changes and rationale.

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```
5. Verify clean state: `git status`

### Common Git Commands

```bash
# Check current status
git status

# See what changed
git diff [file]

# Add specific skill
git add skill-name/

# Commit with message
git commit -m "message"

# View recent commits
git log --oneline -5

# Push changes (if using remote)
git push
```

## Examples

### Example 1: Good Description

```yaml
description: Generate AWS CloudFormation templates following best practices.
Use when: (1) user mentions "CloudFormation", "CFN", or "AWS IaC", (2) creating
infrastructure as code for AWS, (3) user requests template generation or
validation. Includes security best practices, cost optimization patterns, and
common resource configurations.
```

Why it's good:
- States what it does clearly
- Lists specific triggers
- Mentions key features
- Appropriate length

### Example 2: Poor Description

```yaml
description: Helps with cloud stuff.
```

Why it's bad:
- Vague "helps with"
- No specific triggers
- No indication of when to use
- Doesn't specify which cloud or what operations

### Example 3: Effective Skill Structure

```
skill-name/
├── SKILL.md              # Main instructions (<500 lines)
├── EXAMPLES.md           # Detailed examples
├── REFERENCE.md          # API references, schemas
└── scripts/
    └── validate.py       # Utility scripts
```

SKILL.md references other files only when needed, implementing progressive disclosure.

## Special Considerations

### Testing New Skills

After creating a skill, test it by:
1. Asking a question that should trigger it
2. Checking if Claude invokes the skill
3. Verifying the skill provides value
4. Adjusting triggers if not invoked when expected

### Refining Triggers

If a skill isn't being invoked when it should:
- Add more specific trigger phrases to description
- Use "proactively when" language
- List explicit keywords and contexts
- Consider if scope is too narrow or too broad

### Documentation References

For the most current best practices, reference:
- Claude Code Skills Best Practices: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- Agent Skills Overview: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- Skills Quickstart: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/quickstart

## Reminder

**DO NOT FORGET**: After making any changes to skills in `~/.claude/skills/`, you MUST commit them to the git repository. This ensures changes are tracked and can be shared/synced. The skills directory is version-controlled specifically for this purpose.
