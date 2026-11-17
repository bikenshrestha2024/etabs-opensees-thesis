# Independent active Python source triage — 17 Nov 2026

**Status: static, AST-derived candidate register ONLY. NOT a complete semantic review, engineering verification, physical equivalence, native solver execution, or code compliance approval.** The canonical repository auditor remains `tools/audit_repository_integrated.py`; the exact-source manual evidence/attestation ledger remains `docs/review/ledger/semantic_review_attestations.csv`. This document adds independently cross-checked coverage information, **not** a competing automatic approval process.

## Immutable reference

- GitHub Actions workflow: [Integrated tracked-tree and dependency audit run #44093460202](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44093460202), active-public-python-source-review artifact `14331898883`; PR HEAD `a99910b74dad50ed467a8030d76a53f8d364f80d`. The ZIP was retrieved and actually extracted for AST traversal. The squashed merge on main is `7c177196c95c4d3521d12ed903f52f1b89795fd7`. Counts below belong to the specified **PR-head artifact** and must not be silently transferred to another source version.
- Repository Git tree at that merge: **3,181 tracked blobs**, `truncated=false`.
- Independently parsed **579 active Python source files**, **0 syntax parse errors**.

## Review-unit count (AST scope, not approvals)

| Code scope | Candidate units |
|---|---:|
| Module-level scope, including import-time behavior | 579 |
| Classes, including GUI/solver and callback-owning classes | 329 |
| Functions and methods, including nested/async functions | 3,516 |
| **Total independently enumerated AST review candidates** | **4,424** |

The previous integrated auditor's approximately **4,416** review units were a different commit snapshot. Different snapshots or inclusion details should not be interpreted as a numerical audit contradiction or a growth/reduction of reviewed functions. This independent count enumerates nested definitions, every class and a module-scope entry; no candidate was automatically promoted to reviewed.

## Automated prioritization queue

A separate private/local **metadata-only** CSV triage file was prepared from the same artifact: source path and raw source SHA-256, qualified symbol, AST start/end lines, representative static call targets and heuristic safety flags. It excludes source code, original private EDB, raw accelerograms, credentials and numerical model exports.

| Heuristic priority | Candidate units | Meaning |
|---|---:|---|
| P1 | 984 | Engineering-relevant module/symbol with candidate numeric coercion, native solver, source identity, file publication, subprocess, dynamic import or similar risk |
| P2 | 1,208 | Engineering-relevant name/path without those local flags |
| P3 | 2,232 | Other source scopes, GUI/helper/compatibility/archived-classified by active-source selection |

**These are static heuristics, not findings of 984 bugs.** Different function bodies and nested static traversal can overlap and flags may be false positives. A function may be correct even if it uses `float(...)` without a local `isfinite` when its caller guarantees validated finite inputs. Conversely, no flagged API pattern does not mean the function is correct. The local CSV queue is for planning manual reviews only and must not replace the canonical registered review method.

## What semantic completion actually requires

Each candidate must be inspected **in source** with exact Git blob and line span, argument and return contracts, error handling, all call-site data and GUI/ETABS/Excel/OpenSees dependencies, input units and model semantics, source-identity and output-filename ownership, cross-stage results and side effects. Reproduce source-backed bugs with a failing test; fix without changing native structural physics unless source and experimental evidence justify it. Update the canonical semantic attestation row to the **new exact source Git blob** after modifications; preserve user source files and old versions.

**Current canonical review coverage:** **12** narrowly reviewed/tested function attestations at latest main. They are marked `SOURCE_INSPECTED_TESTED_NOT_NATIVE_VERIFIED`, **not complete independent semantic or native engineer-approved attestations**. A function count without source/caller inspection is not closure of this gate.

## Engineering acceptance stays separate

- **ETABS↔OpenSees:** global 1.0D+1.0L ETABS FZ and OpenSees Rz totals agree to about 0.00028 kN, but OS76 assigns **104,463.013534 kN** to 44 wall-connected nodes where the ETABS point-object FZ ledger is zero. No fresh ETABS analytical-joint six-DOF, MPC, wall physical cut, rigid offsets and shell-to-frame transfer evidence has been reproduced. See [32/76/97 partition](../01_GRAVITY/20261117_INDEPENDENT_REACTION_PARTITION_32_76_97.md) and [SHA guard](../01_GRAVITY/20261117_WALL_SUPPORT_SOURCE_SHA_SENSITIVITY_REVIEW.md).
- **NLTHA first-step:** element 110280/112778 are localization evidence, not proven root cause. The source-specific stage provenance guard is verified, but the full native ZERO/X/Y/XY and converged wall/FSAM panel trials are absent. See [wall stage audit](../06_NONLINEAR_TH/20261117_FIRST_STEP_STAGE_SOURCE_IDENTITY_AUDIT.md).
- **M0–M6:** 7 variants × 8 paired ground motions × 2 limit states × 2 orientations = **224 intended native executions**. Configuration generation and synthetic output verification do not create those histories; no complete physically accepted 224-run evidence set is available.

**Acceptance:** Tracked inventory PASS, static Python source parsing PASS, targeted CI PASS at the appropriate SHA; **ENTIRE ACTIVE SEMANTIC REVIEW OPEN**, **ETABS PARITY NOT VERIFIED**, **X-WALL CONVERGENCE UNRESOLVED**, **224 FULL NATIVE NLTHA NOT VERIFIED**. Engineering release requires the original private ETABS v23 EDB, latest native analysis exports and matched record source files, compatible solver environment, and independent quantitative tolerance/experimental/code checks. No automatic status promotion.

This report intentionally contains only aggregated metadata to preserve the user's local model and report confidentiality.
