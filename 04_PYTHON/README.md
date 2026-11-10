# 04 — Python development, automation and GUI

Use Windows Python 3.12, Spyder, and the verified conda-forge environment. Keep `components/` importable for all old launchers and generated runtime scripts; no blind renames. Python source inspection and duplicate grouping are provided by `tools/audit_active_repository.py` and the new `tools/audit_module_boundaries.py`.

Run `python tools/audit_module_boundaries.py --out <private-output-folder>` for static domain/import/duplicate reports. This is an inventory, **not** ETABS/OpenSees numerical validation. Check `sys.executable`, project root and source identity before launching old downloaded scripts.

[Existing tests](../tests/) · [current work-order index](../docs/programs/00_PROGRAM_INDEX.md) · [Python guide](../engineering/topics/PYTHON.md)
