# 2026-11-12 current-source implementation verification register

**Source baseline:** `79ceef130c37b756e2a7dd8ef9623c6efa59bfaa` (`main` at initial audit; later commits may change SHA). **Review method:** inspected Git tree and selected active source, source guides, CI workflow definitions and previous completed GitHub action records. This is **not** a whole-repository line-by-line semantic review or native model certification.

## Implementation and evidence matrix

| Workstream / earlier recommendation | Current source finding | Evidence / entry point | Still required |
|---|---|---|---|
| 01–07 numbered thesis workflow navigation | PRESENT | `01_ETABS/` through `07_REVIEW_MAIN/` | Check internal consistency on later reorganizations |
| Historical review content preservation | PRESENT | `REVIEW_MAIN/`, `07_REVIEW_MAIN/README.md` gateway | Full legacy caller/path migration before any physical rename |
| Primary workflows with who/what/when/why/how/where/which | 15 indexed cards PRESENT | `KNOWLEDGE_BASE/01_WORKFLOWS/WORKFLOW_CARDS.csv` | Expand from principal workflows into exception paths, individual tests and source parameters |
| Source guide paths for active `components/` modules | 158/158 paths present at baseline | `docs/source/components/` | Semantic quality, examples, source units and citations require per-file review |
| Individual guides for active `tests/` files | 6/153 paths present at baseline | `docs/source/tests/` | Incremental guides and test-purpose traceability; do not claim full coverage |
| Readiness GUI asynchronous evidence scans | PRESENT | `components/model/readiness_dashboard_gui.py` | Native Windows/Tk responsiveness stress test, file-changing-during-scan race review |
| Readiness project auto-discovery | PRESENT | `components/model/readiness_dashboard.py` | Verify real project deployment and SHA binding |
| Readiness checklist incomplete-signoff protection | **DEFECT FIXED IN REVIEW BRANCH** | `audit()` required-key logic; `tests/verify_readiness_dashboard.py` | CI; native model review remains separate |
| Readiness cross-project selection protection | **DEFECT FIXED IN REVIEW BRANCH** | same | CI plus Windows GUI test |
| Project nonlinear material evidence vs literature cards | PRESENT | `components/model/nonlinear_preflight.py` | Actual reinforcement, FSAM regions, specimen and cyclic validation |
| NBC 105:2025 full-gravity vs seismic weight factors | PRESENT, input-completeness defect fixed in review branch | `components/model/load_case_purpose.py` | Review actual ETABS pattern assignments and matched-load reactions |
| Distinct storage and roof live ledger fields | PRESENT | `components/gravity/storey_loads.py` | Verify unknown pattern classifications against original ETABS occupancy |
| Original Aw/T1 workbook and EDB provenance | Implemented modules and review instructions exist | ESM source; `REVIEW_MAIN/02_ESM/` | Inspect actual source-cell hashes and adopted model periods |
| LTH XY/YX Kobe full pair | NUMERICALLY COMPLETED in uploaded case | `REVIEW_MAIN/05_LINEAR_TH/20261112_KOBE_FULL_PAIR_TIMING_DRIFT_AND_PERIOD_AUDIT.md` | ETABS-equivalent physical source and eight record-pair suite |
| LTH acceleration optimizer (`factorOnce`) | OPT-IN EXPERIMENT PRESENT | `components/linear_time_history/runner_and_gui.py` | Verify constant tangent, native short-run equivalence and measured speedup |
| LTH vector support-reaction recorder | OPT-IN EXPERIMENT PRESENT | `components/shared/response_recorders.py` | Native 6-DOF reaction equivalence and benchmark |
| History viewer linear vs exploratory-NL scope | PRESENT; explicit mixed selection bug fixed in review branch | `components/ui/history_inspection.py` | Windows UI, large folder responsiveness and provenance checks |
| Readiness file hashing | Per-audit reuse present | `components/model/readiness_dashboard.py` | Source-fingerprint snapshot coherency under concurrent file modification |
| Repository source-code and data security | Governance rules and prior review exist | `engineering/rules/`, `REVIEW_MAIN/08_SOFTWARE_SECURITY/` | Repeat secret scan and ZIP redaction tests after every major revision |
| FVD/BRB literature and reference library | Indexed and linked | `LITERATURE/`, `Material_Catalog/` | Actual manufacturer/specimen parameter validation and device response |
| First-step X core-wall nonlinear failure | **BLOCKED** | `REVIEW_MAIN/06_NONLINEAR_TH/` and wall diagnostic code | ZERO/X/Y/XY finite element evidence, geometry/rebar, solver and P-Delta |
| Gravity physical equivalence with ETABS | **NOT VERIFIED** | `REVIEW_MAIN/01_GRAVITY/` | Identical D/LL/roof, seismic preload, supports, unit and mass scenarios |
| 25-storey M0–M6 224-run plan | PLANNED | `docs/review/20261112_THESIS_DELIVERY_WORKBOARD.md` | Accepted full-duration native XY/YX histories and sensitivity comparisons |
| Source citation inventory | AUTOMATED | `LITERATURE/CODE_CITATION_OCCURRENCES.csv` | Unmatched DOI metadata, author-year citations, legal PDF access |
| Native Windows/OpenSees execution of this review branch | **NOT EXECUTED** | No native evidence supplied with this review | Local ETABS/OpenSees parity and GUI benchmark before thesis production |

## Defects confirmed and fixes proposed in this branch

1. **Readiness false approval:** overall recorded sign-off was computed over whatever keys appeared in a draft; missing required workstreams were not mandatory. Now require the entire canonical set of `REVIEW_KEYS`, plus matching current-project model path and source SHA. Regression tests are synthetic and fail closed.
2. **Empty load-audit false success:** explicit empty source-pattern data could yield no entries and `MATCHES_DECLARED_PURPOSE_FOR_CLASSIFIED_PATTERNS`. Now emit `REVIEW_REQUIRED` with `NO_LOAD_PATTERNS_TO_AUDIT` or `EMPTY_SOURCE_PATTERN_SET`, including Boolean coefficient rejection. Does not rewrite factors.
3. **Explicit history-viewer scope reset:** on refresh, an explicit `All analyses (mixed)` choice reverted to LTH because the label is not a folder name. Now preserve that choice and test it.

## Evidence policy for next steps

Each process report must record: **WHEN** (run UTC/local, tool/code SHA), **WHY** (engineering intent), **HOW** (algorithm and inputs), **WHERE** (output and source locations), **WHICH** (NBC clause/DOI, factors, units and record hashes), **WHO** (source operator and named reviewer only if actually assigned), and **WHAT** (success, warning, failure and limitations). Save original evidence, mark exact accepted steps and full duration. Never substitute documented software behavior for engineering acceptance.

**Review outcomes:** regression tests and CI are software checks. No unobserved native 25-storey run, ETABS comparison or professional sign-off is claimed. Workboard links: [P0–P2](20261112_THESIS_DELIVERY_WORKBOARD.md), [numbered review gateway](../../07_REVIEW_MAIN/README.md).
