---
name: token-saving
description: Use for every Claude Code task in this NBC 105 / ETABS-to-OpenSeesPy thesis repo to keep context and usage low (weekly-limit friendly) without relaxing engineering gates. Mirrors .agents/skills/token-efficient-thesis for Codex.
---

# Token-saving workflow (Claude Code)

AGENTS.md rules still apply in full. Saving tokens never means skipping native checks or relabelling results.

## Before any tool call
- State the single deliverable, the allowed paths and the done-test, in 1–3 lines.
- Split large requests into phases and finish the most valuable one first.

## Reading
- `git status --short`, then `rg -n "<symbol|error text>" components tests`. Read only the matched line ranges (`sed -n a,bp`). Never read a whole large module or GUI file.
- Skip `Saved_Project_V156/`, `Worked_Example_*/`, `archive/`, `Verification_V*/` and generated results unless the task targets them.
- Read each file at most once per session. Re-open only the specific lines you still need.
- Do not re-read `AGENTS.md`, this skill, or large docs after context compaction; use the notes you already have.

## Running
- Run the affected test first: `PYTHONPATH=$PWD python tests/verify_<x>.py`. Run the full `tests/verify_*.py` suite once, before the commit.
- Full-building OpenSees runs take minutes. Run at most one in the background, use a 0.1 s trial with per-step progress, and never run several model copies in parallel (the container runs out of memory).
- If the same command fails twice, stop and diagnose it; do not loop.

## Editing
- Make the smallest change and keep public names stable. Use a scripted `str.replace` with an assertion for multi-site edits instead of rewriting the file.
- Each new module needs a `[REF ...]` docstring tag, a `docs/source/<path>.md` guide and one deterministic test.

## Reporting (short)
- **Changed:** paths and behaviour. **Verified:** commands and their results. **Unverified:** native ETABS/OpenSees items still missing. **Commit:** SHA and branch.
- Give at most 12 lines unless the user asks for more.

## Commit trailers
`AI-Assisted-By: Claude Code` · `AI-Model: not recorded` · `Engineering-Validation: <exact stage>`
