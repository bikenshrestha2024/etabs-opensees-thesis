# material_source_sets.py — implementation guide

**Source:** [components/nonlinear_time_history/material_source_sets.py](../../../../components/nonlinear_time_history/material_source_sets.py)
**Workstream:** 02 Materials. Added 2026-11-07.

## What it does

- **`PEER_2015_12_SINGLE_SOURCE`** uses the RW-A15-P10-S78 web ConcreteCM and SteelMPF entries in R01 Appendix B.3, printed pp. 90–91. The printed Menegotto–Pinto `a1=18.5` is converted to OpenSees `cR1=a1/R0=0.925`, with `cR2=0.0015` carried over. [PEER Report 2015/12](https://peer.berkeley.edu/publications/2015-12), [OpenSees SteelMPF source](https://github.com/OpenSees/OpenSees/blob/master/SRC/material/uniaxial/SteelMPF.cpp)
  - The exploratory frame transfers strength and peak strain to Concrete01 and rebar inputs to Steel02. Frame Concrete01 post-peak terms are `MODEL_ASSUMPTION_NOT_IN_SOURCE`.
  - Appendix B.3 lists `nu=0.8` and `alfadow=0.01` for both FSAM panel regions and different reinforcement ratios for the web and boundary.
  - SHS brace, FVD and BRB inputs are `NOT_IN_SOURCE`. A device scenario still needs its own citation.
- **`source_table(basis)`** returns provenance rows. The GUI's "Material source table" button shows them and saves them as CSV (opens in Excel). `PUBLISHED_REFERENCE` is shown as `MIXED_SOURCES`.
- **`default_candidates(key, basis)`** gives sensitivity candidates of 0.9×, 1.0× and 1.1× the basis baseline (the analyst-bracket rule already used for brace Fy), or a stated reason when the baseline is 0 or depends on the model.

Existing bases are unchanged. This is a research transfer of a specimen card, not project calibration (see the transfer restrictions in [00_RESEARCH_REFERENCES.md](../../../../docs/00_RESEARCH_REFERENCES.md)).

## Verification

Test: `tests/verify_material_source_sets.py`. A native 0.1 s building probe is reported in the PR.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../../docs/00_THESIS_ACCEPTANCE_GATES.md)


## 2026-11-22 — direct PEER Appendix B.3 literature-baseline policy

The user's thesis uses directly cited published constitutive inputs as a **research** baseline and reports source-specific parameter sensitivity; separate project material testing is **not** a prerequisite for attempting exploratory NLTHA. The PEER RW-A15-P10-S78 web FSAM reinforcement ratios are now directly adopted as `rho_x=rho_y=0.0074`, with published `nu=0.8` and dowel `alpha=0.01`. Its **distinct** boundary values (`rho_x=0.0082, rho_y=0.0587`) remain recorded, NOT applied to arbitrary wall panels without a verified region map. In the isolated PEER research draft, the former invented `20 mm @ 200 mm` bar proxy no longer controls these web values; mixed/nominal sensitivity bases remain labeled assumptions. See [the full page-specific source/units table and methodological distinction](https://github.com/bikenshrestha2024/etabs-opensees-thesis/blob/main/docs/engineering/20261122_DIRECT_PEER_LITERATURE_NLTHA_PARAMETERS.md).

Source-level tests: `tests/test_peer_direct_literature_fsam_transfer_20261122.py`. This does not certify that the 25-storey X-wall first step converged, establish actual M0–M6 device input, or set `approved_for_nltha=true`.
