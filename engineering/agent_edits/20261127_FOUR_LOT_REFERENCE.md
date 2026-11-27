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
