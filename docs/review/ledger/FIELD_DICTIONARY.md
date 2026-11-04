# Ledger field dictionary and validation boundaries

| Field | Meaning |
|---|---|
| `baseline_commit` | Exact immutable Git commit used for file inventory |
| `file_path` | Relative active source entry from the Git tree; root versioned launchers remain included |
| `git_blob_sha` | Git object ID for source blob at baseline (**not** raw-file SHA256) |
| `size_bytes` | Tracked blob byte size |
| `inventory_kind` | Component, test, tool, root entry, or compatibility/versioned launcher |
| `inspection_scope` | Directly inspected source versus filename/hash inventory only |
| `inspected_lines_or_functions` | Exact reviewed spans/symbol names; `NOT_INSPECTED` is honest default |
| `review_status` | `NOT_REVIEWED`, `PARTIAL_SEMANTIC_REVIEW`, `REVIEWED_SOURCE_FULL` |
| `finding_or_risk` | Source-grounded finding for inspected files; `NOT_EVALUATED` for others |
| `verification_evidence` | Test command/result if independently executed, or historical label |
| `native_model_status` | `NOT_RUN` unless actual model evidence exists |
| `remaining_action` | Specific next review requirement |

The ledger **does not** automatically inspect the physics or guarantee that file imports resolve, materials are calibrated, or results converge. Preserve exact patches, cases, source provenance, units and native outputs as separate evidence.

See [starting architecture and P0 issues](../00_ACTIVE_CODE_ENGINEERING_REVIEW.md), [existing source audit](../../../tools/audit_active_repository.py) and [Codex RTFC prompt](../../../.github/prompts/soil-c-nltha-rtfc.prompt.md).
