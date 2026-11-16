# Consolidated findings and coordinated fixes

**Status legend:** FIXED_IN_SOURCE; CI_UNIT_TESTED; STATIC_PATTERN_REVIEW; OPEN_NATIVE_VERIFICATION; NOT_YET_REVIEWED. Never use 'verified' without naming the exact gate.

| ID | Severity | Source / contract | Finding | Disposition |
| --- | --- | --- | --- | --- |
| GUI-001 | P1 | `components/ui/application.py App._run` and legacy facade | Legacy `exec(compile(...))` changed global `__file__` to the launcher's file. A worker path resolved to `C:\\Users\\User\\tools`, not repository tools | FIXED_IN_SOURCE; path now uses actual compiled function source; test passed CI previously; native Windows retest required |
| GUI-002 | P1 | `App._run`, ETABS COM | ETABS conversion ran in Tk main callback, appearing frozen during expensive API/HTML/assembly work | FIXED_IN_SOURCE; detached process + GUI polling, cancellation, stage log. Native ETABS COM lifecycle still unverified |
| EXPORT-003 | P0 | `tools/etabs_conversion_worker.py` | The worker accepted any existing `OpenSees_Complete_Export_Report_V118.json` after `convert_model` returned; it did not reject `assembly_errors`. This could mislabel a stale or incomplete model as an export completed | FIXED_IN_SOURCE in `b07462b1`; fresh-report signature and empty error list required; six fail-closed tests added. This is an output-status bug, **not evidence of faulty structural force values** |
| PERF-004 | P1 | `components/ui/application.py` visualizer | Repeated O(N) scans of element-tag crosswalk and thousands of Plotly traces inflate export cost | Lookup index added and HTML/assembly timing; exact native speedup UNMEASURED |
| PERF-005 | P1 | `components/model/assembly.py` mesh and frame splitter | Repeated all-node plane/intersection search for MESH_04/08/16 scales poorly | Spatial candidate indexes implemented; synthetic geometry/conservation tests pass; native 25-storey performance and equivalence still unmeasured |
| PERF-006 | P1 | `components/gravity/load_path_formulas.py` | Openpyxl full-column traversal even when setting header-only widths in large workbooks | FIXED_IN_SOURCE; row generation, serialization, progress stage separated; MESH_16 native high-memory benchmark remains open |
| GOVERNANCE-007 | P1 | `REVIEW_MAIN`, issue #75 | Historical review completion claims exceeded actual semantic/native checks | Issue #75 remains OPEN; AST queue explicitly NOT_REVIEWED; CI static PASS not engineering PASS |
| PUBLICATION-008 | P1 | Public generated model-derived HTML/JSON/CSV | Published detailed model topology/geometry in public MESH_04 review | Removed four artifacts from current public HEAD; historical commits/mirrors remain issue #88; not an engineering bug |
| SCIENCE-009 | P0 | 32 true supports / 44 wall-mesh nodes / 97 sensitivity | Sum of global gravity reactions matched, but frame-only/shell-only support groups redistributed approximately 18,648.51 kN between ETABS and 32-support OpenSees, from earlier saved comparison | OPEN_NATIVE_VERIFICATION; no forcing numerical matching or inventing restraints |
| SCIENCE-010 | P0 | First-step X-wall nonlinear transient | Non-finite/unstable element response previously recorded in wall element 110280; source constitutive, wall mesh and restraints must be verified before full NLTHA | OPEN_NATIVE_VERIFICATION |
| SCIENCE-011 | P1 | Studio B01–B12 | User-submitted 11 native OpenSees component PASS + 1 analytical-only FVD PASS / 58 metrics; separate from full thesis model | COMPONENT_BENCHMARK_EVIDENCE only; native ETABS match, wall/beam/shell interface and project nonlinear dynamics not accepted |

## Dependency and file-ownership risks (discovery, not confirmed bugs)

- Legacy root Python facades execute source via `exec(compile(...))` and import runtime helpers through dynamic filenames. Review **both actual module filename and facade `__file__`** whenever changing paths.
- `OpenSees_Timing_V130` wraps conversion and may recursively inspect a large output tree to create per-artifact metadata after the named stage; likely performance cost, **not measured**.
- Dynamic imports, ETABS COM API returns, shell-to-frame constraints, OpenSees native DOFs, Excel formulas and ZIP snapshots need source-to-consumer validation. Static imports do not resolve all runtime dependencies.
- 403 identical Git blob groups imply duplicate historical bytes, **not disposable files**. Do not delete until authored source, provenance, downstream readers, and archive retention rules are documented.
- Synthetic CI tests cannot establish that native OpenSeesPy, CSI ETABS v23, driver architecture, material files and third-party Windows dependencies behave identically.
- `UNCLASSIFIED_MANUAL_TRIAGE` files and external/dependency candidates remain queued in generated source audit artifacts.

## Correct workflow

Discovery → dependency/output contract review → targeted source inspection and reproducible failing test → minimal coordinated correction → headless CI → native Windows ETABS/OpenSees comparison → engineering acceptance record → close only the corresponding gate.

Do not merge a numerical model change merely to make support reactions or modal periods match without an independent physical equivalence argument.
