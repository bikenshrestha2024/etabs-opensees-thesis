# story_mass_operator.py — optional story-master dynamic mass

**Active source:** [components/model/story_mass_operator.py](../../../../components/model/story_mass_operator.py); **physical-model owner:** [components/model/assembly.py](../../../../components/model/assembly.py); **tests:** [floor mass contract tests](../../../../tests/test_story_mass_operator_and_module_node_cases.py).

## Why this module exists

NBC 105:2025 §5.2 Table 5-1 defines directional seismic weight by floor tributaries (DL plus applicable participating live-load fractions); §5.1.1 Rayleigh uses the floor-level Wi, Fi and elastic COM displacement. A 25-row story-weight ledger is NOT evidence that the separate OpenSees solver operator is actually story-master lumped. The previous solver called `ops.mass(n,m,m,m,0,0,0)` for all source nodes, including intermediate walls. The uploaded 2026-11-22 model has 1571 active nodes and 13841.212 kN of source seismic weight between the diaphragm elevations (4.862% of the 284691.556-kN horizontal active seismic mass).

## Policies (shared model-builder switch)

- `SOURCE_DISTRIBUTED` — default, preserves distributed seismic node mass (except suppressing newly exposed artificial horizontal mass on mesh-only base points originally source-XY-restrained). Original vertical mass is preserved.
- `STORY_LUMPED_NBC` — explicit opt-in changing the solver's dynamic mass. `story_lumped_mass_plan` distributes each **source-active, non-XY-restraint** nodal mass between floor midpoint tributaries according to §5.2, checks each source floor's mass centroid aligns within 1 mm of the diaphragm master, and computes its polar `Jz=Σm((x−xmaster)^2+(y−ymaster)^2)`. It then assigns `Mx=My=sum m` and `Rz=Jz` at the respective rigid floor master. Source vertical mass remains at its original nodes. This changes the kinetic energy and modal frequencies compared with distributed walls; independent ETABS/OpenSees modal and mode-shape validation is REQUIRED.
- All mass policies retain full gravity-comparison load vs seismic preload/weight isolation. Source floor weights are required to match the assembled `NBC105_ESM_Story_Weights_Assembled_V118.csv` story-by-story within 0.01 kN for condensed cases; no missing data or mismatch may be silently accepted.

**Caution:** Translational centroid agreement and conserved polar inertia in a lumped diaphragm are necessary bookkeeping, not sufficient evidence of unchanged dynamic response, vertical mode shapes, physical wall constraints, seismic drift or natural periods. In particular, the intended 32 foundations + 44 shear-wall mesh points require correct native wall auto-edge/MPC load transfer, and full building ETABS equivalence remains NOT_VERIFIED. Do not report Rayleigh periods of the previous 76-restraint gross-shell model for a new mass policy without actual reanalysis.
