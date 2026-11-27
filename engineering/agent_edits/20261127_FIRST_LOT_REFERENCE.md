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


## Independent first-lot reinspection (2026-11-27)

Editor: OpenAI ChatGPT (GPT-6.2). Base: `7401aebc8fa7ed9579910d0b5e55b93445105a86`, main.
Read-first project contract checked. Existing owner: `components/inputs/etabs_table_bundle.py`;
reuse its reference-only schema and the existing worksheet-owner catalog.
No duplicate importer, solver implementation, or reference data was added.

The actual user-supplied first lot was streamed in Python/openpyxl read-only mode,
with advertised dimensions reset, every populated cell inspected, per-worksheet
typed-value digests and numeric profiles recorded locally, and the unchanged
source-byte hash verified on a separate pass. No Excel formula/error cells or
duplicate candidate result keys were observed. A second actual-workbook pass
checked exact story/case/type/step/direction keys, dimensionless drift against
reported drift in mm and the observed floor elevations, full gravity cut-force
superposition, ESM/RSA horizontal section-cut magnitudes and common modal periods.
Those checks passed at the recorded export precision. No synthetic workbook
was substituted. These are local evidence checks, not the repository regression
suite or a native solver rerun. Raw data, source hashes and paths stay private.

Interpretation requirements for downstream modules:
- Use worksheet column units, not Program Control current display units.
- Use the numeric drift ratio rather than the formatted reciprocal text;
  the export contains display strings such as 1/0 even for small nonzero drifts.
- A rounded-zero reported average can coexist with a very large finite ETABS
  max/average ratio. Keep the original result for traceability but classify
  its denominator as unresolved at export precision; do not treat it as
  confirmed torsional irregularity or replace the ratio with zero or one.
  Apply the governing case/step and meaningful response selection separately.
- Section-cut force is not a per-joint support reaction. The first lot cannot
  supply Joint Reactions, native restraints or constraint mappings. Do not
  use section cuts as nodal reactions or add their top and bottom envelopes.
- Preserve exact case names, directions, steps, force locations and signs.
  Time-history Max/Min rows are envelopes, not simultaneous full histories.
  A named time-history case does not establish membership in the adopted
  eight-pair Soil C suite. Zero exported link energy is not proof of device
  failure or proof that the intended damped model was analyzed.
- Reported modal periods are ETABS reference results, not a replacement for
  the adopted NBC empirical/Rayleigh period or mass-participation verification.

32 physical supports and 44 shear-wall mesh points: PRESERVED.
Full gravity 1D+1L and separate NBC Table 5-1 seismic weight: PRESERVED.
Two 12 m X-wall reference lines and approved reference-workbook policy: PRESERVED.
EDB/model configuration identity and native restraint/connection evidence remain
unavailable for this lot. Numerical convergence, ETABS/OpenSees equivalence,
experimental validation, NBC compliance and full NLTHA acceptance remain
NOT_VERIFIED by this audit. Repository checkout and local repository regression
execution were unavailable; no production source changes are represented here.
