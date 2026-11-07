# section_tags.py — implementation guide

**Source:** [components/model/section_tags.py](../../../../components/model/section_tags.py)
**Workstream:** 01 Import/geometry. Added on branch `improve/damping-energy-viz` (2026-11-07).

## What it does

Single source for nonlinear fibre-section tags. Defaults come from `components/sections/definitions.py:SECTION_TAGS`, the module that creates the sections, and equal the literal previously hard-coded in `assembly.py` and `ui/application.py` (701/611/621/631). `nonlinear_section_tags` in the model config may add tags only on the reviewed route, where the project materials file defines the sections. The research route rejects any override that `define_all_fiber_sections` would not create. `validate_frame_mapping` lists **all** ETABS frame section names lacking a `frame_section_mapping` entry or a registered target before any element is built.

## References

NBC 105:2025 §9.3.1 (R10); OpenSees section/beamIntegration tag namespaces. Tag convention: [REF_TAG_CONVENTION.md](../../../../docs/REF_TAG_CONVENTION.md).

## Verification

Test: `tests/verify_section_tags.py`. Passing tests establish solver behaviour on small test models or synthetic data. They do **not** establish convergence, calibration or NBC acceptance of the thesis building.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../../docs/00_THESIS_ACCEPTANCE_GATES.md)
