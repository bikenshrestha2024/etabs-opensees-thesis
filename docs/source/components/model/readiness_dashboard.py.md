# readiness_dashboard.py — evidence backend

**Code:** [`components/model/readiness_dashboard.py`](../../../../components/model/readiness_dashboard.py)

This module is part of the model-specific, read-only nonlinear readiness tool. It discovers candidate evidence and SHA256 fingerprints or displays the evidence dashboard. It does not modify source ETABS exports, apply material profiles, approve nonlinear analyses or bypass the existing model-bound readiness criteria.

Units are not inferred from filenames. Reviewer claims and actual native solver/experimental validation remain different categories.

**Tests:** `tests/verify_readiness_dashboard.py` checks missing evidence, stale model hash, nonpromotion of candidate files and report export.

**References:** [NBC105 seismic index](https://dudbc.gov.np/pages/24231978/), PEER 2015/12 and [thesis gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module index](../../00_SOURCE_GUIDE_INDEX.md)

## 2026-11-12 per-audit hash reuse

**What:** within one refresh, the same evidence file is hashed once even if multiple workstreams require it. **When:** `audit(root, model)` computes file fingerprints. **Why:** reduce redundant file reads and runtime without changing physical evidence.

**How:** local `Path.resolve()`→SHA-256 dictionary, discarded at the end of each audit; each new refresh computes new hashes. Verified with `tests/verify_readiness_dashboard.py::test_duplicate_evidence_is_hashed_once_per_audit`.

**Where:** `components/model/readiness_dashboard.py`. **Which:** only evidence files in allowed project locations; no new source discovery and no change to code acceptance. **Who:** software maintainer validates hash correctness and reviewer validates source identity.

**Limitation:** like any snapshot, a file modified while being hashed may invalidate project identity; don't change evidence during signed analysis.

## 2026-11-12 — incomplete checklist and cross-project model fail-closed fix

**What:** `audit(folder, model_script)` no longer reports an overall model-bound sign-off when a draft contains only an arbitrary subset of the required review keys. It also refuses sign-off when a manually selected model file is outside the selected project directory (or missing). The model may still be inspected without approval.

**Why:** an `approved_for_nltha: true` flag plus one checked item is insufficient for full project-model readiness. Reusing a signed draft from another project must not silently claim current-project sign-off.

**When:** each readiness refresh, project switch or model selection. **Where:** `components/model/readiness_dashboard.py`, `tests/verify_readiness_dashboard.py`. **How:** require all `REVIEW_KEYS` across the twelve groups, true values and substantive evidence strings; require the model to be under the selected project folder, and retain source model SHA comparison. The report still labels any recorded signoff a *claim*, not physical model verification.

**Which:** an exact nonlinear builder file, model-bound draft SHA and all defined review keys; code never modifies materials, loads or native model. **Who:** software maintainer tests behavior; the project engineer documents evidence; the independent structural reviewer decides engineering acceptance.

**Regression:** `python -m unittest tests.verify_readiness_dashboard -v`; new cases cover subset-checklist false approval and external-project model selection. **Limits:** no native full-model analysis, no automatic engineering approval, and no replacement for independent material validation.


## 2026-11-23 — NLTHA run-gate input-binding consistency

The read-only dashboard previously checked only the selected nonlinear
builder path and script SHA before showing a model-bound human sign-off
claim. The production `components.model.readiness` run gate also binds:
`model_config_sha256`, `nonlinear_materials_file_sha256` and
`nonlinear_wall_fsam_tags_sha256`. An unchanged script with a changed
model config, material input or wall FSAM mapping could therefore leave
the dashboard's sign-off claim stale.

`_load_draft` now preserves a signed claim only when all three original
binding keys are present and equal the **current** values computed by
the production `current_binding` helper, and when
`approval_binding_problems` finds no missing material, FSAM tag or
nonlinear-parameter-review prerequisite. Saved draft JSON is **never
changed** by this audit. A legacy unbound signed draft is
`INPUT_BINDING_NOT_RECORDED`; changed source is
`INPUT_BINDING_MISMATCH`; unreadable bound input is
`INPUT_BINDING_UNREADABLE`; incomplete source prerequisites are
`INPUT_BINDING_INCOMPLETE`. None displays an approved dashboard claim
or per-group signoff claim; evidence files remain independently
discoverable for inspection. For unsigned/in-progress drafts the dashboard
still shows existing partial human review entries without promoting them
to overall signed readiness.

**TDD:** `tests/test_nltha_dashboard_input_binding_20261123.py`
simulates a complete bound review, missing legacy binding, config
change, external material file edit/deletion, changed wall FSAM tags,
missing source prerequisites and unreadable input. Existing
`tests/verify_readiness_dashboard.py` valid-signoff fixture now
records synthetic source bindings to reflect actual production policy.
The initial RED run at `c2a33ed8` found six expected failures;
the unreadable classification RED at `fc179f4d` found one expected
failure. Final green status is conditional on latest PR head CI.

**Scope:** this is signoff-provenance consistency, not engineering
approval, native ETABS/OpenSees equivalence, material calibration,
convergence, or NBC clause certification. The separate production run
gate remains authoritative.
