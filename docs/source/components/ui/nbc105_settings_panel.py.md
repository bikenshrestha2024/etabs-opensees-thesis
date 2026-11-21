# NBC 105:2025 settings panel V12 — source-aware, project-specific reference

**Date:** 2026-11-14. **Source:** `components/ui/nbc105_settings_panel.py`.
Official NBC source: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
See NBC §§3.4–3.7, 5.1–5.2, 5.5, 6.1–6.5, 8.1.1 and 9.3.

## Why the old window was misleading

The former `application.py::_open_nbc105_settings` placed NBC code stiffness, IS project adoptions, solver algorithms, load combinations, ETABS-pattern-name defaults and P-Delta requirements inside **one long Treeview**. A viewer could mistake an unverified OpenSees solver preset or the display-only `0.25/0.35` conventional-slab choice for a proven source-model assignment. Table columns labelled "ULS combination/factor" also contained unrelated parameters such as RCM constraints. The previous panel showed no selected export SHA or active Python implementation path.

The V135 screenshot also shows `OpenSees_Analysis_Results/Design_Checks_V135` with new-looking files. That **does not by itself prove the current `main` writer is at fault**: the current `components/validation/design_checks.py::run` writes newly generated V135 reports to `09_SOFTWARE_DIAGNOSTICS/DESIGN_CHECKS_V135`, while preserving nonempty manually edited historical criteria for read-only fallback. Running a stale local checkout, a copied `Saved_Project_V156` runtime or an old launcher can recreate the legacy output. Do not delete or move those files without a verified source/consumer crosswalk.

## New GUI

`application.py::_open_nbc105_settings` calls the source module directly; six tabs separate:

1. **Review & project** — project-mandatory conventional slab IS 16700 Table 5 strength/serviceability `0.25/0.35 Ig` (gross membrane area and unchanged physical weight); signed initial IS §7.2(d) X+/X−, Y+/Y− cases; project-dependent wall, gravity, nonlinear and mesh evidence marked NOT VERIFIED.
2. **NBC code & combinations** — explicit NBC effective stiffness Table 3-1, torsion only for *compatibility*, LSM §3.6 parallel and 100/30 nonparallel combinations, period/Aw/Rayleigh, seismic weight, ESM Fi/k and drift. CBC/IS sources are not silently presented as NBC requirements.
3. **Mass source & patterns** — NBC §5.2/Table 5-1 factors separated from gravity combinations and actual configurable ETABS pattern names. Roof live excluded; asymmetric rotational mass needs real mass-weighted coordinate data.
4. **Current model audit** — reads `components.validation.settings_audit.audit` for the **selected export's config** and preserves its current status/basis; displaying a stored modifier is not evidence of its native application.
5. **Mechanics & solver** — universal equations and OpenSees solver presets labelled *not NBC-specific* or *UNVERIFIED*.
6. **Runtime & folders** — exact Python source path, selected export, source SHA256, expected V135 canonical destination, legacy destination, and observed report-placement diagnostic.

The window includes a notebook/tab search, horizontal and vertical scrollbars, a selected-row detail pane, copy, refresh and local **Export JSON + formatted Excel** action. It does not execute solvers or edit the ETABS `.EDB`, original NBC Excel, OpenSees source model, or historical V135 criteria.

## Reproducible output

Explicit export writes **new** locally timestamped `NBC105_Settings_Reference_<UTC>.json` and `.xlsx` under `09_SOFTWARE_DIAGNOSTICS/ANALYSIS_SETTINGS`. The workbook uses the repository's common `style_workbook` formatting and separate tabs. It contains user-project source paths; **do not commit/upload** local evidence without removing sensitive details.

V135 window now displays `Path(__file__)` and the actual new output directory. It resolves nested stage-folder selections to the active export root instead of creating another shadow results folder.

## Distinguish reference and acceptance

- An NBC/IS reference row does **not** demonstrate the generated OpenSees shell, material, mass or support actually implements it.
- NBC Table 3-1 covers **flat slabs**, not a general conventional RC slab. The selected project **requires** documented conventional slab IS Table 5 `0.25 Ig` ULS / `0.35 Ig` SLS as separate source; do not apply these directly to nonlinear constitutive materials.
- IS §7.2(d) signed initial cases are the user's **required project gate**, not a renamed NBC seismic combination. Audit convergence/source state and do not double-count static earthquake preload and transient motions.
- (A_w) wall opening treatment remains controlled by the user's original workbook with source cell/SHA provenance; this settings viewer prints the formula but **does not replace that calculation**.
- User needs local Windows native verification for source-matched ULS/SLS shell modifiers, mass/Jm, 32/76/97 supports, MESH_04/08/16 gravity reactions, stiffness and nonlinear materials.

## Tests

`python -m unittest discover -s tests -p "test_nbc_settings_panel_v12.py" -v`

Tests are deterministic synthetic config/file checks; an actual Windows Tk smoke test (tabs, scrolling, exported workbook, local launcher source path, 125% DPI) is still required.

## Clause 1–10 reference calculator — source-routed

The existing `launch(parent, export_dir)` panel now includes an **NBC clauses 1–10** button. It opens a local dialog listing each independently registered module's exported rule functions and accepts named JSON parameters. It calls `components.nbc105.dispatch.run_operation`; it does **not** duplicate clauses in GUI code, make an ETABS change, or issue building acceptance. Result status is `CODE_CALCULATION_ONLY_NOT_BUILDING_ACCEPTANCE`. Invalid input shows BLOCKED. The initial example uses Table 10-1 `a_p` for `T1=1.0 s`, `Tp=1.25 s` and produces `1.75`.

Tests: `tests/test_nbc105_gui_clause_routing.py` plus `tests/test_nbc105_module_dispatch.py`. A native Windows tkinter smoke check remains required before production GUI acceptance.
