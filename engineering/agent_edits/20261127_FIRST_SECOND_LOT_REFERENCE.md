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
