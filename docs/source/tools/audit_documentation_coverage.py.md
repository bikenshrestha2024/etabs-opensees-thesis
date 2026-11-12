# Documentation coverage audit tool

**What:** count how many active `components/*.py` and `tests/*.py` files have nonempty matching `docs/source/<path>.md` guides. **When:** every change introducing/removing a Python module and at each thesis evidence freeze. **Why:** prevent undocumented active sources and show remaining test-guide backlog without claiming semantic coverage.

**How:** Python 3.12 standard-library filesystem scan, never imports OpenSees, ETABS or project source and never reads private model values. Writes JSON only when `--output` is requested; `--fail-on-missing-component-guides` fails CI when active component guide paths are absent. **Where:** `tools/audit_documentation_coverage.py`; generated output in `audit/documentation_coverage.json` when CI runs. **Which:** relative paths under current `components/`, `tests/`, and `docs/source/`. **Who:** maintainer maintains automation; authors and engineering reviewer check guide content.

**Run:** `python tools/audit_documentation_coverage.py --output audit/documentation_coverage.json --fail-on-missing-component-guides`.

**Limitation:** existence and file size are the only verified properties; documentation text accuracy, completeness, source DOI, person attribution, native convergence and code acceptance are NOT verified.
