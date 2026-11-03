# 00 — Work-order naming and repository organization

## Applied
20 root runnable entry points now have sequential 01–20 names. Their previous names are forwarding aliases for compatibility. Each has a Markdown guide in `docs/programs/`. The previous state is saved in `backup/pre-workorder-rename-20261103`.

## Stable names required
The repository has approximately 1,560 tracked files. Internal `components/` modules must keep importable module names and their data filenames until dependency graph and regression audit. Experimental records, archived reports and binary outputs are not executable programs and should not be mechanically renamed by run sequence, as that could invalidate paths or provenance.

## Deferred priorities
1. Scan static and dynamic imports, file references and Windows path dependencies.
2. Address first-step nonlinear failure around element 110280; diagnose causality, not just failed tag.
3. Repair RSA source versus runtime import path discrepancy and verify gravity/mass/constraint reconciliation.
4. Add automated launcher smoke tests, native solver benchmarks, complete nonlinear history gates and cancellable solver process.
5. Move historical root reports to versioned archives only after references and provenance checks.

Renaming did not change solver algorithms or validate numerical output.

[Rename map](00_WORK_ORDER_RENAME_MAP.md) · [Program index](programs/00_PROGRAM_INDEX.md)
