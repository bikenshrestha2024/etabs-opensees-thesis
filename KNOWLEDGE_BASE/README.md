# Thesis knowledge base — what / when / why / how / where / which / who

**Purpose:** operational, code-linked explanations for the active ETABS→OpenSeesPy thesis. This is a **navigational overlay**, not a duplicated implementation or a hidden replacement for existing engineering documentation.

## Start here

- [Workflow cards (CSV)](01_WORKFLOWS/WORKFLOW_CARDS.csv) — fifteen code-linked modules with all requested questions, owner roles, prerequisites and acceptance gates.
- [Folder architecture](02_REPOSITORY_STRUCTURE/README.md) — where files belong, canonical location, how to add new files safely and what must not move.
- [UI speed and accuracy](03_UI_PERFORMANCE/README.md) — background evidence hashing, stale results, feedback and native solver speed gates.
- [Physical engineering checks](04_ENGINEERING_GATES/README.md) — separation of numerical, source, material and code status.
- [Knowledge ownership and update policy](05_PROVENANCE_OWNERSHIP/README.md) — source, reviewer responsibilities and explicit gaps.
- [Knowledge map audit](../tools/audit_knowledge_map.py) — offline machine-readable paths and completeness checks, without importing OpenSees or disclosing private inputs.

## What is answerable now and what is not

All 15 core workflows have a documented **when, why, how, where, which input, and who (accountable role)**. A specific engineer's identity or signature, a missing project's actual reinforcement, and an unvalidated native run cannot be deduced from code. Mark them **NOT_VERIFIED**; do not invent answers. There are 2,797+ tracked repository files, and this curated set is not falsely described as a semantic review of every file.

## Usage

1. Choose the task in the [workflow CSV](01_WORKFLOWS/WORKFLOW_CARDS.csv).
2. Open the exact canonical source and guide in the row.
3. Before changing a model, follow the evidence/acceptance gate and source hash.
4. Run the prescribed launcher from [the existing canonical launcher index](../docs/programs/00_PROGRAM_INDEX.md); do not choose by root filename sorting.
5. Record failed steps and differences in [REVIEW_MAIN](../REVIEW_MAIN/07_TIME_HISTORY/20261112_KOBE_LINEAR_PARTIAL_BATCH_AND_PERFORMANCE_REVIEW.md), preserving previous evidence.
6. For maintenance, run `python tools/audit_knowledge_map.py` on a clone. Missing paths are errors; a valid file path is not proof of engineering correctness.

**Model/analysis guardrails:** user ETABS EDB, Excel, matched waves and PDF binaries stay read-only/private; existing root launchers and saved output paths are not renamed; the unresolved X-only first-step core-wall failure remains a P0 blocker.
