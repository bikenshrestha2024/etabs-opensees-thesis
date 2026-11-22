# research_building_materials.py — research constitutive basis and strict thesis qualification

**Source:** [research_building_materials.py](../../../../components/nonlinear_time_history/research_building_materials.py). Existing `define_building_materials` uses `PEER_Web_ESFI_Patch.json` or `M30_Fe500_SFI_MVLEM_3D.json`, nominal Fe500 frame assumptions, a generic two-curtain 20mm@200mm wall reinforcement ratio, and no independently tested actual boundary confinement. The report is explicitly `LITERATURE_INFORMED_RESEARCH_NOT_PROJECT_CALIBRATION`.

New `check_project_material_qualification` prevents a `THESIS_NLTHA` run using those templates; no arbitrary `approved=true` bypass exists. Research diagnostic tests can proceed with the original clearly labeled assumptions. To enable actual production, implement and test real source-mapped frame bar coordinates, actual concrete cyclic constitutive law, web/boundary FSAM materials by region, material sensitivity, and full 3D core model. **Do not disable the gate without replacing the constitutive implementation and native validation.**

**Tests:** [verify_project_wall_material_gate.py](../../../../tests/verify_project_wall_material_gate.py). [Full engineering review](../../../review/01_WALL_GEOMETRY_MATERIALS_FIRST_STEP.md).

Sources: [PEER Report 2015/12](https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf); [OpenSees E-SFI 3D](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html); https://doi.org/10.1016/j.engstruct.2023.116700.


## 2026-11-17 normalized transition-slope safety guard

A newly inspected P1 input-contract risk allowed experimental `frame.steel_cR1` and `wall.cR1` overrides up to 50 even though the local source confirms a NaN under the incorrect direct Menegotto a1=18.5 assignment. The safe normalized OpenSees form requires `cR1=a1/R0` for that source expression and yields 0.925 with R0=20. Only the experimental override upper bound is tightened to <1, with a direct frame-section guard so invalid inputs fail before material creation. **Baseline material files and source-verified PEER .925 conversion remain unchanged.** The user-uploaded Carreño paper recommends cR1=.9 for ASTM Grade 60. The independent source-specific research registry and paper reference card reside in `components/nonlinear_time_history/steel02_carreno_reference.py` and `LITERATURE/Reinforcing_Steel/CARRENO_2020_STEEL02_PARAMETER_CARD.md`. Tests: `tests/test_steel02_carreno_reference.py`. A valid input is not constitutive experimental calibration or a guarantee of nonlinear convergence.


## 2026-11-22 — direct PEER Appendix B.3 literature-baseline policy

The user's thesis uses directly cited published constitutive inputs as a **research** baseline and reports source-specific parameter sensitivity; separate project material testing is **not** a prerequisite for attempting exploratory NLTHA. The PEER RW-A15-P10-S78 web FSAM reinforcement ratios are now directly adopted as `rho_x=rho_y=0.0074`, with published `nu=0.8` and dowel `alpha=0.01`. Its **distinct** boundary values (`rho_x=0.0082, rho_y=0.0587`) remain recorded, NOT applied to arbitrary wall panels without a verified region map. In the isolated PEER research draft, the former invented `20 mm @ 200 mm` bar proxy no longer controls these web values; mixed/nominal sensitivity bases remain labeled assumptions. See [the full page-specific source/units table and methodological distinction](https://github.com/bikenshrestha2024/etabs-opensees-thesis/blob/main/docs/engineering/20261122_DIRECT_PEER_LITERATURE_NLTHA_PARAMETERS.md).

Source-level tests: `tests/test_peer_direct_literature_fsam_transfer_20261122.py`. This does not certify that the 25-storey X-wall first step converged, establish actual M0–M6 device input, or set `approved_for_nltha=true`.
