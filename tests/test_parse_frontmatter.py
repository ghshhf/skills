"""Tests for parse_frontmatter function from frontmatter_utils."""

import sys
from pathlib import Path

import pytest
import yaml

# Add scripts/ to path so we can import frontmatter_utils
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from frontmatter_utils import parse_frontmatter


class TestParseFrontmatter:
    """Test cases for YAML frontmatter parsing."""

    def test_simple_key_value(self):
        """Test basic key: value parsing."""
        text = "---\nname: test-skill\ndescription: A test skill\n---\nBody"
        result = parse_frontmatter(text)
        assert result == {
            "name": "test-skill",
            "description": "A test skill",
        }

    def test_value_with_colon(self):
        """Test that values containing colons are parsed correctly.

        Known P0 bug in old regex-based parser: values with ':' would be
        incorrectly split. This test verifies the yaml.safe_load() fix works.
        """
        text = "---\nname: test-skill\nurl: https://example.com:8080/path\n---\nBody"
        result = parse_frontmatter(text)
        assert result.get("url") == "https://example.com:8080/path"

    def test_value_with_multiple_colons(self):
        """Test complex values with multiple colons (valid YAML: quoted)."""
        text = '---\ndescription: "Fix bug in parser: see issue #123: urgent"\n---\nBody'
        result = parse_frontmatter(text)
        assert result.get("description") == "Fix bug in parser: see issue #123: urgent"

    def test_multiline_value_pipe(self):
        """Test multiline YAML values using | (literal block)."""
        text = "---\nname: test-skill\ndescription: |\n  This is a\n  multiline description\n---\nBody"
        result = parse_frontmatter(text)
        assert "multiline" in result.get("description", "")

    def test_multiline_value_gt(self):
        """Test multiline YAML values using > (folded block)."""
        text = "---\nname: test-skill\ndescription: >\n  This is a\n  folded description\n---\nBody"
        result = parse_frontmatter(text)
        assert "folded" in result.get("description", "") or "This is a" in result.get("description", "")

    def test_empty_frontmatter(self):
        """Test empty or missing frontmatter."""
        text = "No frontmatter here"
        result = parse_frontmatter(text)
        assert result == {}

    def test_frontmatter_only_dashes(self):
        """Test frontmatter with only dash markers but no content."""
        text = "---\n---\nBody"
        result = parse_frontmatter(text)
        # yaml.safe_load("") returns None, which frontmatter_utils handles
        assert result == {}

    def test_all_skill_frontmatter_files(self):
        """Integration test: parse all SKILL.md files to ensure they don't break."""
        repo_root = Path(__file__).resolve().parent.parent
        skill_files = list((repo_root / "skills").glob("*/SKILL.md"))

        # Skip if no skill files found (e.g., in CI)
        if not skill_files:
            pytest.skip("No SKILL.md files found")

        for skill_file in skill_files:
            with open(skill_file, encoding="utf-8") as f:
                content = f.read()
            try:
                result = parse_frontmatter(content)
                assert isinstance(result, dict), f"Expected dict, got {type(result)} for {skill_file}"
            except Exception as e:
                pytest.fail(f"Failed to parse {skill_file}: {e}")

    def test_ter_mux_pkg_name(self):
        """Test TERMUX_PKG_NAME field (used in skills)."""
        text = "---\nTERMUX_PKG_NAME: hf-cli\nTERMUX_PKG_DESCRIPTION: Hugging Face CLI\n---\nBody"
        result = parse_frontmatter(text)
        assert result.get("TERMUX_PKG_NAME") == "hf-cli"
        assert result.get("TERMUX_PKG_DESCRIPTION") == "Hugging Face CLI"

    def test_name_field(self):
        """Test name field (alternative to TERMUX_PKG_NAME)."""
        text = "---\nname: hf-cli\ndescription: Hugging Face CLI\n---\nBody"
        result = parse_frontmatter(text)
        assert result.get("name") == "hf-cli"

    def test_special_chars_in_value(self):
        """Test frontmatter with special characters in values."""
        text = "---\nname: test-skill\nnote: Uses `code` and [links](url)\n---\nBody"
        result = parse_frontmatter(text)
        assert "note" in result
        assert "code" in result["note"]

    def test_yaml_anchors_and_aliases(self):
        """Test that YAML anchors/aliases don't break parsing."""
        text = "---\nbase: &base\n  key: value\nderived: *base\n---\nBody"
        result = parse_frontmatter(text)
        # Should parse without error
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
