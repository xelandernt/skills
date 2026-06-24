---
name: readme-authoring
description: Write or review README.md files for coding projects using a concise, maintainable structure. Use when creating, rewriting, auditing, or improving README documentation, setup instructions, project usage sections, prerequisites, install/build/test commands, contribution pointers, or stale README content.
---

# README Authoring

## Source

This skill summarizes and operationalizes Tina Boyce's Versent article, "Writing a good Readme.md file": https://versent.com.au/blog/writing-a-good-readme-md-file/

## Workflow

1. Identify the README's primary audience before editing:
   - New contributors need setup, install, build, test, and local run instructions.
   - Users of a binary or library need usage examples and common flags or APIs.
   - Open-source readers often need license, contribution, and maintainer context.
2. Organize the README with skim-friendly headings. Start from a simple structure and add sections only when the project needs them:
   - Project name and short purpose.
   - Prerequisites.
   - Install dependencies.
   - Build.
   - Run.
   - Test.
   - Usage examples.
   - Troubleshooting or known issues.
   - Contributing and license.
3. Prefer executable, copyable commands over prose-heavy manual steps. If the repository has a `Makefile`, `justfile`, npm scripts, task runner, or project scripts, document the one-line command before expanding into lower-level commands.
4. Keep each section clear and concise:
   - Use code blocks for terminal commands.
   - Use ordered lists for required sequences.
   - Use bullets or tables for scannable options.
   - Remove padding, history, and explanations that do not help the reader act.
5. Include just enough project-specific information. Add common command-line flags, required services, dependency constraints, links to style guides, or known dependency limitations when they affect normal development or usage.
6. Move bulky or slow-changing material out of `README.md` and link to it instead. Good candidates include ADRs, changelogs, database schemas, detailed design specs, contribution guides, coding conventions, naming rules, and commit-message rules.
7. Avoid dated or brittle instructions. Do not depend on exact external web UI paths, button locations, temporary URLs, or screenshots unless there is no stable alternative. Prefer stable commands, canonical project files, and durable links.
8. Validate the finished README from a reader's perspective:
   - The heading structure makes the needed section easy to find.
   - Setup, build, run, and test commands are copyable and match the repository's actual tooling.
   - Each section has a clear reason to exist.
   - Stale-prone details are removed, generalized, or delegated to more appropriate docs.

## Review Checklist

- Can a newcomer find setup commands without reading the whole document?
- Are common workflows shown as commands, not long manual prose?
- Does the README include project-specific facts that matter and exclude details better stored elsewhere?
- Are volatile instructions avoided or written in a way that will age well?
- Do links point to maintained project files or stable external references?
