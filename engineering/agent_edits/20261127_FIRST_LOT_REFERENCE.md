# First-lot ETABS reference import

OpenAI Codex desktop extended the existing native workbook tool on
`feat/etabs-first-lot-reference` from `b02d0d71a3d3eb6a74d5d9c8a5569dc99f736bf6`.
The existing table-bundle audit, production source resolver, registration CLI
and native earthquake reference extractor were inspected before the change.
The importer and CLI are covered in their existing source guides.

The import uses worksheet-specific column units, preserves exact ETABS
case and result-step identity, and records workbook hashes and coverage
in a local private JSON. The edited paths cover the existing table-bundle
reader and CLI, their documentation and regression tests, and the ignore
rule for the generated reference.

Verified the result rows, source row numbers, normalized values and case
counts against an independent read of the supplied workbook on Windows.
The workbook and its local path, hash and results remain private.
The clear-beam and workbook regression group also ran on Windows.
The source EDB linkage, native case equivalence and numerical agreement
remain unverified. The source reader has no model or solver write path.
