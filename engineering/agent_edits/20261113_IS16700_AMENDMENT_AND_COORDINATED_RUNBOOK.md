# 2026-11-13 — Source-version gate and coordinated thesis runbook

**Actor:** ChatGPT (GPT-6, GitHub connector). **Action:** Documentation-only, isolated branch/PR. **No ETABS EDB, executable solver physics, project inputs, native model output, user PDF, XLSX, or licensed standards were committed.**

## Baseline and scope
- Repository: `bikenshrestha2024/etabs-opensees-thesis`; starting ref: `main` on 2026-11-13 (exact commit base to be taken from created PR).
- Consulted: `AGENTS.md`, `CLAUDE.md`, `engineering/rules/CORE_RULES.md`, `KNOWLEDGE_BASE/README.md`, `REVIEW_MAIN/README.md`, `LITERATURE/README.md`, existing Stage 02 reference and acceptance gates.
- Private source consulted: supplied 38-page base IS 16700:2023 (September 2023) PDF. Its download watermark is not reproduced. Verified BIS catalog lists 2025 First Amendment; exact affected clauses remain unknown.

## Edited paths
- `KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/README.md` (new): explicit dependency order, roles, source/code/solver evidence, GUI and run-manifest status vocabulary.
- `LITERATURE/Codes_Standards/IS16700_2023_AMENDMENT_TRACKER.md` (new): source-page crosswalk, supplementary applicability, pending amendment verification and PDF handling.
- `KNOWLEDGE_BASE/README.md`, `LITERATURE/Codes_Standards/README.md`, `REVIEW_MAIN/README.md`: link existing canonical gateways instead of duplicating launchers.
- This edit evidence record.

## Verification and unknowns
- Checked the GitHub repository's actual tracked instruction and folder paths via repository file/tree reads.
- Checked official DUDBC NBC 105:2025 listing and BIS standard record (IS 16700:2023, First Amendment 2025).
- Documentation Markdown and relative links are to be reviewed in PR/CI. **No native Windows/ETABS/OpenSees, mesh convergence, acceleration-record suite or material experiment was executed.**
- Do not claim code tests passed from a documentation write. Existing code acceptance gates remain OPEN.
- Reviewer of governing code, applicability and amendment text: **NOT_ASSIGNED**.

## Next step
Reviewer checks actual BIS Amendment No. 1 text, signs code applicability, then implement any resulting changes with deterministic and native regression tests. Keep the uploaded PDF private; do not infer redistribution permission.
