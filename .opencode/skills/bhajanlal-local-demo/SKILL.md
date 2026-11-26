---
name: Bhajanlal Local Demo
description: Use when demonstrating project-local skill discovery in the Bhajanlal serve gateway.
---

# Bhajanlal Local Demo

Part of the **Bhajanlal** model-building skill library. Pillar: 12. OpenCode Setup, Models & Skills

Use when demonstrating project-local skill discovery in the Bhajanlal serve gateway.

## Workflow

1. Confirm the project root is exported as `BHAIJANLAL_HOME` before `serve/skills.py` is imported.
2. Load this skill through the `skill` builtin tool or let `prompt_block()` apply it.
3. Verify `SkillLibrary.get("bhajanlal-local-demo")` returns this document.

## Output

Proof that project-local `.opencode/skills/` discovery works end to end.
