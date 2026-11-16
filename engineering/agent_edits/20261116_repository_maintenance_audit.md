# Thesis repository maintenance audit

Baseline: GitHub main at `1dca328ca0b8fd7d8ce0f511fc0e8777e3b4a439`. Audit date: 2026-11-16. Runtime: conda-forge CPython 3.12.11 on Windows. Editor: OpenAI Codex desktop. Exact model identifier: UNKNOWN.

## Confirmed defects and fixes

| Finding | Reproduction and cause | Fix |
| --- | --- | --- |
| Explicit stages could omit metadata for newly generated files | The integrated Windows test failed because the expected CSV timing sidecar was absent. A focused regression that advances the wall clock at finish reproduced the omission deterministically. The old timer reconstructed the start by subtracting a monotonic duration from the wall clock at finish. | Compare immediate output-file size and modification-time snapshots taken at stage start and finish. Monotonic elapsed timing and existing sidecar paths are preserved. The regression checks that an untouched file is excluded. Rewrites that preserve both attributes cannot be detected. |
| Windows test cleanup failed with a workbook file lock | The ID-audit test read a workbook with openpyxl in read-only mode. Its open handle yielded WinError 32 when the test removed the temporary directory. | Close the workbook in a finally block immediately after collecting the worksheet rows. |

Changes are in the accompanying patch. It modifies the timer, its source guide, and the two affected tests. To review and apply on a clean checkout, run `git apply --check thesis-audit-fixes.patch` followed by `git apply thesis-audit-fixes.patch` using the actual patch path.

## Verification

- `python tools/audit_active_repository.py --output audit/active_inventory.json --fail-on-missing-canonical` found 544 active Python files, zero syntax errors, zero missing canonical paths, and zero missing source guides under that tool's coverage rules.
- `python tools/audit_repository_integrated.py --repo . --output audit/integrated --fail-on-static-blockers` passed. It inventoried 3,096 tracked paths and found zero unresolved local import candidates. Its 4,050 semantic review units were machine-inventoried. The semantic-review completion counter was zero.
- `python -m unittest -q tests.test_timing_metadata_structure tests.test_id_audit_roles` passed all five tests. Before the fixes, the timing regression failed and the integrated suite reported the Windows workbook cleanup error.
- The unittest selection in `.github/workflows/integrated-repository-audit.yml` ran 136 tests before and after. Before: 123 passed, 11 skipped, one assertion failure and one error. After: 125 passed and 11 skipped.
- Scoped `git diff --check` and reverse patch application check passed. Git LFS checkout did not finish during review. Tracked-path audit used an isolated index populated from the baseline tree. Native ETABS, OpenSees engineering comparisons, Spyder GUI flows and full NLTHA were outside the local verification.

## Maintenance register

| Priority | Finding | Evidence and next verification |
| --- | --- | --- |
| P0 | Gravity support equivalence and X-direction wall first-step failure | The integrated gate carries both as open engineering findings. Re-run the repository's native evidence gates using matched, provenance-checked inputs before changing the model or accepting results. |
| P1 | Legacy output paths | 96 static legacy path references and 108 canonical path references. Trace actual readers and writers beginning with `components/inputs/output_layout.py` and `components/ui/organized_results.py`. Migrate one stage at a time with fixtures for old and new layouts. |
| P1 | Import cycles | Four static local cycles. Trace runtime entry points before changing import direction. Keep public launchers usable during any migration. |
| P1 | ESM/MRSM equivalence | The integrated gate tracks this as pending. Validate against matched ETABS case definitions and evidence. |
| P2 | Exact duplicates and facades | 403 exact Git blob groups, including 382 with historical snapshots. Review the remaining 21 groups against the canonical module registry before removing anything. The 59 dynamically executing facades merit caller tracing, with particular care around Spyder and legacy entry points. |
| P2 | Dependency drift | CI mixes conda-forge environments with pinned and unpinned PyPI installs across separate jobs. The NLTHA job pins NumPy 2.1.3, Matplotlib 3.9.2 and pytest 9.1.1. Upstream lists newer [NumPy](https://pypi.org/project/numpy/), [Matplotlib](https://pypi.org/project/matplotlib/) and [pytest](https://pypi.org/project/pytest/) releases. Test candidate versions in a separate Windows/Python 3.12 conda-forge environment against workbook, GUI, and native solver fixtures before changing pins. Package age alone does not establish an incompatibility or vulnerability. |

The audit did not move launchers, remove historical evidence, alter solver assumptions, change dependency pins, or publish a branch.
