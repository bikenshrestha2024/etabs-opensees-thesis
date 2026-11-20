# tools/audit_literature_code_map.py — source guide

**What:** offline map from each reference (R01-R13 in `docs/00_RESEARCH_REFERENCES.md` and each ID or DOI in `LITERATURE/MASTER_LITERATURE_INDEX.csv`) to the `components/`, `src/` and `tests/` Python files that cite it, or `UNIMPLEMENTED` when none does.

**When:** after adding or removing a `[REF R##]` tag, DOI citation or master-index row, and before merge. `--check` exits 1 when the committed map is stale.

**Why:** the existing `LITERATURE/tools/audit_source_citations.py` indexes DOI and URL strings only. This tool adds register IDs, `[REF ...]` tags, comment and docstring IDs, and the code versus tests split, so unreferenced sources are visible. It is registered in `engineering/registry/CANONICAL_MODULES.csv` as NEW_WITH_JUSTIFICATION.

**How:** Python 3.12 standard library. Scans `*.py` by filesystem walk in sorted order (not `git ls-files`), so the output depends only on file content. IDs count only inside `[REF ...]` tags, comments and docstrings (plain string literals such as test data do not count). DOIs match case-insensitively with alphanumeric boundaries. Writes `docs/validation/LITERATURE_CODE_MAP.md` and `.csv`, byte-identical across runs, no timestamps. The output directory must be inside `--root`. It opens no PDF, uses no network and imports no solver.

**Where:** source `tools/audit_literature_code_map.py`; outputs `docs/validation/LITERATURE_CODE_MAP.{md,csv}`; tests `tests/test_literature_code_map.py`.

**Which:** only the two metadata files above and Python source files; `tests/test_literature_code_map.py` is excluded from scanning because it names every R-ID on purpose.

**Who:** software maintainer owns the tool; the thesis author owns the hand-reviewed [gap register](../../validation/DAMPED_OUTRIGGER_NLTHA_GAP_REGISTER.md).

**Limitations:** a citation is provenance, not validation. Author-year citations without an ID or DOI are not detected. `UNIMPLEMENTED` means not cited in the scanned folders; it does not mean the source is unused elsewhere (documents, notebooks, root-level scripts).

**Run:** `python tools/audit_literature_code_map.py` (write) or `python tools/audit_literature_code_map.py --check`.
