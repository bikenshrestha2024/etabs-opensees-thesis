# audit_repository_integrated.py — canonical tracked-file and function-level review

**Source:** [tools/audit_repository_integrated.py](../../../tools/audit_repository_integrated.py)

**Purpose:** One authoritative non-destructive repository-wide static audit. It collects exact Git-index blob identities, root Python launchers and active packages, imports (eager/deferred/literal dynamic), cycles, source risks, output-writer occurrence candidates, facades and archive duplicate identities. Archived files are metadata/provenance only.

**Command:**

    python tools/audit_repository_integrated.py --repo . --output audit/integrated --fail-on-static-blockers

**Existing outputs:** audit/integrated/00_OVERVIEW through 09_FACADE_COMPATIBILITY. The source file/function register in 08_SEMANTIC_REVIEW/function_review_register.csv is a review queue, NOT automatic engineering acceptance.

## 2026-11-17 source-review attestation extension

A tracked CSV at docs/review/ledger/semantic_review_attestations.csv may recognize a **specific, already inspected code symbol**, but only with:
- exact tracked source path + qualified Python symbol and 40-character Git blob SHA,
- named reviewer and explicit status SOURCE_INSPECTED_TESTED_NOT_NATIVE_VERIFIED,
- tracked source-review evidence under REVIEW_MAIN/ or docs/review/ledger/,
- tracked regression test(s) under tests/, multiple tests separated by |.

New helper apply_source_review_attestations(root, semantic_units, indexed) refuses stale source blobs, duplicates, unknown symbols, untracked/redirected/unsafe review evidence or missing reviewer/status. It never opens private source files or changes any model. Its output is an explicit annotation distinct from semantic_review_completed_count, which remains zero until separately evidenced *independent* full review. Additional report audit/integrated/08_SEMANTIC_REVIEW/attestation_validation.json contains count and errors.

The static audit becomes BLOCKED when attestation integrity fails; changes to a reviewed function's source must **invalidate** its old attestation. It cannot silently keep a previous green review merely because filename/symbol still match.

**Status distinctions:** SOURCE_INSPECTED_TESTED_NOT_NATIVE_VERIFIED means scoped AI-assisted code inspection supported by tests; it does NOT certify every line, business behavior, physical equivalence, NBC 105:2025, numerical stability, ETABS/OpenSees 32/76/97 support reactions or complete NLTHA.

**Tests:** tests/test_repository_integrated_audit.py validates correct SHA, stale SHA, unsafe path, duplicate and unknown symbols. Full CI validates actual tracked source/evidence paths and emits the integrated report.

**Security/limits:** Relative tracked paths only, no source EDB/XLSX, private output or user-specific absolute paths committed. Source code content is not uploaded outside the existing public repository. Git history security assessment and native Windows ETABS/Spyder are distinct gates.
