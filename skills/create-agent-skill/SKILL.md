---
name: create-agent-skill
description: Create or update Agent Skills in a project. Use when the user asks to create an AGENT SKILL, add a skill under .agents/skills, scaffold SKILL.md, package workflows/scripts/references/assets for an agent, or make reusable instructions for skills-compatible agents.
---

# Create Agent Skill

## Default Location

Create new skills in `./.agents/skills/{skill-name}` unless the user gives another path. The `{skill-name}` must be lowercase hyphen-case, no more than 64 characters, and match the folder name.

## Upstream References

Use the Agent Skills documentation as the source of truth when creating or updating skills:

- Specification: https://agentskills.io/specification
- Quickstart and default project location: https://agentskills.io/skill-creation/quickstart

Before changing rules for `SKILL.md` frontmatter, directory layout, optional resource directories, progressive disclosure, file references, or validation, re-check the specification.

## Workflow

1. Clarify only if the purpose, skill name, or target location is ambiguous. Otherwise choose a short verb-led hyphen-case name from the user's request.
2. Inspect the repository for existing `.agents/skills`, `AGENTS.md`, README, or project conventions before writing files.
3. Design the smallest useful skill:
   - Put required activation details in the `description`.
   - Keep `SKILL.md` focused on procedures and non-obvious project knowledge.
   - Add `scripts/`, `references/`, or `assets/` only when they directly support repeated use.
4. Scaffold the skill with `scripts/create_agent_skill.py`.
5. Replace placeholder instructions with the actual workflow, examples, and validation notes.
6. Validate the created `SKILL.md` frontmatter and confirm the files exist.

## Scaffold Command

From the repository root, run:

```bash
python3 .agents/skills/create-agent-skill/scripts/create_agent_skill.py "Skill Name"
```

Useful options:

```bash
python3 .agents/skills/create-agent-skill/scripts/create_agent_skill.py "Review API Changes" --resources scripts,references
python3 .agents/skills/create-agent-skill/scripts/create_agent_skill.py "Review API Changes" --description "Review FastAPI endpoint changes. Use when checking API behavior, auth, schema changes, or regressions."
python3 .agents/skills/create-agent-skill/scripts/create_agent_skill.py "Review API Changes" --path ./custom/skills
```

The script refuses to overwrite an existing skill unless `--force` is passed. Prefer inspecting and patching an existing skill instead of overwriting it.

## SKILL.md Requirements

Use this shape for every generated skill:

```markdown
---
name: skill-name
description: What the skill does and when to use it. Include concrete trigger words and task contexts.
---

# Human Readable Title

## Workflow

1. Step one.
2. Step two.
3. Validate the result.
```

Required rules:

- `name` must match the parent directory.
- `description` must be non-empty, under 1024 characters, and describe both capability and activation context.
- Keep the main body concise. Move long technical details to `references/` and link them from `SKILL.md` with relative paths.
- Use `scripts/` for deterministic repeated operations. Make scripts self-contained and include helpful error messages.
- Use `assets/` for templates, examples, images, or other files meant to be copied into outputs.

## Validation

After creating or editing a skill, check:

```bash
test -f .agents/skills/{skill-name}/SKILL.md
python3 .agents/skills/create-agent-skill/scripts/create_agent_skill.py --validate .agents/skills/{skill-name}
```

Also read the final `SKILL.md` and remove boilerplate that does not help another agent perform the task.
