# 12 Nov 2026 — ESM GUI, ETABS identity, combined export and physical-joint review

**Status:** UI + evidence export implemented on review branch; native Windows/ETABS model verification PENDING. The existing modal and ESM source model analyses were NOT rerun and cannot be declared accepted by this software-only change.

## Source observations and outstanding engineering decisions

1. ESM ULS source runs report X V=25,659.046 kN, k=1.7406 and Y V=26,450.735 kN, k=1.7110, with adopted T1-X approximately 1.9812809 s and T1-Y approximately 1.9219798 s. These are computed applied lateral profiles and are **NOT** native ETABS matched recovered story shear.
2. NBC 105:2025 §3.2.1 ULS equivalent static **COMPARISON ONLY** for this ~95 m building; this does not replace MRSM/NLTHA. NBC §4.1.3.1 requires measured Vs30 for this height; missing project geotechnical evidence still blocks site acceptance.
3. Source-model X-wall effective area has competing interpretations: historical linked original workbook Aw-X=1.95829363 m² using four 6m bay records; grouped two continuous 12m wall candidate Aw-X=2.07317452 m² from OpenSees shell geometry; continuous-pier-only candidate Aw-X=1.93063712 m². Y is 2.20308033 m². **Do not adopt a candidate solely because an audit has successfully read its coordinates.** Verify all first-storey wall boundaries and 2m openings, then independently check the approved NBC wall grouping formula and authoritative source workbook/EDB identity. Earlier B4 EDB paths differ, and path spelling equality alone is weaker than matching SHA256.
4. Clicking direct ETABS comparison with arbitrary source metadata JSON previously raised "'list' object has no attribute 'get'". Mapping files are dedicated objects with source_edb, assumptions_verified and a cases list, **not** arbitrary source metadata arrays, exported record lists or OpenSees node mappings. The UI now creates a discoverable *incomplete* ETABS_API_Mapping_TEMPLATE.json; it does not silently fabricate native ETABS cases. Selected EDB and mapping EDB must still match.
5. Direct ETABS API implementation currently has native MODAL/MRSM case extraction. It must not present an ESM applied force chart as a verified ETABS response or infer ESM case equivalence without matching explicit native case, analysis basis and story mapping.

## Gravity load-path connection

The 8,652.444 kN original gross-beam/clear-length candidate and 19,358.527 kN multi-joint geometric overlap estimate are **different auditing conventions** and must not be summed or removed automatically. A controlled full beam–column joint and beam–shear-wall joint audit is the right next local test:

- Extract exact ETABS analysis member clear lengths, insertion points, rigid-end-zone factors and shell joint intersection geometry; establish all object owners and material self-weight multipliers.
- Map original source member IDs and material/section assignments to OpenSees frame and shell tags. Audit volume once per frame/shell, not just bounding-box overlap; check columns and walls above and below the intersection.
- Isolate one matched physical bay in each system: a unit pressure to slab, frame line load and self-weight cases; calculate nodal/element joint force equilibrium in six DOFs at connected boundaries and compared end stations.
- Independently check diaphragm equalDOF constraints, shell mesh edge sharing, auto-mesh restrained nodes, member stiffness/offsets, source load pattern and local axes.
- Record ETABS and OpenSees six-DOF reactions at original 76 source restraints with identical origin/sign convention. Global 311,367.31388-kN gravity equilibrium is necessary but insufficient.

The supplied XLSX files (Slab_Load_Path_Formulas_V141, OpenSees_Property_Element_Load_Audit_V125, ETABS full export and native assignments) are reference evidence and not modified. This code-only PR does not claim to certify their complete beam–column/beam–wall member-by-member reconciliation.

## User-facing ESM changes

- Replaced the 18-action crowded footer with persistent Calculate, Run, Stop and Combined Export actions. Secondary actions are organized in ETABS comparison, Wall / period sources and Plots / reports / files tabs.
- Added text-and-color process status without conflating green FINISHED with code acceptance: blue running/exporting, green completed/exported, amber cancelled and red blocked/failed.
- Stop button already terminates the active OpenSees child process and preserves earlier results; now explicitly reports cancelled rather than generic blocked. It does not force-terminate in-process ETABS COM or source Excel work, which still needs a separate safe cancellation contract.
- New **Export combined Excel + ZIP** creates independent ESM_Organized snapshots. Each ETABS Linked / OpenSees Direct tree includes state/case subfolders and JSON, Excel, CSV, PNG, Scripts, Logs. Provenance SHA256 and original source path per copied file. Original exporter outputs remain in place to protect direct-run script and comparison references.
- The combined Excel includes case-by-case T, Aw, Ch, Z, C, Cd, W, V, k and eligibility, floor h, Wi, Wi*h^k, Fi, input source and explicit validation gates. It cannot substitute for native solved dynamic responses or authoritatively certify NBC §6 compliance.
- ETABS comparison dialog now includes a template creation control, error on wrong JSON types, and explanatory EDB mismatches; the exact EDB identity gate is preserved.

## Acceptance gates

| Gate | Status |
|---|---|
| Source code compiles / unit tests | CI REQUIRED before merge |
| Native Windows Tk actions/scroll/DPI/Stop | PENDING |
| Original user ETABS and source workbooks preserved | Yes; code change does not write originals |
| Source EDB hash and real case/story map | OPEN |
| ESM ULS design method and Vs30 | COMPARISON ONLY / OPEN |
| Beam–column/wall joint accounting + local load path | OPEN |
| Modal/MRSM/ESM model equivalence | OPEN |
