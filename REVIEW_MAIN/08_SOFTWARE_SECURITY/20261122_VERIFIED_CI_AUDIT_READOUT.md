# Integrated engineering and migration audit — verified GitHub CI readout

**Date:** 2026-11-22  
**Audited change:** PR [#143](https://github.com/bikenshrestha2024/etabs-opensees-thesis/pull/143), merged to `main` as `480d768bb3a41a49c12111ecb3507d2fd36e0048`  
**Evidence:** [Integrated static workflow run 45000278995](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/45000278995) (successful; artifact retention is finite)

## Actual machine-generated counts

The successful integrated static audit reported:

| Category | Result | Interpretation |
|---|---:|---|
| Active production Python scanned by cross-module audit | 396 | Static AST only; tests are separately included in dependency inventory |
| Source/test Python modules with imports checked | 684 | 0 explicit local targets unresolved |
| Direct local import edges | 827 | Includes more complete relative-import resolution |
| Eager-only import cycles | 0 | Not a guarantee of runtime call-order correctness |
| Deferred/conditional possible cycle groups | 6 | Startup/callback tests required |
| Dynamic-import review records | 92 | Name resolution not fully static |
| Active shadowed definitions | 0 | AST group checked |
| Cross-file AST-identical function-body groups | 32 | Separate semantic adjudication is open |
| Potential file read call sites | 724 | Conservative AST count |
| Potential file write call sites | 1,149 | Conservative AST count |
| Active sources needing producer/consumer follow-up | 292 | NOT all 292 proven broken |
| Legacy executable/configuration string matches | 82 | Some may be intentional read aliases or scanner constants |
| Additional legacy documentation/docstring matches | 13 | Not executable by themselves |
| Existing source-review attestations with valid identity | 13 | Attestation integrity is not independent complete semantic review |
| Independently completed full semantic reviews recorded | 0 | Full independent coverage remains incomplete |

The tracked-tree inventory covers the full repository including historical snapshots and generated evidence. The previously reported 383 exact-blob duplicate groups and 461 additional identical file paths were counted against main `9c708f448903a7e9d097d5299a5f137dd9d75890`. Duplicate content **does not prove** that two historical outputs or compatible entrypoints can be safely removed.

## Correction already merged

Two scanners previously omitted `from .` and `from ..` edges in their own cross-stage import/migration summary. A shared, non-executing module resolver now feeds `tools/audit_cross_module_consistency.py` and `tools/audit_output_writer_reader_pairs.py`. `tests/test_source_dependency_edges.py` validates relative package targets, no fabricated imported-symbol submodules, and cross-owner output audit edges. All six associated GitHub workflow runs completed successfully; these are static/fixture-based results.

Full line-level registers and candidate groups are in the CI artifact at `audit/integrated/02_DEPENDENCIES`, `10_MODULE_CONSISTENCY` and `12_MIGRATION_QUEUE`. The artifact is a point-in-time queue and has not been promoted into numerical authority.

## Engineering and migration acceptance remains OPEN

- **P0 gravity:** full independent 32/76/97 native support results, 6-DOF common-cut resultants, pointwise ETABS/OpenSees reactions, beam-force parts and restraints are missing or discrepant. See [#140](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/140). Equal scalar total reactions is not structural equivalence.
- **P1 saved-output migration:** each real writer/reader pair must reopen a hash-pinned run across ETABS export, Model, Gravity, ESM, Modal, MRSM, LTHA, NLTHA, NBC, comparison and viewer. Legacy readers and historical files must remain accessible. See [#141](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/141).
- **P1/P2 duplicates:** inspect each of the 32 active cross-file function clone groups, preserve compatibility shims, and only refactor after call/output parity tests. See [#142](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/142).
- **Current 12 m model:** a private selected V10.7 workbook's filename is not source authority. EDB SHA-256, exported two 12 m X walls and opening geometry, current workbook formula/cell validation and ULS/SLS status must be established together; do not silently reuse prior scaling sheets.
- **NBC 105:2025:** exhaustive code clause, table, exception, Annex and actual building acceptance remain unverified.
- **NLTHA:** first-step X-wall nonfinite localForce problem, model calibration and full M0–M6 run acceptance remain unresolved.
- **Release:** Windows ETABS/OpenSees/Spyder GUI, source-matched full solver reruns, and saved-case migrations were not performed in GitHub CI.

**Safety:** The repository was not bulk-migrated and no EDB, private spreadsheet, source user path, historical result, or solver output was deleted or replaced. Preserve immutable input digests and case-specific acceptance flags. Native project data must stay local unless separately approved for disclosure.

To perform the documented local, read-only inventory on a genuine current export, run:

```powershell
python tools/RUN_FULL_OUTPUT_MIGRATION_AUDIT.py --export-root "D:\\PATH\\TO\\EXACT_ETABS_EXPORT"
```

That command reports incomplete acceptance until source-specific writer/reader and numerical evidence is supplied. An exit code of 2 is not proof that a source file has been corrupted.

The lasting audit boundary is recorded in [the integrated engineering and migration audit](20261122_INTEGRATED_ENGINEERING_AND_MIGRATION_AUDIT.md), the [relative-import fix](20261122_RELATIVE_IMPORT_GRAPH_CORRECTION.md), and the architecture [module policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md).
