# Current-HEAD complete tracked-file inventory — not a semantic review

Run `python tools/audit_tracked_review_coverage.py --repo .` from a current clone to enumerate **all files tracked in the Git index** (root launchers, active components, tools, tests, archives, documentation and workflow configuration), not just active Python sources. It reads the exact Git blob SHA and file mode, records the source HEAD and whether tracked worktree files differ from it, and categorizes each entry. It does not read or copy native structural source files or execute arbitrary project Python.

**Critical scientific restriction:** Every newly generated entry starts as `NOT_REVIEWED_CURRENT_HEAD`, regardless of whether static AST inventory, CI, earlier snapshots or file documentation exists. The Git blob SHA is not a PEER record / Excel / EDB SHA256. To transition a file to semantic-reviewed status, an engineer must inspect the exact current blob, document inspected line ranges/functions, numerical units, physical assumptions, caller/reader paths, regressions and (where applicable) native evidence in the existing human review ledger. This tool never self-certifies review coverage or ETABS–OpenSees acceptance.

Optional `--export "<LOCAL_SELECTED_ETABS_EXPORT>"` writes a **fresh private-local** report under:

```text
09_SOFTWARE_DIAGNOSTICS/REVIEW_REGISTERS/RUNS/<UTC_RANDOM>/
├── JSON/Tracked_Review_Coverage.json
├── CSV/Tracked_Review_Coverage.csv
└── REPORT/READ_FIRST.md
```

It refuses a selected export destination inside the public source checkout and refuses linked intermediate diagnostics folders. Do not commit generated CSV/JSON with private case details; do not move historical files based solely on this inventory. This tool supplements `tools/audit_active_repository.py` and the frozen `docs/review/ledger/` snapshots rather than replacing them.

Test with `python -m unittest tests.test_tracked_review_coverage_v23 -v`. Native ETABS, OpenSees, Tk GUI and solver equivalence are never invoked.


## Coordinated source-tree coverage correction (2026-11-15)

The tracked-index categorizer now includes active `src/**/*.py` alongside root, components and tools. It also labels `Verification_V*/`, `Worked_Example_V*/` and `Research_Components/` as historical/snapshot metadata rather than generic files, aligning the provenance basis with `tools/audit_repository_integrated.py`. The correction changes only classification, not the underlying Git index paths, file digests, semantics or the explicit all-files `NOT_REVIEWED_CURRENT_HEAD` status. Regression `tests/test_tracked_review_coverage_v23.py` covers the revised taxonomy and counts; the integrated workflow executes it.
