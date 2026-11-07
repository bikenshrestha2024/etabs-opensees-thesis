# material_source_sets.py — implementation guide

**Source:** [components/nonlinear_time_history/material_source_sets.py](../../../../components/nonlinear_time_history/material_source_sets.py)
**Workstream:** 02 Materials. Added 2026-11-07.

## What it does

- **`PEER_2015_12_SINGLE_SOURCE`** basis: wall concrete (ConcreteCM), reinforcing steel (SteelMPF; the printed Menegotto–Pinto a1 = 18.5 is converted to OpenSees cR1 = a1/R0 = 0.925, because OpenSees uses R = R0(1 − cR1ξ/(cR2+ξ)) and an unconverted 18.5 gives NaN on the first reversal; cR2 = 0.0015 as printed), frame Concrete01 strength and peak strain, and frame Steel02 rebar are all taken from **one** card: Kolozvari, Orakcal & Wallace (2015), PEER 2015/12, Appendix B.3 (RW-A15-P10-S78 web). Nothing missing is filled from another paper:
  - Concrete01 post-peak terms: `MODEL_ASSUMPTION_NOT_IN_SOURCE`.
  - FSAM ν/α: `PROVENANCE_NOT_RECORDED` (the catalogue file has no locator).
  - SHS brace, FVD and BRB: `NOT_IN_SOURCE`. A device scenario still needs its own citation.
- **`source_table(basis)`** returns provenance rows. The GUI's "Material source table" button shows them and saves them as CSV (opens in Excel). `PUBLISHED_REFERENCE` is shown as `MIXED_SOURCES`.
- **`default_candidates(key, basis)`** gives sensitivity candidates of 0.9×, 1.0× and 1.1× the basis baseline (the analyst-bracket rule already used for brace Fy), or a stated reason when the baseline is 0 or depends on the model.

Existing bases are unchanged. This is a research transfer of a specimen card, not project calibration (see the transfer restrictions in [00_RESEARCH_REFERENCES.md](../../../../docs/00_RESEARCH_REFERENCES.md)).

## Verification

Test: `tests/verify_material_source_sets.py`. A native 0.1 s building probe is reported in the PR.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../../docs/00_THESIS_ACCEPTANCE_GATES.md)
