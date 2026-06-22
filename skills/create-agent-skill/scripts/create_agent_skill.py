#!/usr/bin/env python3
"""Scaffold and validate Agent Skills."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAX_NAME_LENGTH = 64
RESOURCE_DIRS = {"scripts", "references", "assets"}
DEFAULT_DESCRIPTION = (
    "Describe what this skill does and when to use it. Include concrete trigger "
    "words, task contexts, file types, or workflows that should activate it."
)


def normalize_skill_name(raw: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower())
    name = re.sub(r"-{2,}", "-", name).strip("-")
    return name


def title_from_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def validate_name(name: str) -> list[str]:
    errors: list[str] = []
    if not name:
        errors.append("name is empty")
    if len(name) > MAX_NAME_LENGTH:
        errors.append(f"name is longer than {MAX_NAME_LENGTH} characters")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name or ""):
        errors.append("name must use lowercase letters, numbers, and single hyphens")
    return errors


def parse_resources(raw: str) -> list[str]:
    if not raw:
        return []
    resources = [item.strip() for item in raw.split(",") if item.strip()]
    invalid = sorted(set(resources) - RESOURCE_DIRS)
    if invalid:
        allowed = ", ".join(sorted(RESOURCE_DIRS))
        raise ValueError(f"unknown resource directories: {', '.join(invalid)}; allowed: {allowed}")
    deduped: list[str] = []
    for resource in resources:
        if resource not in deduped:
            deduped.append(resource)
    return deduped


def skill_template(name: str, description: str) -> str:
    title = title_from_name(name)
    return f"""---
name: {name}
description: {description}
---

# {title}

## Workflow

1. Replace this placeholder with the concrete steps an agent should follow.
2. Include only instructions that are useful when this skill activates.
3. Add validation steps that prove the requested work is complete.

## Notes

- Add `scripts/`, `references/`, or `assets/` only when they support this skill directly.
- Keep detailed reference material in separate files and link to it from this file.
"""


def create_skill(args: argparse.Namespace) -> int:
    name = normalize_skill_name(args.name)
    errors = validate_name(name)
    if errors:
        print("[ERROR] Invalid skill name:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    base_path = Path(args.path)
    skill_dir = base_path / name
    if skill_dir.exists() and not args.force:
        print(f"[ERROR] Skill already exists: {skill_dir}", file=sys.stderr)
        print("Use --force only when replacing the scaffold is intentional.", file=sys.stderr)
        return 1

    description = args.description or DEFAULT_DESCRIPTION
    if len(description) > 1024:
        print("[ERROR] Description must be 1024 characters or fewer.", file=sys.stderr)
        return 1

    try:
        resources = parse_resources(args.resources)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill_template(name, description), encoding="utf-8")
    for resource in resources:
        (skill_dir / resource).mkdir(exist_ok=True)

    print(f"[OK] Created {skill_dir / 'SKILL.md'}")
    if resources:
        print(f"[OK] Created resource directories: {', '.join(resources)}")
    return 0


def extract_frontmatter(skill_md: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, ["SKILL.md must start with YAML frontmatter"]
    try:
        _, raw_frontmatter, body = text.split("---", 2)
    except ValueError:
        return {}, ["SKILL.md must contain closing frontmatter delimiter"]
    fields: dict[str, str] = {}
    for line in raw_frontmatter.strip().splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("\"'")
    if not body.strip():
        errors.append("SKILL.md body is empty")
    return fields, errors


def validate_skill(path: Path) -> int:
    errors: list[str] = []
    if path.name != normalize_skill_name(path.name):
        errors.append("skill directory name is not normalized hyphen-case")
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"missing {skill_md}")
    else:
        fields, frontmatter_errors = extract_frontmatter(skill_md)
        errors.extend(frontmatter_errors)
        name = fields.get("name", "")
        description = fields.get("description", "")
        errors.extend(validate_name(name))
        if name and name != path.name:
            errors.append("frontmatter name must match parent directory")
        if not description:
            errors.append("description is required")
        if len(description) > 1024:
            errors.append("description is longer than 1024 characters")

    if errors:
        print("[ERROR] Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"[OK] Valid skill: {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create or validate Agent Skill folders.")
    parser.add_argument("name", nargs="?", help="Skill name or title to create")
    parser.add_argument("--path", default="./.agents/skills", help="Directory containing skill folders")
    parser.add_argument("--description", help="Initial SKILL.md description")
    parser.add_argument("--resources", default="", help="Comma-separated list: scripts,references,assets")
    parser.add_argument("--force", action="store_true", help="Overwrite the scaffold files in an existing skill")
    parser.add_argument("--validate", metavar="SKILL_DIR", help="Validate an existing skill directory")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.validate:
        return validate_skill(Path(args.validate))
    if not args.name:
        parser.error("name is required unless --validate is used")
    return create_skill(args)


if __name__ == "__main__":
    raise SystemExit(main())
