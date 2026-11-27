# Third-lot actual workbook review — 2026-11-27

Editor: OpenAI ChatGPT (GPT-6.2). Base cc024bd341b3ad3311b0d07e7e718b5c31194a05. Read-first project contract and existing offline reaction reader, support filter, source guide and tests reviewed. No change to model, solver, supports, gravity factors, seismic weight or adopted NBC rules. Previous picker fix PR #227 passed all eight CI workflows and merged. Its exact patched selector accepted the actual third-lot input and rejected the two earlier partial inputs when selected as reaction sources.

Actual source was streamed using openpyxl read_only=True; all worksheet and populated-cell counts, original byte hash, CSV row counts and engineering checks verified locally. Raw workbooks, hashes, nodal vectors, local paths and extracted model datasets remain private. Source-side tests checked exact case/step/joint keys, joint ID coverage against topology, 32 nonzero/44 zero reaction split, static force magnitudes against first-lot section cuts, gravity superposition, duplicate-table response equivalence, distinct relative/absolute response, total displacement reconciliation and adjacent-floor drift at simultaneous non-envelope steps. No synthetic test was substituted for workbook inspection. Two interrupted CSV writes were re-extracted from the unchanged source and checked for completeness; full typed-cell scan was completed independently.

The matching evidence is not a native EDB binding, native six-DOF restraint validation or an OpenSees comparison. The third lot fills the missing Joint Reactions evidence but not native assignment tables, Base Reactions, source EDB SHA, restraint/edge-constraint definitions, full dynamic records or the current matching OpenSees solution. Use existing source-identity and approval gates, preserve the 32 primary/44 mesh split and separate 1D+1L gravity from NBC Table 5-1 seismic weight. No full multi-lot production merge or unverified solver change was made. Documentation-only follow-up; local audit regression completed, no new native solver execution. Existing all-76 report label remains a follow-up reporting issue, not a changed acceptance rule.


## Cumulative FIRST + SECOND + THIRD LOT follow-up

Editor: OpenAI ChatGPT (GPT-6.2); base 8c73e7530313a21adcccae4417c7c2ada5526cae. Preserve PRs #231 and #232 and their prior workbook evidence. Existing read-first contract and current source owner/guide/test reviewed. The newly supplied third-lot workbook was independently streamed with openpyxl read_only=True, reset dimensions, typed-cell digests and row-level extraction for every sheet. Earlier first and second lot original byte hashes match the prior audit records; the relevant topology and section-cut/story-drift tables were independently reopened. All source files remain unchanged. The actual third lot had no exact repeated rows, repeated candidate result keys, formula/error cells or nonfinite numerics. Joint response ID, story and label agreed with the second-lot joint table across all ten response tables. Static linear force sums agree with first-lot section-cut magnitudes at the reported precision. The explicit full-gravity combination also reconciles to dead plus live per joint across all six components. Observed reaction-bearing and zero-reaction groups agree in count with the physical model contract; reaction zeros are not evidence of native restraints.

Ordinary and internal-mesh displacement rows and joint/design reaction rows were identical by exact keys and payloads in this supplied export; preserve their separate worksheet ownership. The relative/absolute time-history responses differ, and absolute displacement coverage is a subset of ordinary displacements. All available joint-drift displacement records agree with ordinary displacements; the first-lot controlling-joint drift records match exactly. Linear static adjacent-floor drift ratios checked using the verified 3.8 m coordinate spacing agree within displayed rounding. Do not compute time-history envelope drift by subtracting nonconcurrent maxima or sum response-spectrum or history envelopes as a base reaction. No change to native source case selection, solver physics, adopted periods, wall geometry, support assignment or loading.

Extend the canonical reference importer with prefilter joint identity diagnostics and guarded linear-static reaction group summaries. Preserve unknown and inconsistent source rows as diagnostic exceptions; do not sum incomplete or ambiguous groups. Explicitly exclude envelopes and combination cases from generic force sums; no summed joint moments without a common origin. Added a SQLite regression fixture for the new checks; it supplements rather than substitutes for the actual private workbook audit. Local full repository clone unavailable due to DNS; CI must verify the patch before merge. The 32 physical supports and 44 mesh points, full 1D+1L gravity and separate NBC 105 Table 5-1 seismic weight, and the adopted 12 m X-wall reference remain preserved. Native EDB binding, exact constraints, current matching OpenSees solution, full histories and NLTHA and NBC acceptance remain NOT_VERIFIED. Raw results, local file hashes and row references stay private.


## Post-merge cumulative diagnostic replay

PR #233 passed all nine triggered workflows and merged into main at
`8bcda6a618731a22fab4aa98194e880c65a2e7c8`. PRs #231 and #232 remain in its ancestry.
The merged reference diagnostic functions were fetched from that exact
commit, copied locally, and checked against the connector source length and
64-bit FNV fingerprint before execution. All three original workbook
SHA-256 values were rechecked against the previous private full-cell audits.
The small modal, connectivity, story-drift, story-force and reaction tables
were reread directly using openpyxl read_only; other large joint-response
tables were streamed from the prior actual-workbook CSV extractions. The
replay exercised the merged cross-lot diagnostic dispatcher with an
evidence-store adapter, not the complete production importer or SQLite
write path. All worksheet names have unique ownership; modal matches,
drift-to-joint coordinate matches, endpoint references, and all joint
response identities passed. The static reaction diagnostics reconciled to
FIRST LOT bottom section-cut force magnitudes at the source rounding
precision. Noneligible reaction rows were excluded from static summation,
not discarded from the source reference. Both prior audits and the explicit
full-gravity superposition check remain preserved.

For an actual complete local production import, use
`python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-reference FIRST.xlsx SECOND.xlsx THIRD.xlsx --reference-storage sqlite --reference-output NEW_PRIVATE_DIRECTORY`
with the actual file paths and a new output directory. Source EDB identity,
native restraints/constraints, matching OpenSees results, NLTHA convergence,
and NBC compliance remain NOT_VERIFIED. Native solver and approval rules,
32/44 support contract, 1D+1L benchmark, NBC seismic weight and 12 m wall
policy unchanged. No private workbook data, raw numerical results or source
file hashes were committed. The post-merge replay evidence is retained
locally.
