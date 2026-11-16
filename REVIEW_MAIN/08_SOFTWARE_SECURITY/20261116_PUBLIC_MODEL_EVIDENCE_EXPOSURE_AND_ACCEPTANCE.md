# Public model-evidence disclosure and engineering acceptance review — 2026-11-16

**Repository:** public `bikenshrestha2024/etabs-opensees-thesis`. **Classification:** SECURITY / DATA GOVERNANCE, NOT A NUMERICAL SOLVER DEFECT.

## Confirmed public artifacts and remediation

The model-specific MESH_04 review directory contained four generated artifacts that exposed structural coordinates, shell/frame incidence maps, internal node and frame tags, and section properties. They are engineering source/derived topology evidence, not generic technical documentation. Their publication was not necessary to explain the numerical verification method.

| Public path (under `REVIEW_MAIN/00_MODEL/20261116_MESH04_AND_ETABS23_VERIFICATION/`) | Last observed Git blob SHA | Public-branch action |
| --- | --- | --- |
| `Frame_Mesh_Interface_Audit.json` | `3a4d5aba1a95fe49cbfb8be10be6e1a9beaf3974` | deleted from HEAD |
| `MESH_04_Floor_Mesh_3D.html` | `14b43a0c791d52629dd777a7c7b693f0ee020344` | deleted from HEAD |
| `MESH_04_Floor_and_Beam_3D.html` | `e1ad614072722fdf33ae0821b0b9d5f4e47dfc62` | deleted from HEAD |
| `MESH_04_Node_Roles.csv` | `259d2d0d856a2a7ae84699db00dc02cbd52e6e30` | deleted from HEAD |

The folder README was replaced with a redacted engineering summary. Explicit ignore entries were added to `.gitignore` for the four derived paths. The official ETABS benchmark review narrative remains public.

**Residual disclosure:** This removal is **not a Git history purge**. The earlier contents may still be accessible through previous commits, cached mirrors, forks, archived CI artifacts, or locally cloned repositories. Search/identify other historical artifacts before declaring the repository private-data clean. If the owner wants a comprehensive permanent publication takedown, evaluate migration to a private repository and coordinated history/remote/CI artifact remediation; such operations can disrupt existing collaborators and Git references. Do not rewrite history automatically.

**Remaining scope unknown:** This targeted review examined the new MESH_04 directory and existing governance docs, not every historical source-derived dataset in the public repository. Further publication scanning is needed before making a repository-wide clearance statement. Do not publish source EDB/XLSX files, complete exported model JSON, local model paths, structural topology coordinate tables, sensitive model-derived HTML, or private evidence packages.

## Findings tracked separately

**SECURITY-G1 (mitigated at current HEAD, residual historical exposure):** model-derived detailed connectivity artifacts were committed publicly. Prevent repeats with private case-local review location and public redacted metadata only.

**GOVERNANCE-G2 (reopened):** GitHub [issue #75](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/75) was marked completed although its own checklist and latest Codex ledger still describe incomplete active-source semantic reviews and native numerical verification. Reopened to prevent implying acceptance from CI. Closed PRs and successful static tests are retained as earned accomplishments, but do not automatically close P0 numerical and scientific gates.

**ENGINEERING-E1 (still open, not a security finding):** 32 physical supports + 44 extra wall mesh nodes + 97-point continuous wall-base sensitivity must be compared with actual ETABS analysis-mesh constraints and full six-component foundation actions. Matching total gravity force is insufficient; the unresolved frame/wall force redistribution requires native ETABS and OpenSees subassembly/result comparisons.

**ENGINEERING-E2 (still open):** first-step X-wall NLTHA failure and incomplete full-record transient verification remain independent physical/numerical blockers.

**SOFTWARE-S1 (separate from above):** static code tests, organized output manifests and revised load-path formulas have specific regression evidence in `docs/review/ledger/20261116_b8db900/`, but total tracked inventory or scanned AST units do not establish semantic review completion.

## Required acceptance gates

1. `PUBLIC_DATA_REVIEWED`: inspect current tracked text/binary, history, releases and workflow artifacts for source-derived coordinates, machine paths, passwords/tokens, model topology. Publish only an anonymized summary, preserve details in private local case folders.
2. `SEMANTIC_SOURCE_REVIEWED`: line-level actual code inspection with source blob, caller contracts, tests and reviewer; AST enumerations alone do not count.
3. `STATIC_REGRESSION_PASS`: tests and workflow checks for a **specific pinned commit**, with skipped tests distinguished from passes.
4. `NATIVE_OPENSEES_PASS`: exact model identity, solver version, load/constraint set, complete result vectors and convergence.
5. `ETABS_EQUIVALENCE_VERIFIED`: source EDB identity, mesh/edge constraint equivalence, matched support reactions, beam/wall force and displacement, declared tolerances.
6. `NLTHA_ACCEPTED`: fresh domain, completed motions/orientations, complete accepted responses and independent engineering acceptance.

Issue #75 must remain open until its own acceptance checklist is independently satisfied or scope is explicitly revised by engineering decision, not merely when a review document is added.

## Publication rules

- Keep ETABS-generated model exports, 3D viewers, nodal/mass/reaction CSVs and specific model topology JSON in private case-local `REVIEW_MAIN` or `06_REVIEW` output, **not** public GitHub.
- Retain precise file fingerprints privately. In public documentation prefer generic component/ID descriptions and non-identifying engineering conclusions. Source IDs alone can be acceptable when stripped of geometry and force values.
- `.gitignore` prevents ordinary new tracking of named files but is **not a security boundary**; explicit `git add -f`, renaming or other paths can bypass it. Add a targeted path/content scanner and reject known generated model evidence in PR reviews.

**Disposition:** targeted public-branch mitigation performed. Historical data disposition and repository-wide publication scan are outstanding; numerical equivalence remains blocked.
