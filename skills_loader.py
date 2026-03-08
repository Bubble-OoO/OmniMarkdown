"""
skills_loader.py
Scans all Markdown skill files in the skills/ directory and parses them into structured objects.

Markdown skill file format:
  ## Metadata        → parses skill_id / trigger prefix / icon / color / description
  ## System Prompt   → extracts system prompt text
  ## User Prompt Template → extracts template with {note_content} {user_input} placeholders
"""

import os
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Skill:
    skill_id: str
    label: str
    icon: str
    prefix: str
    color: str
    description: str
    system_prompt: str
    user_prompt_template: str

    def build_user_prompt(self, note_content: str, user_input: str) -> str:
        """Replace placeholders in the template with actual content."""
        return self.user_prompt_template.replace(
            "{note_content}", note_content
        ).replace(
            "{user_input}", user_input
        )


def _extract_section(text: str, section_title: str) -> Optional[str]:
    """Extract content between two ## headings."""
    pattern = rf"## {re.escape(section_title)}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _parse_meta(meta_text: str) -> dict:
    """Parse metadata block, supports - **Key**: value format."""
    result = {}
    for line in meta_text.splitlines():
        m = re.match(r"-\s+\*\*(.+?)\*\*:\s*`?(.+?)`?\s*$", line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            result[key] = val
    return result


def load_skills(skills_dir: str = "skills") -> dict[str, Skill]:
    """
    Scan all .md files in skills_dir, parse and return a {skill_id: Skill} dict.
    """
    skills: dict[str, Skill] = {}

    if not os.path.isdir(skills_dir):
        print(f"[SkillLoader] Warning: skills directory '{skills_dir}' not found. Using empty skill set.")
        return skills

    for filename in sorted(os.listdir(skills_dir)):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(skills_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"[SkillLoader] Failed to read {filename}: {e}")
            continue

        title_match = re.match(r"#\s+Skill:\s*(.+)", content)
        raw_label = title_match.group(1).strip() if title_match else filename.replace(".md", "")

        meta_text      = _extract_section(content, "Metadata")
        system_prompt  = _extract_section(content, "System Prompt")
        user_prompt_tpl = _extract_section(content, "User Prompt Template")

        if not meta_text or not system_prompt or not user_prompt_tpl:
            print(f"[SkillLoader] {filename} is missing required sections, skipping.")
            print(f"             Required: Metadata / System Prompt / User Prompt Template")
            continue

        meta = _parse_meta(meta_text)

        skill = Skill(
            skill_id=meta.get("Skill ID", filename.replace(".md", "")),
            label=raw_label,
            icon=meta.get("Icon", "🔹"),
            prefix=meta.get("Trigger Prefix", "?"),
            color=meta.get("Color", "blue"),
            description=meta.get("Description", ""),
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_tpl,
        )
        skills[skill.skill_id] = skill
        print(f"[SkillLoader] ✅ Loaded skill: {skill.icon} {skill.label} (prefix: {skill.prefix})")

    return skills


def match_skill(user_input: str, skills: dict[str, Skill]) -> tuple[Optional[Skill], str]:
    """
    Match a skill based on the user input prefix.
    Returns (matched Skill or None, instruction text with prefix stripped).
    """
    text = user_input.strip()

    for skill in skills.values():
        prefix = skill.prefix.strip("`").strip()
        variants = [prefix, prefix.replace("!", "！"), prefix.replace("?", "？")]
        for v in variants:
            if text.lower().startswith(v.lower()):
                instruction = text[len(v):].strip().lstrip("：:").strip()
                return skill, instruction

    default = skills.get("query")
    return default, text