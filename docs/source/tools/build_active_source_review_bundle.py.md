# Active public source review snapshot builder

Source: `tools/build_active_source_review_bundle.py`.

**Purpose:** enable current-HEAD inspection of complete active Python sources and their callers without exposing ETABS source EDB, private Excel, ground-motion files, research datasets, historical binary outputs or archived snapshots. It is a repeatable temporary **source review input**, not engineering approval.

Run `python tools/build_active_source_review_bundle.py --repo . --output audit/source_review/ACTIVE_PUBLIC_SOURCE_REVIEW.zip` from a clean Git checkout. The tool refuses tracked changes, linked source paths/ancestors, existing output overwrite, and current-tree known-token pattern candidates. Selection is limited to root `*.py`, `components/**/*.py`, `src/**/*.py`, `tools/**/*.py`, `tests/**/*.py`, plus explicitly listed `AGENTS.md`, `engineering/rules/CORE_RULES.md` and `engineering/rules/ENGINEERING_GATES.md`.

It records `git_head`, exact per-file SHA256, size and explicit `SOURCE_PRESENT_NOT_SEMANTICALLY_REVIEWED` in the ZIP manifest. It never includes any EDB, XLSX, source model JSON, private dataset, recorded accelerogram, generated solver output, or historical snapshot. It cannot prove that source code contains no embedded credentials; the current tracked-tree pattern scan is a limited preflight.

The integrated CI uploads the archive as an Actions artifact (`active-public-python-source-review`, retention 7 days). Do not add this ZIP to the public git tree. `tests/test_active_source_review_bundle.py` confirms all allowed source, disallowed archive/data and linked inputs. Actual manually verified line-by-line semantics, linked callers, P-Delta, nonlinear, solver and ETABS comparison require separate review evidence tied to the bundle manifest. NEVER describe this ZIP creation as completed code review.
