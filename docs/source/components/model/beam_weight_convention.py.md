# ETABS beam end-offset self-weight reconciliation

[REF components/model/beam_weight_convention.py]
[REF docs/review/GRAVITY_ETABS_COMPARISON.md]

The original 2026-11-08 ETABS Material List and the OpenSees source
weight ledger show:

| Component | ETABS kN | OpenSees gross kN | Excess kN |
|---|---:|---:|---:|
| RCC beams | 45331.611 | 53984.055 | **8652.444** |
| RCC columns | 56733.868 | 56733.868 | ~0 |
| RCC shear walls | 52934.365 | 52934.365 | ~0 |
| Slabs | 44986.712 | 44986.712 | ~0 |
| SHS braces | 1280.758 | 1308.789 | 28.031 |
| All structural self-weight | 201267.314 | 209947.789 | **8680.475** |

The original ETABS Frame Assignments - End Length Offsets report
contains 750 RCC 600x800 mm beams with summed end offsets 721.25 m.
Using actual M45 concrete weight 24.992618 kN/m³:

`721.25 m * 0.6 m * 0.8 m * 24.992618 kN/m³ = 8652.444 kN`.

This identifies the overwhelming numerical source of the *gross-weight
difference*, but it does **not** prove that the ETABS automatic
self-weight calculation, every end offset, and the physical slab-beam
solid geometry all follow the same policy. The opt-in gate is explicit
to avoid accidental correction in a different model.

## Model configuration

`OpenSees_Complete_Model_Config_V118.json`:

- `"etabs_beam_weight_policy": "GROSS_SECTION_LENGTH"`: **default**;
  unchanged historical model and diagnostic report.
- `"etabs_beam_weight_policy": "ETABS_BEAM_CLEAR_LENGTH"` plus
  `"etabs_clear_beam_weight_confirmed": true`: enabled after reviewing
  the source *ETABS Frame Assignments - End Length Offsets* and material
  list. Missing or invalid end-offset data raises an error instead of
  silently reverting to gross length.

A per-ETABS-object audit is exported under the same export directory:

`ETABS_OpenSees_Beam_Weight_Reconciliation.csv`
`ETABS_OpenSees_Beam_Weight_Reconciliation.json`

The mode computes each original beam's clear-weight interval
`[I_offset, L - J_offset]`, clips this to each subdivided OpenSees
frame element, and applies a **uniform distributed weight only on
that interval**, using the existing consistent-element-load integrator.
This preserves the load centroid better than multiplying each entire
element's distributed load by `L_clear/L_gross`.
All gravity patterns that include source self-weight use the adjusted
beam forces; seismic mass is derived from the same corrected source
load vectors. Other non-self-weight beam loads are untouched.

This policy does NOT change beam stiffness, local axes, frame end
rigidity, shell membrane/bending properties, slab weights, column
weights, wall weights or SHS brace section properties. It does NOT
silently add support restraints or modify ESM/MRSM/NLTHA *run settings*.
Source-derived mass will change when the verified beam-weight policy
is selected; all modal, RSA and TH results must be regenerated if it
is accepted.

**Never combine `ETABS_BEAM_CLEAR_LENGTH` and
`joint_volume_weight_policy="VERIFIED_SINGLE_OWNER"`.** Both could
deduct the same joint region. A configuration-level guard prevents this.

## Dlubal steel SHS

User-supplied Dlubal [SHS EN 10210-2 ALUKÖNIGSTAHL catalog]
(https://www.dlubal.com/en/cross-section-properties/series-shs-en-10210-2-alukonigstahl)
identifies the hot-formed EN 10210-2 square hollow-section series.
It does **not** provide a verified exact 350x350x16 section area in
the accessible catalog extract. The ETABS source section incorporates
rounded corners (24 mm radius per screenshot), while the current
OpenSees section uses a sharp-corner tube formula.
The residual 28.031 kN brace weight difference is approximately
0.009% of total full gravity load; retain the brace's source properties
until its tabulated `A`, `Iy`, `Iz`, `J`, thickness and corner
radii have been independently checked against Dlubal / ETABS.
Do NOT apply an arbitrary 28.031 kN adjustment.

## Native references

OpenSees `eleLoad` documentation:
https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/PlainPatternloadcommands/eleLoad.html

CSI ETABS End Length Offsets:
https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm

CSI ETABS Analysis Reference:
https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf

ETABS rigid-zone factor affects bending/shear stiffness; it is not
a scalar for self-weight. The source `GetEndLengthOffset` alone is
also not proof of the `Self Weight Option`. The case-by-case weight
audits and original ETABS material list are the control evidence.

## Validation gates

1. Confirm beam offset records and the source material list, and
   enable `etabs_clear_beam_weight_confirmed` only after review.
2. Rebuild the complete OpenSees model, do not only rerun the old
   generated gravity script, and inspect the exported per-beam ledger.
3. Compare loaded dead + live base reactions (ETABS ~311367.314 kN
   as observed in the 2026-11-08 source model). Do **not** adjust
   results merely to match the numerical value.
4. Compare original 76 ETABS-point support reactions using the
   `ETABS_SOURCE_SUPPORTS` strategy. The 44 null-line-only
   fixed nodes are a separate, **unresolved load-transfer/mesh
   connectivity problem**, despite accurate global loads.
5. Compare 1076 unique mapped gravity node displacements,
   and segregate 25 ambiguous duplicate coordinate mappings.
6. Preserve the original solver files, hashes, source EDB and
   before/after load provenance; run modal/RSA/NLTHA validation
   only after the corrected source weight and supports are accepted.

## Regression tests

`python tests/verify_beam_weight_convention.py`
