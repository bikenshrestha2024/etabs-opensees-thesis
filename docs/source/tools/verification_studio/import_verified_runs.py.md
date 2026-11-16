# tools/verification_studio/import_verified_runs.py

**Purpose:** Validate private local B01–B12 Verification Studio JSON files for consistency and publish a sanitized local `EVIDENCE_CONSISTENT` or `EVIDENCE_REJECTED` report. This does **not** run OpenSeesPy, read the source EDB, or confer thesis model acceptance.

## Inputs and output

```powershell
python tools/verification_studio/import_verified_runs.py --results "<PRIVATE_STUDIO_RUN>/cases" --out "<PRIVATE_EXPORT_CASE>/REVIEW_MAIN/VERIFICATION_STUDIO/B01_B12_SUMMARY.json"
```

Reads `B01.json` … `B12.json` from a local folder. Output is a JSON manifest of counts/statuses, solver/studio version and self-reported source SHA256, separate native/analytical case statuses, issues and explicitly `NOT_VERIFIED` thesis-specific gates. No source model content is copied into the output, and machine paths are omitted.

## Units, assumptions and acceptance

- The benchmark's own recorded metric units are retained in the original *private* reports, but the sanitized summary contains only counts and statuses.
- A metric counts only if its `passed` field is `true`, its actual/expected values are finite, and the recorded difference is within `max(1e-7, relative tolerance × |expected|)`. The input tolerance must be finite and between 0 and 1.
- Exactly 12 named cases, expected per-case metric counts, one consistent program version and source SHA, and one native OpenSeesPy version are required.
- B01–B11 must report native OpenSeesPy `PASS`; B12 must be `ANALYTICAL_PASS` with `NONE_ANALYTICAL_ONLY`; every case must report `etabs_native_equivalence: NOT_VERIFIED`.
- SHA is compared *between user-supplied cases*, **not independently matched against the current GitHub source**. Synthetic tests prove fail-closed parsing, not structural behavior.

## Security and limitations

Do not commit the source JSON, raw `report.html`, machine paths, 3D geometry, reinforcement or mapped 32-support files. The report is case-local, offline and read-only except for the explicit output file. The public review report contains only carefully selected generic test metrics.

No external network, ETABS API or OpenSeesPy API is called. Importing this module does not modify a thesis model. A consistent summary is **not** a cross-program validation or engineering approval.

See `REVIEW_MAIN/00_MODEL/20261116_B01_B12_STUDIO_RESULTS_AND_ACCEPTANCE.md` and `docs/00_THESIS_ACCEPTANCE_GATES.md`.
