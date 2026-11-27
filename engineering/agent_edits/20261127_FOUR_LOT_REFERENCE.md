# Four-lot ETABS reference import

OpenAI Codex desktop extended the shared workbook reference reader and CLI
from main commit `daef7574401cf5090b746b5bfaefb8d1a5ae28c8`. The same
worksheet-owner catalog still verifies each workbook's identity. The first
and second lots retain their existing JSON command behavior.

The third and fourth lots add joint, wall, frame, shell and station tables.
SQLite storage streams the full selection through the common parser and
records repeat positions without merging distinct source samples at the
same normalized value. The SQLite manifest and database are published as
one completed local directory. Regression tests cover the legacy workflow,
unit conversion, source row identity, filtered aliases and interruption
before publication.

The reference has no production solver write path. The 32 physical
foundation supports, 44 wall-mesh points, full 1D+1L gravity benchmark and
NBC Table 5-1 seismic weight remain separate from workbook results. Source
EDB identity, complete native case coverage and ETABS/OpenSees numerical
equivalence require their existing evidence. The private workbooks and
generated reference are excluded from the commit.


## Fourth-lot split-source handoff (2026-11-27)

Editor: OpenAI ChatGPT (GPT-6.2). Base commit `3ea8b60b53f4af9e3ab30127aed5fea3e6277ddc`.
Read-first contract checked. The earlier FIRST, SECOND and THIRD LOT
integration PRs #231–233 and the post-merge replay record are retained.
The full fourth lot and two candidate fourth-lot parts were supplied.
Python/container startup returned a client error when attempting to open
the new inputs; the alternate file reader provided no worksheet content.
Consequently the fourth-lot cell scan, sheet ownership, row counts,
content fingerprints, equivalence of the split parts to the original
and engineering diagnostics are NOT_VERIFIED. No source results were
substituted and no numerical or solver code changed.

The existing CLI accepts an arbitrary list of input paths; the canonical
reference importer rejects a supported table with multiple workbook owners.
For the split form, use five complementary files (lots 1, 2, 3 and lot 4
parts 1 and 2), not those files plus the unsplit fourth lot. This is a
candidate selection until the actual worksheet-owner catalog confirms
disjoint supported tables. If a single supported worksheet was divided
by rows across parts, the existing importer does not implement a general
row-shard merge; retain both parts, audit them separately and resolve the
partition using source keys and units before importing. Do not rename
worksheets just to bypass the ownership check.

From the repository root, using actual local source paths and new private
output locations:

```powershell
$lots = @(
    "FIRST LOT.xlsx"
    "SECOND LOT.xlsx"
    "THIRD LOT.xlsx"
    "FOURTH LOT part 1.xlsx"
    "FOURTH LOT part 2.xlsx"
)
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-files $lots --audit-output "../FIVE_FILE_AUDIT.private.json"
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-files $lots --table-index-output "../FIVE_FILE_CATALOG.private.json"
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-reference $lots --reference-storage sqlite --reference-output "../FIVE_FILE_REFERENCE"
```

Replace the example names with exact paths. Review exit codes and audit
completeness before publishing the local reference. Compare the original
fourth lot with its parts in a separate audit, not a joint production
selection. Keep prior audit artifacts, inputs and outputs private and
unchanged. These commands and ownership rules were checked against the
current CLI and importer source; they were not successfully executed on
the new files. This is documentation-only, no new regression or native
solver execution. 32 physical + 44 mesh points PRESERVED; full gravity
1D+1L PRESERVED; NBC Table 5-1 seismic weight PRESERVED; 12 m X-wall
policy PRESERVED. All native model and code acceptance gates remain open.
