# 05 — AI agents, low-token context and edit tracking

Canonical rules: [CORE_RULES](../engineering/rules/CORE_RULES.md). Keep existing `AGENTS.md`, `.agents/skills/token-efficient-thesis/SKILL.md`, and `.claude/skills/token-saving/SKILL.md`. Use tool-specific short pointers `CLAUDE.md`, `.github/copilot-instructions.md`, `ai/chatgpt/PROJECT_CONTEXT.md`, and `ai/deepseek/PROJECT_RULES.md`.

Every agent must search the current module index and duplicate symbols before adding any file. Actual code change editor attribution is recorded in `engineering/agent_edits/`; never infer it from commit author or a label.

For new tasks, supply a bounded prompt: goal, source file/function, relevant decision and source, tests, expected output, missing native evidence, and edit limits.
