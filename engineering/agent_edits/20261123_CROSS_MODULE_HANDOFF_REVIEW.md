# 2026-11-23 — all-module ETABS → OpenSees handoff audit and runner SHA gate

- **Editor/agent:** OpenAI ChatGPT GPT-6 using connected GitHub (not native Codex, Claude, ETABS, or Windows).
- **Base main:** `e3e14d884de38c3a4d9d9de0567795a887b16db1`.
- **Branch/PR:** `audit/cross-module-handoff-integrity-20261123`, pull request #162.
- **Read-first:** `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `CORE_RULES.md`, `ENGINEERING_GATES.md`, NBC code matrix, active module inventory and source guides.
- **Reviewed owners:** inputs, model/sections, gravity/PDelta, modal, ESM, MRSM, linear/nonlinear time history, NBC 105, validation, GUI and shared outputs. See `REVIEW_MAIN/09_SOFTWARE_SECURITY/20261123_ALL_MODULE_ETABS_OPENSEES_HANDOFF_AUDIT.md`.
- **TDD RED:** GitHub Actions `45126416007` at `c126ebe195e2692ae544f707667b68225e07bb8d`: four expected failures exposing re-used ESM success after runner bytes change, missing digest, foreign runner path and duplicate-name collision; 1,771 unrelated tests passed, 5 skipped. This is a software regression only.
- **Code scope:** `components/equivalent_static/organized_exports.py` + `calculation_and_gui.py`; exact-runner hash/path comparison, saved batch status and workbook detail. Synthetic tests and source docs updated.
- **Preserved physical contract:** 32 physical supports + 44 wall-mesh points; full 1D+1L gravity; NBC Table 5-1 seismic weight; current two 12-m X source walls; all stiffness/material/mass/load/solver calculations untouched.
- **Native source IDs:** EDB SHA, workbook SHA and exact Windows model/result ZIP UNAVAILABLE; do not invent or publish.
- **Native acceptance:** NOT EXECUTED. ETABS/OpenSees physical equivalence, 32-support reaction residual, Vs30, wall NLTHA convergence and complete M0–M6 records remain OPEN.
- **Later regression/check output:** see GitHub PR #162 latest Actions checks, not earlier commits. Legacy saved statuses without runner SHA are intentionally unverified.
- **Confidentiality:** no EDB, workbook, motion files, private absolute Windows paths or raw measured project evidence uploaded.
