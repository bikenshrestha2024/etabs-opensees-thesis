# tests/test_literature_code_map.py — source guide

**What/when:** unit tests for `tools/audit_literature_code_map.py`, run in the headless pytest suite and before documentation updates.

**Why/how:** a temporary repo-shaped fixture checks ID, DOI and string-literal handling and the CSV order. Real-repository tests check that two runs produce identical text, that R01-R13 all appear, and that the committed `docs/validation/LITERATURE_CODE_MAP.*` is current. A guard test patches the network entry points and file opening to show no network call and no PDF read, and that an output directory outside the root is refused. A static test checks the tool imports no network modules.

**Where:** `tests/test_literature_code_map.py`, `tools/audit_literature_code_map.py`.

**Which:** fixture files only for behaviour checks; the committed map for the currency check.

**Who:** maintainer owns regression; the committed map must be regenerated when citations change.

**Run:** `python -m pytest -q -p no:cacheprovider tests/test_literature_code_map.py`.

**Status:** navigation and provenance test only; not engineering validation.
