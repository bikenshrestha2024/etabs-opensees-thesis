# Shared actual-solver support reaction identity: ETABS-to-OpenSees modules

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Perform failing-test-first and re-run full CI.

**Goal:** MRSM, NLTHA and shared model validation must recover reactions at actual OpenSees `build_complete_model` support joints, not at 76 original exported mixed mesh/foundation nodes when 32 physical supports are selected.

**Evidence and root cause:** `components/response_spectrum/model_analysis.py::run_model_spectrum` calls `require_runtime_support_case(selected_support,built)` correctly, then constructs `support_tags=sorted(int(n) for n,v in data['supports'].items() if any(v))` from *raw source JSON*. Under primary 32 support case the latter may enumerate 76 source-restraint/mesh tags. `components/nonlinear_time_history/source_model_handoff.py::solver_reaction_support_tags` already implements runtime tag extraction, but putting MRSM through NLTHA is an improper dependency. Migrate a single implementation to `components/model/support_case_contract.py`; preserve the NLTHA import as a compatibility wrapper.

**Source constraints:** read `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `CORE_RULES.md`, `ENGINEERING_GATES.md`, `MODULE_BOUNDARIES.md`, and relevant guides. 32 primary physical supports; 44 mesh points; 76/97 explicitly diagnostic; 2×12m X walls and 3×6m Y walls; 1.0D+1.0L gravity distinct from Table 5-1 seismic mass. Native EDB/workbook, Windows OpenSees and true reaction cuts are unavailable; no engineering acceptance.

## Step 1: RED behavior for exact solver tag recovery
- Modify `tests/test_esm_support_case_and_export_recovery.py` to assert the **shared** `solver_reaction_support_tags` returns exactly 32 current actual tags even when a synthetic source dictionary contains 76; also 76 and 97 explicit diagnostics, duplicates/booleans/non-integer values fail.
- Modify `tests/test_direct_existing_nltha_20261122.py` to assert the old NLTHA import still delegates and returns the same exact set.
- Add AST/structural regression to `tests/test_mrsm_canonical_output_v4.py`: MRSM reaction recovery must invoke shared `solver_reaction_support_tags(built,selected_support)`, and may not read `data['supports']` to decide `nodeReaction` tags.
- Run new headless tests in red on current production code. If missing-symbol/AST failures are the intended failures, proceed.

## Step 2: GREEN shared owner and compatibility
- Add strict shared implementation to `components/model/support_case_contract.py`. It calls `require_runtime_support_case`, forbids duplicate, boolean and malformed runtime tags, returns sorted exact actual solver tag list and explicitly labels *tag selection*, not physical ETABS matching.
- Retain `components/nonlinear_time_history/source_model_handoff.py::solver_reaction_support_tags` as a delegating backward-compatible facade.
- Change MRSM reaction recorder `support_tags` to the shared actual builder-derived result (both E0/E+/E− and X/Y); source `data['supports']` remains untouched for other legitimate source audits.
- Keep existing ESM/Modal/LTHA consumers and structure unchanged. No modifications to source EDB, stiffness, masses, gravity, model builder, spectrum CQC or modal factors.

## Step 3: Verification and limitations
- Run all affected tests and repository CI: headless tests, NLTHA quality, model/CI inventory, compilation and security.
- Record exact commit SHA, tests and actual changed paths.
- Document legacy/sensitivity support policies and the unresolved 768.045-kN pointwise primary foundation residual; current fix corrects only *which nodes* are queried for MRSM reaction results, not the numerical reaction values at those nodes.
- Note separate unresolved MRSM generalized modal mass from source `data['nodal_mass']` versus current `STORY_LUMPED_NBC` operator; do not silently change equations without numerical validation.
- Include all-module workflow priorities and the actual source basis in REVIEW_MAIN without claiming a 404-file line-by-line semantic audit.
