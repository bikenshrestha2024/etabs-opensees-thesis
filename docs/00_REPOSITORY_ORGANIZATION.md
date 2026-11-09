# 00 — Work-order naming and repository organization

## Applied
Canonical root entry points are listed in the [current program index](programs/00_PROGRAM_INDEX.md); numeric gaps are intentional. Their previous names are forwarding aliases for compatibility. Each has a Markdown guide in `docs/programs/`. The previous state is saved in `backup/pre-workorder-rename-20261103`.

## Stable names required
Internal `components/` modules must keep importable module names and their data filenames until dependency graph and regression audit. Experimental records, archived reports and binary outputs are not executable programs and should not be mechanically renamed by run sequence, as that could invalidate paths or provenance.

## Deferred priorities
1. Scan static and dynamic imports, file references and Windows path dependencies.
2. Address first-step nonlinear failure around element 110280; diagnose causality, not just failed tag.
3. Repair RSA source versus runtime import path discrepancy and verify gravity/mass/constraint reconciliation.
4. Add automated launcher smoke tests, native solver benchmarks, complete nonlinear history gates and cancellable solver process.
5. Move historical root reports to versioned archives only after references and provenance checks.

Renaming did not change solver algorithms or validate numerical output.

[Rename map](00_WORK_ORDER_RENAME_MAP.md) · [Program index](programs/00_PROGRAM_INDEX.md)

## Notation and naming contract

- Launcher `NN_`: a stable tool ID, not an execution counter. Use the current index.
- Evidence stage `00`-`09`: an engineering dependency category in the canonical map.
- Gate `G00`-`G10`: acceptance conditions in the thesis acceptance register.
- `Vnnn`: a historical release/source identifier; it does not establish current compatibility.
- `ULS` / `SLS`: retain explicit limit state in run metadata and result names.
- `XY` / `YX`: simultaneous horizontal component assignments, not signed force cases.
- `E0` / `Eplus` / `Eminus`: centered / positive / negative accidental eccentricity;
  retain the method-specific sign convention and perpendicular breadth in metadata.
- Gravity profile and seismic mass factors are separate fields. A full 1.0D+1.0L
  gravity comparison is not automatically a seismic preload.

Do not bulk rename importable modules, evidence artifacts or legacy aliases.
Add new behavior to its owning `components/` package. Consolidate duplicate
implementations only after comparing callers, input/output contracts and tests.
