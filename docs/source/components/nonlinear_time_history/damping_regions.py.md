# damping_regions.py — implementation guide

**Source:** [components/nonlinear_time_history/damping_regions.py](../../../../components/nonlinear_time_history/damping_regions.py)
**Workstream:** 05 Damping. Added on branch `improve/damping-energy-viz` (2026-11-07).

## What it does

Assigns Rayleigh damping with two OpenSees `region` commands: structural elements (frame, core wall, slab) get `-rayleigh aM 0 0 bK`; lumped-mass nodes that belong to no structural element (diaphragm masters) get `aM` only. Elements whose `ops.eleType` is a link, truss or zero-length class (FVD `TwoNodeLink`, BRB/brace `CorotTruss`) are excluded, plus any tag in `rayleigh_excluded_element_tags`.

Inherent ratio: `inherent_damping_ratio` (fraction) defaults to **0.025**. Ratios above 0.025, up to the 0.05 cap, need `inherent_damping_five_percent: true`. Set that flag to reproduce runs made before 2026-11-07, which used a fixed 0.05.

Native facts this design relies on (OpenSeesPy 3.8.0, see the test):
* `Truss`, `CorotTruss` and `TwoNodeLink` ignore bK unless created with `-doRayleigh 1`. The former global `ops.rayleigh` therefore did **not** double-count on the current braces and FVD links; the region form is result-identical for them and stays correct if a device opts in.
* `region -node` also captures every element whose nodes all lie in the node set and resets its factors. A node region covering slab/beam nodes would erase their bK. Only orphan mass nodes go in the node region.

## References

Charney (2008) doi:10.1061/(ASCE)0733-9445(2008)134:4(581); Zareian & Medina (2010) Comput. Struct. 88(1-2):45-53; PEER TBI 2017; LATBSDC 2020; NBC 105:2025 §8.1.1 as cited in the repo (verify the clause text). Tag convention: [REF_TAG_CONVENTION.md](../../../../docs/REF_TAG_CONVENTION.md).

## Verification

Test: `tests/verify_damping_regions.py`. Passing tests establish solver behaviour on small test models or synthetic data. They do **not** establish convergence, calibration or NBC acceptance of the thesis building.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../../docs/00_THESIS_ACCEPTANCE_GATES.md)
