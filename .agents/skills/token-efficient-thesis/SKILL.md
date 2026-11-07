---
name: token-efficient-thesis
description: Use for small or medium scoped Codex tasks in this ETABS-to-OpenSeesPy/NBC 105 thesis repo when reducing context, tool calls, repeated compaction, and unnecessary file reads is important. Applies to coding, debugging, GitHub review, tests and documentation; never relax physical validation gates.
---

# Token-efficient thesis engineering workflow

**Goal:** minimize wasted context and repeated work, not minimize engineering correctness. Follow the root `AGENTS.md` first. This skill cannot override code, evidence, confidentiality, or native-validation requirements.

## 1. Define one bounded deliverable

Before tools, identify in 1–3 lines:
- Target: one bug, feature, module, or engineering hypothesis.
- Allowed paths and the smallest directly related dependencies/tests.
- Done condition: precise changed behavior, a relevant test, or a short evidence-based finding.

If a prompt combines DOCX reading, full Git history, source review, research, code modifications, and GitHub commits, split into phases. Complete the highest-value bounded phase first; report deferred work rather than silently expanding scope. Ask one question only when work cannot safely proceed.

## 2. Retrieve narrowly and only once

1. Check `git status --short`, `git rev-parse --short HEAD` and `git diff --stat`. Preserve all unrelated user changes.
2. Read only the matching task guide and source file slice, not every document linked from `AGENTS.md`. When physics is affected, consult the applicable NBC 105 source, review ledger and source guide.
3. Use `rg -n "exact_symbol|error_message" components tests` before browsing; request bounded context (`rg -C 5`, selected line ranges). Exclude `Saved_Project_V156/`, `Worked_Example_*/`, generated results and historical archives **unless** the task specifically targets them.
4. Cache a source/path once per turn. Never repeatedly read the same `SKILL.md`, DOCX, log, or whole source after compaction if it was already successfully read. Refer to existing notes/line refs; reopen just the required passage if genuinely missing.
5. Read a documents/PDF/spreadsheet skill only when actually creating or processing that artifact; a file mentioned as background does not justify repeatedly loading its whole skill guide.

## 3. Loop/compaction circuit breaker

- If the **same command or file-read is attempted twice without useful progress**, stop that approach. Diagnose path, permissions, size and tool output; try at most one meaningfully different method.
- If context compacts repeatedly, create/reuse a *short* checkpoint of objective, changed paths, current HEAD, passed/failed commands and next single action. Do not re-run discovery from the beginning.
- When a source response is too long, request line slices; do not send or print an entire huge repository file or DOCX into context.
- Avoid autonomous loops. After a failed test, inspect the targeted traceback and change only the relevant code; do not run the whole CI suite repeatedly.
- If progress remains blocked, report the blocker, what is verified and an exact next command. Do not claim success or start another broad agent task.

## 4. Minimal edit → focused verification

1. Reproduce with a deterministic, small test or a captured actual failure.
2. Change the smallest active module; keep legacy launchers and unrelated functions stable.
3. Run syntax/import checks and *affected tests first*. Only then run a broader suite if necessary.
4. For ETABS OAPI and OpenSees native modeling: CI/static smoke tests are **not** real ETABS/OpenSees validation. Do not report code acceptance without project-native gravity, mass, wall material, transient, and record evidence.
5. Do not replace the authoritative **original Excel Aw/opening method**; preserve workbook source hashes and source-cell traceability. Keep ULS/SLS, XY/YX, 8 paired matched Soil-C records, `Acc(g)` → SI conversion, separate M0–M6 cases and failure statuses intact.
6. For first-step NLTHA failures, prioritize a bounded ZERO/X/Y/XY diagnostic and the first nonfinite accepted state, not a full 224-case rerun.

## 5. Source and code attribution

- Use repository `docs/review/AI_CONTRIBUTION_PROVENANCE.md`.
- When Codex assists with a commit, add truthful trailers, e.g.:
  `AI-Assisted-By: Codex`
  `AI-Model: <model displayed in this session or Unknown>`
  `Engineering-Validation: STATIC_TESTS_ONLY` (or exact honest stage).
- Never infer earlier commits' AI origin from the GitHub author, writing style, or timestamps. A changed Git author is not AI provenance.
- Do not rewrite published Git history or commit unrelated changes.

## 6. Response contract (short)

Reply in at most ~12 lines by default:
- **Changed**: paths and key behavior.
- **Verified**: exact commands/tests and outcome.
- **Unverified**: native ETABS/OpenSees or code-clause review still missing.
- **Commit**: SHA and branch (only if actually committed).
- **Next**: one actionable, bounded engineering step.

Do not claim an estimated percentage of token savings, guarantee a lower rate-limit charge, or recommend lowering reasoning effort for a safety-critical engineering decision merely to save tokens.

## Useful task prompt

```text
Use $token-efficient-thesis. Scope: <one module / issue>.
Read only the active file, direct imports and relevant tests.
Preserve root AGENTS.md engineering gates and original Excel Aw.
Implement the smallest safe change; execute targeted tests once,
then report observed failures, validation gaps and exact changed files.
Do not read archives, rerun full-repo audits or infer source data.
```
