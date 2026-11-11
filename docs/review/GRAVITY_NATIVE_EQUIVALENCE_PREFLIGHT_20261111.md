# Native ETABS–OpenSees Gravity support and rigid-zone preflight (2026-11-11)

## Scope and why the previous total reaction match is not enough

The user's 32-node set is the preferred primary comparison case. **It is not a
native ETABS support-equivalence certificate.** The native ETABS original export
has 76 vertical support coordinates; the 32-node case removes restraints at the
remaining 44 positions. An ETABS Fz of zero is NOT proof that U3, rotations or
other source support DOFs are free. Separately, native ETABS beams have automatic
end offsets and rigid-zone factors; clear-span beam **weight** correction does
not implement native rigid-end **stiffness**.

Existing comparison: ETABS global Fz ~= OpenSees Fz ~= 311367.314 kN, but
ETABS joint 263/264 differs by approximately 3041.266 kN per mapped reaction.
The generated element/joint balances establish OpenSees internal equilibrium
only; they do not establish source ETABS equivalence. This preflight cannot
assign cause to this difference without controlled native comparisons.

## How to run

From the intact Windows project checkout in Spyder, open
`01_WORKFLOW_START.py`, build/read the current saved export, open Gravity,
and click **Audit ETABS support DOFs + rigid end zones**.

Alternatively, from the environment with your project code:

```powershell
python -m components.validation.gravity_native_equivalence_preflight "D:\\YOUR_PRIVATE_EXPORT" "D:\\YOUR_PRIVATE_RESULTS\\Gravity_Native_Equivalence_New"
```

Do not reuse a populated audit folder. Original source files are only read.
The output contains:

- `GRAVITY_NATIVE_EQUIVALENCE_PREFLIGHT.json` — source SHA256,
  missing native evidence, source DOF/release counts and blockers.
- `SOURCE_SUPPORT_DOF_VS_PRIMARY32.csv` — original restrained DOFs at
  each source base node, primary-32 membership and mapped ETABS point.
- `ETABS_END_ZONE_STIFFNESS_REVIEW.csv` — native cFrameObj end lengths,
  auto offset and rigid-zone factor; these are **not** weight correction rules.
- `READ_FIRST.txt` — status and next controlled verification step.

The CLI can include an independently selected primary 32 audit with
`--primary-audit`. It must be for the same source export; compare SHA and
case identity. It is never auto-picked from an unrelated run.

## Next native validation sequence — *not executed in GitHub CI*

1. Verify same source EDB SHA, exact ETABS case `1. DL + LL`, active ULS/SLS
   stiffness profile, nodes/geometry/sections, support DOFs, material and
   property modifiers and total applied load.
2. In native ETABS on a private read-only *copy* when analysis is needed,
   export exact per-point support restraints and joint forces; compare
   the 32 originally reaction-bearing locations **and all other 44
   originally restrained points**. Do not release a restraint simply because
   native vertical reaction happens to be zero.
3. Reconcile exact automatic end lengths and rigid-zone factors at source
   member ends and ETABS vs OpenSees joint offsets, elastic effective
   EI/EA/GA/J and wall in-plane stiffness. Do not globally add or scale
   frame offsets to make foundation reactions fit.
4. Run explicitly separated 32-primary, 76-source-boundary and
   97-continuous-wall sensitivity configurations with identical unfactored
   `1.0D + 1.0L` input ledger, independent results, no overwritten outputs.
   Document any changed physical boundary/stiffness model as a new variant.
5. Compare source-to-solver story loads, joint equilibrium, actual recovered
   interface forces, and native ETABS individual foundation reactions.
   Use the complete native frame/shell response export: Excel sheets with
   1,048,576 rows require split exports.
6. Only after gravity load path is reconciled: independently verify ULS/SLS
   modal mass/periods, X/Y response-spectrum cases, CQC, scaling,
   eccentricities, displacement, floor/story shear and inter-storey drift.
   The project's ESM can be ineligible as **design** analysis; comparisons
   are not code acceptance.

The preflight must never mark `ETABS_OPENSEES_MATCHED` or `CODE_ACCEPTED`.
It cannot operate native ETABS from Linux CI. A converged and internally
balanced OpenSees model is not an ETABS-equivalent model.
