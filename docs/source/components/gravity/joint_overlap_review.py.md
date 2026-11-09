# RCC joint volume by actual member category — comparison, not automatic deduction

Source code: `components/gravity/joint_overlap_review.py`.

This module is called during the source model build **after** the existing `build_joint_volume_ledger` has constructed its candidate geometric intersection model. It does not alter the gravity load vectors or physical mass.

## Why the 32-joint approximation is not an automatic fix

The user's 2026-11-09 trial uses 32 joints, removes 8 opening-edge joints, 2 central-core points and 4 outer-core points, giving 18 **remaining points**, not 14. Separately the user gives 14 wall junctions.

* Column example 1.1 × 1.1 × .8 × 25 kN/m³ = 24.2 kN **per junction**.
* Wall example .6 × .6 × .8 × 25 kN/m³ = 7.2 kN **per junction**.
* The wall expression ×25 storeys ×14 joints gives **2520 kN**.
* If 18 are column joints and 14 are wall joints, gross hypothesis is **13410 kN**.
* If 14 are column joints and 18 are wall joints, gross hypothesis is **11710 kN**.

These expressions are not physically verified: all 25 floor members need not have the same dimensions, a core corner may involve three intersecting walls, and an opening-edge point can be on a shear-wall pier even if no beam connects. Neither 32 mapped foundation nodes nor a 25-storey repetition produces a reliable count of three-dimensional overlapping concrete solids.

## Actual model audit

It reads the project's existing `OpenSees_Joint_Volume_Ownership_Audit.json` equivalent data, generated using source RCC frame segments and shell cells; it reports:

* `Gravity_Joint_Type_Overlap_Review.xlsx` with per-category actual rectangular-box union estimate, pairwise ownership (e.g. `BEAM_OVERLAPS_COLUMN`, `SHEAR WALL_OVERLAPS_SHEAR WALL`, `FLOOR_OVERLAPS_COLUMN`) and every source-member candidate row.
* `Gravity_Joint_Type_Overlap_Review.csv` — component-level summary.
* `Gravity_Joint_Type_Overlap_Solids.csv` — per-object or per-shell-cell gross, potential overlap and retained weight.
* `Gravity_Joint_Type_Overlap_Review.json` — evidence, assumption comparisons, flags and untouched actual program policy.

The union follows the conservative precedence `COLUMN > SHEAR WALL > FLOOR > BEAM`, but *only for supported axis-aligned centered rectangular RCC solids*. It does not infer offsets or solid geometry from 32 point IDs. `AUDIT_ONLY` is the working mode and applies **zero** changes to building gravity and mass. The potentially duplicated solid volume cannot be equated with the ETABS result difference unless native ETABS Material List and Self Weight Option establish that ETABS uses the same physical volume ownership convention.

The existing reviewed `VERIFIED_SINGLE_OWNER` policy is not turned on by this change; it requires source geometry verification and remains mutually exclusive with `ETABS_BEAM_CLEAR_LENGTH`. They are alternative counting policies, NOT additive corrections.

ETABS itself distinguishes frame end offsets from rigid-zone factors; see [CSI ETABS frame end offsets](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm). Frame self-weight settings must be verified separately. For the original user export, the reported global excess remains 8680.475 kN; previous independent material-list review identified potential 8652.444 kN beam and 28.031 kN brace differences. Do not reinterpret this as proof that all junction weight has been double counted.

**Acceptance**: verify exact ETABS source/working model identity; native beam/column/slab/wall material quantities; physical shape, insertion and cuts at every opening; no duplicate source load pattern weight; gravity 1.0DL+1.0LL total; independent support reactions and region load shares; then modal/ESM/MRSM. Avoid tuning loads to match base reactions.

Author: ChatGPT GPT-6.
