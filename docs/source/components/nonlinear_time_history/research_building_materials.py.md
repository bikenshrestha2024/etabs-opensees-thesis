# research_building_materials.py — research constitutive basis and strict thesis qualification

**Source:** [research_building_materials.py](../../../../components/nonlinear_time_history/research_building_materials.py). Existing `define_building_materials` uses `PEER_Web_ESFI_Patch.json` or `M30_Fe500_SFI_MVLEM_3D.json`, nominal Fe500 frame assumptions, a generic two-curtain 20mm@200mm wall reinforcement ratio, and no independently tested actual boundary confinement. The report is explicitly `LITERATURE_INFORMED_RESEARCH_NOT_PROJECT_CALIBRATION`.

New `check_project_material_qualification` prevents a `THESIS_NLTHA` run using those templates; no arbitrary `approved=true` bypass exists. Research diagnostic tests can proceed with the original clearly labeled assumptions. To enable actual production, implement and test real source-mapped frame bar coordinates, actual concrete cyclic constitutive law, web/boundary FSAM materials by region, material sensitivity, and full 3D core model. **Do not disable the gate without replacing the constitutive implementation and native validation.**

**Tests:** [verify_project_wall_material_gate.py](../../../../tests/verify_project_wall_material_gate.py). [Full engineering review](../../../review/01_WALL_GEOMETRY_MATERIALS_FIRST_STEP.md).

Sources: [PEER Report 2015/12](https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf); [OpenSees E-SFI 3D](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html); https://doi.org/10.1016/j.engstruct.2023.116700.
