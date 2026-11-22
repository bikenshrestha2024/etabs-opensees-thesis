# 2026-11-22 — NLTHA source-mapped acceptance and reference-framework integration record

**Editor / tool actually used:** OpenAI ChatGPT GPT-6 using connected GitHub actions. Other editor/provider: UNKNOWN; no retrospective attribution to Codex or Claude. **Branch:** `fix/nltha-reference-step-acceptance-20261122`. **Base main commit:** `3c3b9e3876569fbf042482158314b504d8069122`. Final PR: #152. **Model EDB / source workbook SHA:** UNAVAILABLE in this connector session. Native Windows ETABS/OpenSees/XARA replay: NOT RUN.

## First-read and accessible historical context

Read `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `engineering/rules/CORE_RULES.md`, code-purpose matrix, NLTHA source modules and relevant per-file guides. Consulted recorded project memory and project provenance. Raw prior Codex/Claude chat sessions were not accessible; no private model data or assistant conversations were reproduced to GitHub.

**Physical invariant:** 32 actual foundation support joints + 44 wall-mesh transfer points, not 76 independent foundations. **Load-purpose invariant:** full comparative gravity `GRAVITY_1.0D_1.0L` with full live participation; NBC 105:2025 §5.2 Table 5-1 category-dependent seismic mass separately. X wall remains two 12 m walls with source openings. Never substitute 2020 code, reference low-rise frame model or historical 6 m X-wall workbook.

## Upstream source and engineering rationale

Reference `nirajkyadav/Framework_for_Seismic_Assessment_of_RC_Buildings` (MIT ©2025 Niraj Kumar Yadav); reviewed README and source `Test_Models/Groups/CCP/single/Gravity_Analysis.py`, `Unidirectional_Multiple_Eq.py`, `ReadRecord.py` and `Final_Codes/NBC_105_2020/NBC_105_2020_parallel_runs.py`. Only the broad architecture (explicit gravity-to-dynamic handoff, staged fallback and full response recording) was adopted as guidance. Reference fallback hardcoded increments and unchecked solver returns were **not copied** into this NBC 105:2025 25-storey system. The previous project fork review remains in `REVIEW_MAIN/04_NONLINEAR/FORK_RC_ASSESSMENT_20261117/SOURCE_REVIEW.md`.

## Scope of source edits

- `components/nonlinear_time_history/full_record_gate.py`: add strict finite-clock increment contract, without solver material or time-step alteration.
- `components/nonlinear_time_history/runner_and_gui.py`: use same contract for **production and exploratory caller**; reject a failed step which advances solver time; track accepted step count and first accepted evidence only after successful recorder. Save first wall focus before appending any accepted CSV row; reject nonfinite or absent focused wall tags.
- `components/nonlinear_time_history/first_step_transition.py`: explicit focused accepted-step finite/tag gate with non-causal diagnostic semantics.
- `tests/test_nltha_step_clock_contract_20261122.py`: deterministic fake-OpenSees tests, with RED verified via GitHub Actions on test-only source branches; includes 0-return-without-progress, overshoot, failed-step clock shift, positive fallback, callback failure and wall focus status.
- `tests/test_first_step_transition.py`: previous test fake now advances simulated clock on success; existing first-step evidence coverage retained.
- Source guides and existing fork-review document updated; `docs/review/ledger/semantic_review_attestations.csv` renewed against current source Git blob SHA and explicit test evidence, not asserted as native physics verification.

## Verification classification / unresolved science

**Software gates:** GitHub CI unit, compile, audit, import and output checks required on final PR head. Record executed outcomes from GitHub rather than claiming them from code inspection. **Engineering gates remain OPEN:** historical first-step X-wall at ~0.005 s, source mapping 110280/112778 and localForce after solver failure; user-confirmed 32-support ETABS–OpenSees pointwise reaction mismatch; source wall panel material/FSAM calibration; same-source gravity and IS exception P-Delta native handoff; modal/damping/record scale; 8 matched Soil-C pairs across M0–M6 full XY/YX history. No change qualifies a real physical NLTHA as passed.

## Academic integrity and attribution

Reference README uses supervisor spelling `Dr. Kshitiz C. Shrestha`. User's thesis document names `Assoc. Prof. Dr. Kshitij Charan Shrestha`. Preserve exact source spelling in citations and do not silently equate two names without verification. No upstream code copied verbatim and no private EDB/Excel, file paths, personal discussions or copyrighted paper PDF committed.
