# 00 — Duplicated source routes and physics-equivalence checks

This is a specific engineering risk inventory, not a claim that duplicate modules are defective. An apparently identical analysis must be demonstrated by geometry/material/response mapping, not identical file names.

| Case | Source A | Source B | Required proof |
|---|---|---|---|
| Nonlinear wall meshing | components/model/assembly.py | components/sections/area_elements.py | Same original quad; same macro-fiber widths, thickness, material tags, local axes, node winding and cyclic panel force/displacement |
| Material libraries | components/nonlinear_time_history/research_building_materials.py | Material_Catalog JSON + Define_Section_V109.py | Same nominal versus calibrated profile, MPa→kN/m2 conversion, specimen vs project steel/concrete |
| Time-history status | components/nonlinear_time_history/building_exploratory.py | components/validation/nonlinear_performance.py | Verified evidence schema and signoff; do NOT automatically change COMPLETED_EXPLORATORY_RECORD to COMPLETED_FULL_RECORD |
| Gravity/modal runtime | components/model/assembly.py | preserved Saved_Project_V156 or old wrappers | Identical source SHA, namespace, loads, mass and P-Delta state; never mix legacy saved export with current modules |
| Device model | components/sections/devices.py | element mapping overrides, building model and GUI | Device axes, proper connection, calibrated K/Cd/alpha, BRB core area; recorder sign, force/stroke and energy consistency |

## Suggested numerical parity regression

Build two 1×1 wall panels with exact same nodes, material cards, imposed displacement/axial force and time stepping. Compare initial tangent, peak force, strain, hysteresis area and convergence behavior. Then assemble a 2-story frame/slab/wall/beam reduced model for joint and diaphragm compatibility. Only after equivalence passes revisit the 25-story 3D core.

## Nonlinear first-step issue

Prior V168 evidence localizes to X excitation and AREA:354/482, but does not independently prove a constitutive flaw. The first observable NaN after a failed solve is contaminated evidence. Verify wall panel tangent and constraint consistency with single-panel, ZERO and X-only independent runs.

[Main research reference register](00_RESEARCH_REFERENCES.md)
