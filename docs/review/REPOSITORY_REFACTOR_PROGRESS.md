# Implementation checkpoint — 2026-11-10

Branch: `fix/primary-gravity-seismic-inputs`.
Source commit: `a7e26466c1613fb0db32cee88c322444167d5343` (main).
PR #13 is merged; PR #15 is an open draft with overlapping input-default work.
This branch implements the user's eight follow-up requests incrementally; the
entire V4 architecture migration is not complete.

## Completed changes

- EXTEND existing gravity GUI: 32-node primary default, private source defaults,
  explicit fingerprint-checked saved-case plot action for 32/76/97 results.
- EXTEND existing project workbook reader: SHA256-scoped private source registry;
  original engine's labelled `ETABS Sync` adopted-period outputs are readable.
- EXTEND existing ESM GUI: reuse known EDB/workbook/engine/output directory,
  prefer original matching linked audit over provisional geometric Aw,
  expose adopted periods separately from modal/Rayleigh periods, and include
  solved response-profile images in existing Matplotlib selector.
- EXTEND existing MRSM GUI: current source/state output root for viewers,
  manual full evidence ZIP, source-matched original adopted-period fallback.
- EXTEND gravity recorder: every frame/shell global end-force vector; recovered
  interface Fz and joint vertical force balance in gravity workbook and JSON.
- FIX scorecard lookup: selected run's direct comparison precedes parent root.
- Preserve solver equations, restraints for each selected case, source datasets,
  old scenario identifiers, compatibility imports, and all historical results.

## Executed verification

- Initial focused regression: 39 tests plus 5 subtests passed.
- Static active inventory: 416 modules, no syntax errors, missing canonical
  launchers or missing source guides at execution time.
- Native Tk gravity construction: primary 32 default and both workbook entries
  populated from the local source registry.
- Original linked workbook read: X=2.03856740011866 s,
  Y=1.9219797767063125 s (adopted design periods).
- Native OpenSeesPy 32-node run on an isolated copy: reaction
  311367.31387954945 kN, applied 311367.3138795495 kN,
  maximum downward displacement -0.021017645469009413 m.
  These reproduce supplied saved values. 14262 element vectors recorded,
  11097 joints, largest vertical equilibrium residual 3.97e-10 kN.
- Final broader gravity/ESM/MRSM regression: 197 passed plus 5 subtests.
  Native Tk workbook export succeeded: 26 recovered interfaces and 11097
  joint balances. Offline native-table/32-node reaction comparison workbook
  was also generated. All rerun displacements and support Fz reproduce the
  saved solution exactly (maximum difference 0.0).

## Engineering blockers

Local foundation reactions still differ despite matching global gravity.
Native ETABS auto offsets/rigid factor and the 32-node model's released base
points are not equivalent. The provided beam-force sheet reaches Excel's row
limit; full beam-response coverage cannot be assumed. See the investigation
report. No native ETABS solve, full seismic rerun, stiffness correction or
code/engineering acceptance is claimed.

## Already inspected instructions

User V4 prompt, AGENTS.md, CLAUDE.md, engineering migration/start guide,
CORE_RULES, ENGINEERING_GATES, MODULE_BOUNDARIES, PROVENANCE, AI_ATTRIBUTION,
thesis acceptance/reference registers, active engineering review/canonical run
order, program index, nonlinear NBC implementation guide, and module READMEs.

Next executable engineering action: reconcile actual ETABS end-zone stiffness
and internal base mesh constraints against the preserved 32-node main case;
compare new recovered frame/shell interfaces with native section cuts under
the same load discretization. Do not tune support reactions to fit totals.

Last completed commit: pending final commit of this checkpoint.
