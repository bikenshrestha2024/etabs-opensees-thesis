# Repository-wide semantic audit — 2026-11-16 checkpoint

**IMPORTANT:** This folder is a **versioned checkpoint of verified work and unresolved gates**, not a claim that 3,000+ files were each semantically reviewed. The code can discover all tracked symbols; it cannot establish engineering correctness by parsing them.

## Baseline and method

- Immutable successful discovery baseline `19342cb0bf7d70f1c543f819e9fafb2d6fc40699`: **3,129 tracked files**, **770 Python source files**, **4,561 AST-discovered class/function symbols**, **0 AST parse errors**, **403 duplicate Git blob groups (484 extra identical files)**, **538 pattern-review candidates**. These are machine counts at that pinned SHA. Later changes require a new pinned run.
- Git tree and actual tracked blobs were enumerated using `git ls-files -s -z`; the discovery runner never imports thesis engineering modules or opens EDB files.
- After the dependency extension, `RESOLVED_IMPORT_CLASSIFICATION.csv` classifies explicit static import edges; `OUTPUT_READER_WRITER_REVIEW_QUEUE.csv` identifies potential read/write call sites. Both are **heuristic review queues**; dynamic imports, imports from external packages and file schema equivalence need manual and native testing.
- All 4,561 discovered classes/functions were marked **DISCOVERED_NOT_SEMANTICALLY_REVIEWED**, not reviewed. Reviewers must record source SHA, actual lines read, caller contract, input/output units, tests, physical assumptions and acceptance status before promotion.
- Duplicated archived blobs are preserved: historical snapshots, calibration records, published examples, regression fixtures, source provenance and references must not be removed before dependency and hash-based review.

## Directory contract

```text
REVIEW_MAIN/
  09_REPOSITORY_AUDIT/
    20261116/
      README.md                       # This checkpoint
      FINDINGS_AND_FIXES.md           # Confirmed issues, tested corrections, open items
      MANUAL_REVIEW_LEDGER.md         # Precisely scoped source-level review evidence
      ENGINEERING_ACCEPTANCE.md       # Unclosed ETABS/OpenSees scientific gates
tools/
  repository_semantic_discovery.py    # Complete tracked-tree AST and import/IO discovery
tests/
  test_repository_semantic_discovery.py
.github/workflows/
  repository-semantic-discovery.yml   # Public-source audit artifact (NOT model results)
AUDIT_RUNS/                            # Local/CI generated review files, Git-ignored
  semantic_discovery/
    TRACKED_INVENTORY.csv
    SYMBOL_DISCOVERY_NOT_REVIEWED.csv
    IMPORT_EDGES.csv
    RESOLVED_IMPORT_CLASSIFICATION.csv
    OUTPUT_READER_WRITER_REVIEW_QUEUE.csv
    SUSPICIOUS_PATTERN_QUEUE.csv
    DISCOVERY_SUMMARY.json
    READ_ME_FIRST.md
```

To reproduce on a **full local clone**:

```powershell
git pull origin main
conda activate etabs_env312
python tools/repository_semantic_discovery.py --root . --out AUDIT_RUNS/semantic_discovery
python -m unittest discover -s tests -p "test_repository_semantic_discovery.py" -v
```

This produces a reproducible source inventory on the *current* checkout; it does not alter original EDB/XLSX, mesh, solver response, load factors or case outputs.

## Related lifecycle

- [Confirmed fixes and review blockers](FINDINGS_AND_FIXES.md)
- [Source inspection ledger](MANUAL_REVIEW_LEDGER.md)
- [Engineering acceptance gates](ENGINEERING_ACCEPTANCE.md)
- [Cross-repository issue #75](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/75)
- [Security/history issue #88](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/88)

Do not publish private source/solver data through audit reports. CI artifacts contain public tracked **source-code paths** and AST/import metadata only. Reproducible models and numerical evidence must stay under the selected **private case root**.
