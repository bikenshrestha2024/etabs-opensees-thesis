# Repository semantic review checkpoint

Baseline: `b8db900d84078b3de5387bf86e2cce1cdd411ab4`. Scope and outstanding gates: [issue #75](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/75).

## Inventory and review evidence

The integrated audit classified 3,104 tracked paths, including 129 root Python entry points/helpers and 415 Python source, tool or test files. Its 4,051 source units are the review queue. The module boundary scan checked 544 files with zero prohibited imports or parse failures. The import graph found zero unresolved explicit local imports and four cycle candidates. It identified 59 execution facades. Archive provenance identified 403 exact Git blob groups, of which 382 included a historical snapshot. Historical copies remain evidence. Outputs are grouped by subject by the existing `audit/integrated` writer.

The [source review ledger](inspected_source.csv) records actual baseline line spans. A full-file mark applies to that file only. Static scanning, test discovery and a repeated archived blob confer no semantic-review credit. The 214 Python paths outside the current active inventory include archived code, calibration and diagnostic scripts. Confirm live callers and ownership for those scripts before excluding them from semantic scope.

## Changes and reproduced defects

| Area | Failure reproduced | Acceptance evidence |
| --- | --- | --- |
| Static audit | Missing runtime facade target produced a blocker finding and a passing gate | A fixture with all canonical launchers and a missing facade target now blocks the gate |
| Output readers | Legacy history outputs were found by short stage IDs but missed by equivalent canonical names | LTHA and NLTHA aliases, case and whitespace variants resolve to the same compatibility roots |
| Case manifests | JSON arrays and objects in solver status raised TypeError | Invalid status produces an issue and UNKNOWN result |
| Review archives | Bundle name could replace a per-module archive. A per-module manifest also carried totals for other modules | Case-insensitive name collision is rejected and counts match the entries in each ZIP |
| ESM publication | Windows backslashes appeared in snapshot-relative paths and read-only test workbooks blocked cleanup | Manifest paths match ZIP members and test workbook handles close |
| Slab evidence | Gross shell formula replaced the assembled source-detail retained slab weight in VERIFIED_SINGLE_OWNER mode | Synthetic 5 kN gross and 2.5 kN retained case preserves the actual ledger. The checked AUDIT_ONLY MESH_04 case used unit retained ratios |
| NLTHA comparison | Finite numeric strings passed validation, then crashed pooled maxima or compared as text | One numeric normalization feeds both pooled and grouped reductions without mutation. Matched cases must also agree on source duration |
| Horizontal acceleration | A finite input scale could overflow after multiplication by the unit factor | Converted factor must be finite before use |

CI installs the pinned openpyxl version already used by the NLTHA job and exercises the affected workbook, output and comparison regressions. Other workflow-wide dependency upgrades require isolated Windows Python 3.12 and native solver regression. No general package upgrade was applied.

## Open findings and acceptance gates

| Priority | Finding | Evidence required before closure |
| --- | --- | --- |
| P0 | 32-support gravity equivalence | Exact source EDB/case and analysis mesh, edge constraints, offsets, units, mass and loads. Match six equilibrium components, mapped reactions and local beam/wall forces at equivalent stations. Treat 76/97 as boundary sensitivity |
| P0 | X-wall NLTHA first-step failure | Preserve the failing wall tag and source mapping. Re-run fresh ZERO/X/Y/XY domains using actual geometry and project material evidence |
| P1 | Centerline-only frame split admission | Trace live node provenance and intended shell/frame connectivity. The exact 3751 and 3754 splits are supported by assembled incidences. Test an intentionally unconnected coincident node before changing admission policy |
| P1 | Potentially stale beam-end actions and ESM batch status | Pin current model and script fingerprints in run evidence. Exercise failed/empty recorder output and regenerated same-name scripts before accepting a saved status |
| P1 | MRSM saved-case evidence | Require comparable story IDs/counts and complete finite metrics under matched source/state identity. Existing six-file presence check can pass unequal incomplete story rows |
| P1 | Isolation study provenance | Match motion hashes in completed summaries and reject nonfinite achieved time before probe approval |
| P1 | Concurrent gravity reaction registrations | Verify concurrent writers preserve all successful case entries. Current registry uses a fixed temporary filename and read/modify/write without a lock |
| P1 | Legacy output paths and import cycles | Classify 96 legacy path references by reader/writer and confirm four potential cycles by runtime entry point. Migrate one stage with compatibility fixtures for legacy and canonical routes |
| P2 | Dependency alignment | Identify CI resolver ownership, compare pinned and floating environments, and rerun Windows workbook/GUI and native OpenSees checks before changing solver-sensitive versions |
| P2 | Further semantics | Review remaining active source, workflows and live diagnostics against their pinned blobs and caller contracts. Audit evidence dependencies and archived-file integrity before any relocation |

Software verification requires deterministic regression and relevant normal entry-point tests. Native OpenSees, ETABS equivalence, laboratory validation and NBC acceptance each require their own evidence. This checkpoint does not close issue #75.

Editor: OpenAI Codex desktop. Exact model identifier: UNKNOWN.

## Executed tests

The exact unittest selection in the integrated audit workflow passed on Windows, conda-forge Python 3.12.11 and openpyxl 3.1.5: 203 tests run, 185 passed and 18 skipped. Full unittest discovery could not be used as a passing gate. Direct discovery exited with a Windows process error, and discovery with the repository as top-level rejected the tests directory as nonimportable. The named suite was used to verify the changed entry points.

Native probes, the complete building gravity and modal comparisons, and the full-record suite remain unverified in this checkpoint. The solver mechanics and archived engineering data were not reorganized.
