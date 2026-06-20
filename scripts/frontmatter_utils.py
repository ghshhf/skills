"""Shared frontmatter parser using yaml.safe_load()."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """
    Parse YAML frontmatter from a markdown file.

    This is a drop-in replacement for the old regex-based parse_frontmatter.
    Uses yaml.safe_load() to correctly handle:
      - Values containing colons (e.g., URLs like https://example.com:8080/path)
      - Multiline YAML values (using | or >)
      - Empty or missing frontmatter

    Returns:
        dict: metadata dict (empty dict if no frontmatter found)
    """
    match = FRONTMATTER_RE.search(text)
    if not match:
        return {}

    frontmatter_raw = match.group(1)
    # body is available via text[match.end():] if needed

    try:
        metadata = yaml.safe_load(frontmatter_raw)
        if metadata is None:
            return {}
        if not isinstance(metadata, dict):
            return {}
        return metadata
    except yaml.YAMLError as e:
        print(f"Warning: Failed to parse frontmatter: {e}")
        return {}


def load_skill_frontmatter(skill_md_path: Path) -> dict:
    """Load and parse frontmatter from a SKILL.md file."""
    text = skill_md_path.read_text(encoding="utf-8")
    return parse_frontmatter(text)
