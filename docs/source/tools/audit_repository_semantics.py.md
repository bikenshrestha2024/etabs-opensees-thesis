# Repository semantic discovery: static scope and provenance

**Implementation:** `tools/audit_repository_semantics.py`.

The analyzer reads `git ls-files --stage -z` (Git's tracked index), not arbitrary untracked Windows ETABS exports. It records Git blob IDs, tracked-path counts and roles. Active root Python launchers, `components/`, `src/` and `tools/` get AST parsing/compilation, nested and literal dynamic import inspection. The `tests/` tree is parsed separately. Versioned `Saved_Project_*/`, `Worked_Example_*/`, `Verification_*/`, `archive/`, preserved research/calibration examples, archived logs and large generated reports are listed with provenance but **not executed or moved**.

## Reproducibility

```powershell
python tools/audit_repository_semantics.py --output audit/repository_semantics.json
python -m unittest tests.test_repository_semantics_audit -v
```

The CI workflow runs the tool and retains its JSON report as an Actions artifact. The summary prints active files, missing local import references, syntax/compile errors, and advisory review-candidate counts. `--fail-on-active-errors` is available only once confirmed missing imports have been classified; it will fail on active syntax/compile errors or static local module misses. Advisory risk patterns (swallowed exceptions, eval/exec, shell subprocesses) never automatically constitute confirmed vulnerabilities.

## Scope caveats

- An AST module name may be a dynamically injected package or optional plugin, and `from package import name` may reference a variable; an unresolved candidate **requires source inspection** before remediation.
- GUI callbacks and strings building filenames can evade static import resolution; use explicit integration tests for each canonical launcher and stage.
- No physical FEM equivalence, NBC 105:2025 compliance, damping or nonlinear convergence, 32/76/97 native joint reactions or solver responses are certified.
- Do not commit model EDB/XLSX, source full-table exports, unredacted runtime logs, site project paths or sensitive data. The output contains tracked relative paths and code diagnostics only.
- No changes to canonical source ownership, engineering source/load factors, source hash tracking, supports, mesh or output path consumers are performed by this analyzer.

## Acceptance

G0: every Git-tracked path assigned a role and count reconciled to `git ls-files`.
G1: active Python parses/compiles and known local imports are resolved or listed for investigation.
G2: standard Windows GUI/input/output tests are independently green.
G3: documented original ETABS and OpenSees wall-base forces and restraints match tolerances, not merely global weight.
G4: original NBC-based ESM/MRSM/LTHA/NLTHA source fingerprints and final solver response status are verified.
G5: public disclosure scan and output folder provenance/reader compatibility gates pass.
G6: review and CI pass before merging, while unresolved engineering gates stay explicitly open.

**This is systematic discovery and a machine-readable triage index, not a substitute for detailed line-by-line human review of all active engineering functions.**
