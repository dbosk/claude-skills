#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import sys
import os
import re
from pathlib import Path

import yaml

def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)
    
    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"
    
    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"
    
    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"
    
    frontmatter = match.group(1)

    # Parse the frontmatter strictly. A frontmatter that is not valid YAML
    # may still look fine to the eye, but the description is then lost: in
    # a plain multi-line value, " #" starts a comment and ends the value,
    # and ": " is a mapping indicator. Claude Code then shows the skill's
    # heading instead of its description, so its triggers never fire.
    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as e:
        first = str(e).splitlines()[0]
        return False, (f"Frontmatter is not valid YAML ({first}); write the "
                       "description as a block scalar ('description: >-' "
                       "with the text indented on the following lines)")
    if not isinstance(data, dict):
        return False, "Frontmatter is not a YAML mapping"

    # Check required fields
    if not data.get('name'):
        return False, "Missing 'name' in frontmatter"
    if not data.get('description'):
        return False, "Missing 'description' in frontmatter"

    name = str(data['name']).strip()
    # Check naming convention (hyphen-case: lowercase with hyphens)
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"
    if name.startswith('-') or name.endswith('-') or '--' in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > 64:
        return False, f"Name '{name}' is longer than 64 characters"

    description = str(data['description']).strip()
    if '<' in description or '>' in description:
        return False, "Description cannot contain angle brackets (< or >)"
    if len(description) > 1024:
        return False, f"Description is {len(description)} characters; the limit is 1024"

    return True, "Skill is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)