# 2026-11-23 — MRSM source-verified reopen / shared ledger provenance

- **Editor:** ChatGPT GPT-6 through connected GitHub and Superpowers installed skill guidance; not ETABS/OpenSees native solver.
- **Base:** `main@b042f1583504c4f66bc54312232e5cf04013b077`. **Branch:** `fix/mrsm-reopen-provenance-20261123`; PR #163.
- **Read-first:** AGENTS.md, READ_FIRST_PHYSICAL_MODEL_CONTRACT.md, .agents/skills/etabs-opensees-read-first/SKILL.md, CORE_RULES.md, ENGINEERING_GATES.md, relevant stage and ledger source guides, prior all-module integration audit.
- **Source defect:** MRSM GUI reopened saved `MRSM_Batch_Status_V151.json` and counted completed process rows as numerical success without verifying current serialized model SHA, selected ULS/SLS/config, unique canonical run ID, case manifest or saved numeric output.
- **Intended fix:** opt-in shared ledger provenance + exact same source/state/config/run revalidation on MRSM reopening; stage level latest status and immutable per-run ledger archive; fail closed for changed/missing source/numeric evidence.
- **TDD RED:** GitHub Actions run 45138690703 on `dc505037`: five new tests failed because `review_saved_mrsm_batch` and `mrsm_input_signature` did not exist; 1775 existing tests passed.
- **Changes:** `components/shared/case_status.py`, `components/response_spectrum/model_analysis.py`, focused synthetic regression and two source guides; all-module follow-up in REVIEW_MAIN/09_SOFTWARE_SECURITY.
- **Physical contract preserved:** 32 actual supports with 44 wall mesh nodes, full gravity D+L, NBC Table 5-1 categorized seismic weight, actual two 12m X walls, 3×6m Y walls. No spectral/scaling, damping, mass, element, source geometry, support assignments or solver algorithms changed.
- **Model and workbook source digests:** unavailable here; no private project files uploaded or guessed.
- **Native model/ETABS parity, code compliance, 768kN reaction residual and NLTHA wall failure:** unverified, open blockers.
- **Latest CI:** check workflow run IDs associated with PR #163 final head; old RED and intermediate failures are not claimed to pass.


- **Additional GUI performance gate:** Initial direct saved JSON validation on Tk initialization was detected in code review after source tests passed; synthetic AST regression committed at `6d4d17a4`, verified red 1/1781. Review moved to a background thread with Tk event-loop callback and input-change invalidation. No speedup in native solver computation is claimed.
