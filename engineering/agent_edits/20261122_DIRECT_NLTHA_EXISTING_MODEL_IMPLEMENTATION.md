# 2026-11-22 — Direct NLTHA existing-model execution and literature chapter

**Editor actually used:** OpenAI ChatGPT GPT-6 via connected GitHub API actions. Other editors/tools: UNKNOWN; no claims about Codex/Claude activity.
**Branch:** `feat/nltha-direct-run-literature-methods-20261122`.
**Base `main`:** `17f09109baf528dcaa23d4f7fb38cfeebbc214db`.
**User original model EDB SHA:** UNAVAILABLE; actual native case file SHA: UNAVAILABLE. **Native Windows ETABS/OpenSeesPy/XARA:** NOT EXECUTED in this connector environment.

## Mandatory physical contract and literature sources

Read `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `engineering/rules/CORE_RULES.md`, `ENGINEERING_GATES.md`, current NLTHA code, source guides and the NBC governing-code matrix. Preserve 32 physical support joints and 44 shell-mesh points; use 1D+1L only for full gravity comparison and NBC 105:2025 Table 5-1 for seismic weight; keep source 12 m X wall openings and actual model masses/geometry.

Scientific/standard sources: R01 PEER 2015/12, R02 Kolozvari et al. 2023 DOI 10.1016/j.engstruct.2023.116700, R10 NBC 105:2025, NIST GCR 17-917-46v1 DOI 10.6028/NIST.GCR.17-917-46v1, and OpenSees E-SFI-MVLEM-3D/Path documentation. Source models/accelerograms were not uploaded to GitHub by this change.

## Scope and actual source edits

- Tests added first (`tests/test_soil_c_direct_execution.py`). Test-only GitHub CI headless pytest failed at import as expected; this is recorded RED evidence, not a physical solver failure.
- New `components/nonlinear_time_history/soil_c_case_execution.py` calls the existing native exploratory solver in an isolated child Python process after source-bound configuration, registered A/B pair hash, model file and output collision checks. No change to numerical model, gravity solver, transient tolerance, accepted-step logic or physical theory.
- New root `38_EXECUTE_SOIL_C_NLTHA.py`, source guide, Stage 38 runbook, active module README and ordered-program index; source registry updated.
- New thesis chapter structure at `docs/thesis/NLTHA_METHODOLOGY_AND_EVIDENCE_20261122.md` explains literature-to-model translation, input provenance, governing NBC code, analyses, recorders, numerical validation, and publication limitations.
- Existing Stage 21 wall triage, Stage 35 input preflight, Stage 36 matrix, Stage 27 comparison and strict `THESIS_NLTHA` qualification gates are preserved.

## Required verification before merging

GitHub PR CI on exact final head must pass repository compilation/navigation, headless pytest, tracked-tree/integration audit, source inventory and disclosure checks. New tests use a fake child launcher and **do not** verify E-SFI wall convergence. A complete 25-storey native test requires matched source EDB/OpenSees JSONs, material/rebar cards, original waveform records, current OpenSeesPy binary, SeismoMatch processing evidence, 32-support ETABS-native verification, modal and signed P-Delta cases. No 224-run or code compliance claim is made.
