# V11 independent model fingerprint consistency gate — 2026-11-14

**Confirmed source-level gap:** V142's `recorded_result_model_sha` previously used an available `CASE_MANIFEST.json` SHA256 before consulting the source SHA embedded in the numerical result. If an MRSM/Deformation file was copied from another model into an otherwise valid case directory, the old V142 review could present the result as source-matched even when the two independent saved source fingerprints disagreed.

**Correction:** The source identity reader now examines both the canonical manifest and the saved MRSM/Deformation payload (or ESM drift response META). If both contain valid, different SHA256 digests, V142 excludes the response from drift/deflection charts and records `SOURCE_MANIFEST_RESULT_SHA_CONFLICT_EXCLUDED`, exact file, case and both hashes. Files remain untouched. Missing hashes stay unverified; matching serialized hashes do not prove ETABS model equivalence, native support/load equivalence or NBC structural acceptance.

**Regression:** `tests/test_saved_case_identity_v142.py` has a synthetic case where the manifest matches the current selected source but its numerical response belongs to another source, then verifies a matching replacement is accepted as a serialized model match only.

**Further gates:** Native Windows source checks, ULS/SLS stiffness, 32/76/97 support cases, shell MESH_04/08/16, P-Delta, device connection physics and full time-history durations remain open. No original ETABS/Excel input or saved solver file was changed.
