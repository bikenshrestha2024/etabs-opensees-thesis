# Canonical cross-agent research engineering contract
Status: governance policy; not structural verification. Existing `AGENTS.md`, established decisions, source guides, and existing agent skills remain in force and must be merged rather than overwritten.

## Before ANY edit
1. Read `engineering/migration/README.md`, `docs/programs/00_PROGRAM_INDEX.md`, and the relevant active module guide; search existing functions, aliases, tests, issues, and PRs before creating a file.
2. Classify candidate as EXISTING / EXTEND / REPLACE_WITH_MIGRATION / NEW_WITH_JUSTIFICATION. Maintain `engineering/registry/CANONICAL_MODULES.csv`; do not create `*_latest.py`, `*_fixed.py`, or version-numbered active source duplicates.
3. Record git base SHA, exact changed paths, user-preserved files and test plan; make an isolated branch/PR for nontrivial changes.
4. Verify actual numerical source and source EDB/workbook identity; do not invent material/earthquake/reference numbers.
5. Never silently change load/mass, pier/opening treatment, frame overlap, units, stiffness or accepted research decisions. Distinguish solver success, ETABS equivalence, component validation, and code acceptance.
6. Test the smallest affected unit, then integration and engineering gates where available; report native Windows/ETABS and full-model tests as PENDING unless actually run.
7. Save reproducible manifests, optional evidence and missing-file lists. Do not upload confidential models, personal paths, credentials or unlicensed full texts.
8. Record actual editor/tool in `engineering/agent_edits/` when changes are made; unknown providers are UNKNOWN, never inferred from Git commit author.
9. Do not merge major reorganization without compatibility, regression, security and human engineering review.

Read `ENGINEERING_GATES.md`, `MODULE_BOUNDARIES.md`, `PROVENANCE.md`, and `AI_ATTRIBUTION.md` only when those topics are touched. Platform rules and verified source evidence always take precedence over repository suggestions.
