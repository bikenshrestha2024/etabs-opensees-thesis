# Provenance, responsibilities and knowledge gaps

## WHO — roles, not invented people

| Role | Responsibility | Required evidence |
|---|---|---|
| Researcher/model operator | Select exact project, collect 25-storey source data, record motions/variants | EDB/motion SHA, configuration, saved run logs |
| Structural/earthquake reviewer | Validate geometry, confinement, structural loads, wall behavior, code interpretation | Dated signed review, referenced calculations |
| Numerical methods reviewer | Verify elemental behavior, solver stability, sensitivity and convergence | ZERO/X/Y/XY diagnostics, accepted finite history, residuals |
| Software maintainer | Code review, CI, GUI and packaging, security | Git diff/commit, tests, import checks, rollback |
| Reference curator | Paper metadata, DOI, source/section and PDF usage rights | Literature IDs, citation source/date and license |

A missing person or approval is `NOT_ASSIGNED` or `NOT_VERIFIED`, never an implied signature.

## Five-W-one-H evidence record

- **What:** named program, material/element, case, result and acceptance status.
- **When:** observation/run timestamp, code commit, input modification date, source publication date.
- **Why:** purpose, physical assumption and discrepancy motivating change.
- **How:** native commands, solver setup, exact inputs, checks, test results and limitations.
- **Where:** canonical repo file + local private input/output path (redacted in public logs).
- **Which:** parameter/DOI, NBC clause, software version, options and sensitivity case.
- **Who:** actor/editor + qualified reviewer identity when supplied, never guessed.

## Limitations and update discipline

The fifteen curated workflow cards do not cover every symbol in thousands of tracked files. The path-audit tool checks discoverability, not structural accuracy or completeness of publication metadata. New evidence must be linked to its source, project model hash and owner role. Keep all sensitive models, matched records, original PDF copies and API secrets outside public GitHub.

Canonical rules: [AGENTS.md](../../AGENTS.md), [provenance](../../engineering/rules/PROVENANCE.md), [AI attribution](../../engineering/rules/AI_ATTRIBUTION.md), [review ledger](../../docs/review/ledger/README.md).
