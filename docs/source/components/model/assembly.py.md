# assembly.py — source-model assembly and E-SFI node orientation

**Implementation:** [assembly.py](../../../../components/model/assembly.py), notably `_wall_panel_nodes`, `_mesh_areas` and `build_complete_model`.

- **Source:** actual ETABS export geometry, family tags, material/section records, wall quads and opening mesh, kg/kN-m-s consistency.
- **Geometry contract:** wall quad must be bottom-first; i→j wall width horizontal; i→l storey height vertical upward; 4 counterclockwise corners, normal and nondegenerate area. Correct source *node topology* is essential; no automatic triangulation/reconstruction of nonparallelogram wall openings.
- **Numerical element:** `ops.element('E_SFI_MVLEM_3D',tag,*nodes,m,'-thick',...,'-width',...,'-mat',...,'-Density',0.)`. Width uses actual i–j distance in metres; do not use diagonal or storey-height length. Mass is assigned separately to nodes and must be audited against ETABS source.
- **Material warning:** Current research constructor still assigns nominal unconfined frame and PEER/M30 wall benchmark values. It does NOT implement validated boundary/web project material cards; the thesis intent is now correctly blocked at source input, not an auto-approval.

**Native evidence needed:** project ETABS model and openings schedule, verified frame/wall reinforcement and confinement, source gravity/mass, individual FSAM cyclic wall element and full 3D core. Do not repair a nonfinite value by silently inventing stiffness or altering source geometry. [P0 review](../../../review/01_WALL_GEOMETRY_MATERIALS_FIRST_STEP.md).

Source: [OpenSees E-SFI 3D](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html); [NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf) §§9.3.1–9.3.3.
