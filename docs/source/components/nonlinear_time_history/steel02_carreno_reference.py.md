# Steel02 Carreño et al. 2020 — provenance-restricted research candidate matrix

**Source module:** `components/nonlinear_time_history/steel02_carreno_reference.py`

**Original paper inspected:** R. Carreño, K. H. Lotfizadeh, J. P. Conte and J. I. Restrepo, “Material Model Parameters for the Giuffrè–Menegotto–Pinto Uniaxial Steel Stress–Strain Model,” *Journal of Structural Engineering*, 146(2), 04019205 (2020), DOI [10.1061/(ASCE)ST.1943-541X.0002505](https://doi.org/10.1061/(ASCE)ST.1943-541X.0002505). Uploaded user PDF: 21 pages; parameters from **Table 12, printed journal page 04019205-16, PDF page 16**. Do not redistribute uploaded publisher PDF or upload it to the public repository.

## Exact paper values and transfer restrictions

Table 12 gives **unmachined ASTM Grade 60 reinforcing bars**, not Nepal Fe500 project tests:
- ASTM A615: E=202 GPa, expected Fy=480 MPa, b=0.020.
- ASTM A706: E=202 GPa, expected Fy=476 MPa, b=0.012.
- Both: R0=20, cR1=0.900, cR2=0.080; isotropic a1=0.039, a2=1.0, a3=0.029, a4=1.0.

Official OpenSees Steel02 documentation lists example/recommended default cR1=0.925 and cR2=0.15, while a1/a3 default to 0. Paper outcomes are **empirical study estimates for the tested standards**, not OpenSees defaults or universal Fe500 parameters. Paper's validation coupons are separate from the original calibration set, but the paper does not qualify specific Nepal-supplied bars.

## API

- `build_carreno_study(nominal_fy_mpa=500.0)`: returns the current original Fe500 nominal material card unchanged, a Fe500 **shape-only** scenario with R0/cR1/cR2 transferred from Carreño while retaining original Fe500 Fy, E, b and zero isotropic hardening, and **separate** paper-exact A615/A706 reference cards.
- `write_carreno_study(path)`: writes strict JSON to an explicit target with atomic_json; it does not choose input/output folder by itself.

All candidate entries are `auto_apply_to_building=False`; all report flags indicate **research-only, no native OpenSees solver, no design approval**. The paper's a1/a3 isotropic parameters are in the **paper-exact** reference cards, not auto-installed into the actual frame/SteelMPF building wall. The current `components/sections/definitions.py` frame Steel02 call uses only Fy, E0, b, R0, cR1 and cR2, so claiming the full paper isotropic response is incorporated in an analysis would be false.

Both MPa and kN/m² forms are identified; 1 MPa = 1000 kN/m². A valid project cyclic protocol or laboratory coupon is required to judge Fe500 transfer. Altering Fy or adding a1/a3 to the physical building must remain a separate source-verified, code-reviewed and regression-tested feature.

## Related safety correction

`research_building_materials.validate_material_overrides` previously permitted cR1 up to 50 for frame Steel02 and wall SteelMPF, although an absolute Menegotto coefficient a1=18.5 had already been documented as causing a nonfinite response when passed directly instead of the normalized parameter cR1=a1/R0=0.925. New restricted bounds reject cR1 >=1 in the explicit research override, and direct frame-section validation guards its input too; this does **not** alter prior valid baseline values or the default Steel02 material code.

## Tests and physical acceptance

`tests/test_steel02_carreno_reference.py` verifies exact paper values, source distinction, unchanged nominal Fe500 strength/postyield/isotropic terms in shape-only scenarios, correct units, output non-approval, invalid input rejection, and false a1→cR1 assignment.

A passing source test is not hysteresis simulation. Next native OpenSees work must compare standalone Steel02 coupon cyclic loops under a defined strain protocol (stress/strain/hysteretic energy), then an isolated wall/FSAM material test, then the first-storey source wall with identical mass/constraints and ZERO/X/Y/XY excitation. Do not reinterpret a failed solver step as evidence favoring one uncalibrated constitutive model.

**Citation context:** official [Steel02 documentation](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/Steel02.html); source model [E-SFI-MVLEM-3D](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html), wall tangent improvement research identified in 2026 (see review file).
