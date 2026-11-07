# Direct gravity ETABS API — integrated into existing Gravity GUI

[REF components/validation/gravity_etabs_direct.py]

The OpenSees gravity analysis interface (`10_GRAVITY.py`) now includes
**Extract ETABS + compare gravity**. It invokes `components.validation.gravity_etabs_direct.connect_and_compare`
without opening another app.

Prerequisites:
- The exact ETABS source EDB for the already exported OpenSees model is **open and analyzed** in ETABS v23.
- The corresponding `Gravity_Result_V110.json` exists for `GRAVITY_1.0D_1.0L`.
- An existing ETABS linear-add result combination named `1. DL + LL` (editable in the GUI) has **Dead** and **Live** as direct case inputs, each at factor 1.0. Its analysis cases must have finished.
- The source EDB path is recorded in OpenSees source manifests and matches the currently open ETABS EDB exactly.

This integration reads existing ETABS results; it never opens/saves/unlocks an EDB,
changes case definitions, or runs analysis. It temporarily chooses `kN-m-C`
units and selects case/combination results, restoring both in `finally`.

Captured: global `BaseReact()`, Dead and Live constituent `BaseReact()`
(additivity audit), all restrained point inventory, each matching `JointReact()`,
and joint displacements. It records failures explicitly rather than claiming
complete support coverage. Individual `JointReact()` F1/F2/F3 are **point-local**
and must not be summed as global Z without rotation verification. Global base FZ
is the primary gravity-force comparison.

The program uses exact case+step identity, no envelopes; it checks that the
gravity profile is **1.0D + 1.0L**, including source roof-live pressure *if it
was assigned to Live*. The two-case combo **does not prove** physical roof-live
assignment. ETABS may have foundation spring/link reactions beyond restrained
point inventory.

Output from the same GUI under:
`<gravity output>/Gravity_ETABS_OpenSees_Direct/`

- `etabs_gravity.json`
- `Direct_Gravity_Comparison.json`
- `ETABS_Base_Reactions.csv`
- `ETABS_Fixed_Support_Reactions.csv`
- `ETABS_Support_Displacements.csv`
- `ETABS_OpenSees_Direct_Gravity_Comparison.xlsx` (requires openpyxl)

Click the existing **Bundle gravity evidence ZIP** button afterward; its
archive includes the direct comparison and available ETABS results.

The direct comparison computes the base-reaction difference and percentage;
**not** member-by-member load-path equivalence or engineering acceptance.
Discrepancies in self-weight, member properties, geometric overlap and
connection stiffness remain separate checks. The module has synthetic unit
tests but still needs a native ETABS v23 test.

Tests: `python tests/verify_gravity_etabs_direct.py`.
