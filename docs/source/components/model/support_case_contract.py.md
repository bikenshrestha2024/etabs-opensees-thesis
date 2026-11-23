# support_case_contract.py — authoritative thesis support-case selector

**Active owner:** [components/model/support_case_contract.py](../../../../components/model/support_case_contract.py) · **Source:** [read-first physical-model contract](../../../../engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md) · **Tests:** [ESM/support case source regressions](../../../../tests/test_esm_support_case_and_export_recovery.py)

## Purpose and source-identity limits

The user's intended primary foundation has **32 actual physical foundation supports**. The original 76 exported restrained source IDs include **44 shear-wall mesh points, not 44 independent physical foundations**. The current 32 tags are project-specific to the active 25-storey model. This module guards their exact identity; do not substitute an old EDB or different mesh without independent matching provenance. Native ETABS auto-edge, parent shell, beam-end rigid zones and MPC load-transfer equivalence remain **NOT_VERIFIED**.

## Centralized profiles

- `PHYSICAL_32` — default for the active thesis model. Retains the source's original restraint components for exactly the user-confirmed 32 tags, leaving the 44 other source-restrained shear-wall mesh points **unfixed** for source-verified shell/edge transfer. This is the primary **intended physical foundation topology**, not yet proven equivalent to ETABS's analytical constraint interpolation.
- `SOURCE_76` — explicit diagnostic sensitivity reuses the exported 76 restraint-point flags; **not** a model with 76 independent physical foundations.
- `WALL_BASE_97` — explicit diagnostic 97-restraint idealized wall-base extension, using the existing geometry-checked wall-edge method. Only available if exactly the required new 21 geometric mesh-node restraint positions can be identified; this is not a claimed real foundation topology.

`normalize_support_case(value)` accepts only these three values or numeric aliases `32`, `76`, `97`; `select_support_case(data,topology,case,wall_base_extension=...)` does not modify the exported original data. It fails closed on missing physical tags, invalid DOFs, inconsistent source counts and unavailable 97-point topological extension.

## Integration and evidence

The active `components/model/assembly.py::build_complete_model` resolves `OPENSEES_SUPPORT_CASE` before constructing the OpenSees domain, and records `support_case_evidence` in the model report. This shared entrypoint is used by ESM, Rayleigh, Modal, MRSM and seismic history scripts that run the active complete model builder. The ESM GUI pins the chosen profile to each generated script and to subprocess environment; the original gravity GUI's full-`1D+1L` comparison profiles remain separate, backward-compatible and source-labelled.

**Important physical caveat:** simply removing 44 exported restraints does **not** implement ETABS auto-edge constraints or prove correct reaction transfer. The prior best rebuilt ETABS-elastic maximum joint gravity discrepancy **768.045 kN** remains unresolved. A source-specific native element/node/MPC and common-cut comparison is mandatory.

**Load-case firewall:** `GRAVITY_1.0D_1.0L` is the full 100% dead + live gravity comparison. Seismic mass/preload uses NBC 105:2025 §5.2 Table 5-1, categorized DL=1, storage LL=0.6, other LL=0.3, roof LL=0, when applicable. Support scenario selection must never silently change these.

**Validation status:** synthetic software tests only; full 25-storey native ETABS/OpenSees model and 32/76/97 modal, ESM, MRSM and NLTHA equivalence remain NOT_VERIFIED.

## 2026-11-22 stale packaged-runtime gate

`require_runtime_support_case(profile, build_report)` compares the selected profile and **actual build-returned** `gravity_base_support_tags`, then requires matching `support_case_evidence.profile`. A stale exported `OpenSees_Runtime_V118` that ignores a new GUI support choice now triggers a clear **REFRESH THE EXPORTED RUNTIME** error instead of producing mislabeled 76/97 source results for a selected 32-case. This check is called after model construction by ESM, Modal, MRSM, LTHA and NLTHA, using the same project tag contract. The check verifies a source software selector, **not** native ETABS analytical edge interpolation, 768-kN gravity reaction parity or code design acceptance.


## 2026-11-23 — Single actual-solver reaction tag owner

New `solver_reaction_support_tags(report, support_case)` retrieves
`gravity_base_support_tags` **from the actual built model report**, validates
their positive-integer, unique identity, calls
`require_runtime_support_case` to verify the exact chosen 32 / diagnostic
76 / diagnostic 97 profile, then returns sorted node tags for solver
reactions and response records. This is a shared function, not an
independently reconstructed support assumption.

**Changed call sites:** `components/response_spectrum/model_analysis.py`
MRSM uses the actual builder report for reaction baselines, modal reaction
envelopes, and CSV node tags. The pre-existing public import in
`components/nonlinear_time_history/source_model_handoff.py` delegates to
this function to avoid a backward-incompatible NLTHA change.

**Conservative limits:** 32 actual supports versus 44 extra wall-mesh
points is still the user-confirmed source policy. The model's shell/MPC
edge transfer, rigid-end offsets and pointwise reaction agreement
remain unverified. This correction changes which recorder nodes are read,
not solver stiffness, loads, mass, boundary conditions or spectral
combination equations.

**Regression:** `tests/test_shared_solver_support_recovery_20261123.py`
verifies primary and diagnostic profiles, rejects duplicate/bool/invalid
tags, checks NLTHA public import and MRSM AST reaction-tag call site.
