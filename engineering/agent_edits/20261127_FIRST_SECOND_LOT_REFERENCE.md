# First- and second-lot ETABS reference integration

OpenAI Codex desktop extended the existing ETABS workbook reader and
registration CLI from main commit `ccdfb86b2e5ec13d69b386a39cc9e9000365572c`.
The parser uses the existing worksheet-owner catalog scan. The edit includes
the catalog and table-bundle readers, CLI, compatibility tests, source guides
and private-output ignore rule. The split-workbook gravity selection guard
was inspected and exercised.

The two supplied workbooks were processed locally. A separate readback
checked both workbook hashes, first-lot compatibility, and reconstruction of
all second-lot source rows from the retained records and repeat positions.
The modal overlaps and joint endpoint references were checked against the
available tables. The source workbooks, reference output and private
provenance stay local.

No model assignments or solver inputs are written by the reference command.
Source EDB identity, complete native case coverage and ETABS/OpenSees
numerical equivalence remain unverified.


## Cumulative independent workbook review and reference diagnostics

Editor: OpenAI ChatGPT (GPT-6.2). Base 62228b72b124d105f8cfe6170d2c7cc9bcd9a9ac. Prior FIRST LOT
audit and merged PR #231 preserved. The read-first physical-model contract,
existing reference importer, source guide and relevant regression tests govern
this additive change. The actual SECOND LOT was streamed with openpyxl
read_only=True, reset dimensions and typed-cell digests; every populated cell
and all worksheet rows inspected. Both original file hashes were checked;
FIRST LOT prior full scan was reused only after its hash matched, and the
response-spectrum and story-drift tables were independently reopened.

The frame table has exact repeated shell-edge records but also distinct
records sharing element IDs. Existing full-record deduplication and alias
provenance are retained, not ID-only deduplication. All exported endpoints
resolved; no coincident coordinates, zero frame/edge length or zero polygon
area in the source checks. Native constraint transfer and support restraints
are still unverified. Modal periods agreed across the common exact mode/case
keys, including FIRST LOT response spectra. Reported cumulative horizontal
mass and first 90% crossings were independently extracted; these are source
diagnostics only, not independently calculated mass or adopted NBC periods.
Every FIRST LOT controlling drift point had a unique story/label/coordinate
match within the diagnostic per-axis 1 mm tolerance. All raw results, private
hashes and row references remain local.

Extend the existing reference-only owner, not the native model generator:
add modal mass summaries and drift-to-joint diagnostics before case filtering
in JSON and SQLite. Added tests for unique, missing, mismatched and ambiguous
matches, and first reported 90% crossing. The local audit is actual-workbook
evidence, not a test of the full patched repository. Local repository clone
was unavailable (DNS). CI is required before merging the patch. No claim of
native convergence, equivalent model, full NBC compliance or solver changes.
32 physical + 44 mesh points PRESERVED; full gravity 1D+1L PRESERVED;
NBC Table 5-1 seismic weight PRESERVED; 12 m X-wall policy PRESERVED.
