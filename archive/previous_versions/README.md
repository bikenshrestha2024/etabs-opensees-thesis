# Historical versions archived from repository root

The newest tracked revision of each `_V###` file family remains at repository root. Superseded versions are preserved byte-for-byte using the same Git blob SHA under `archive/previous_versions/<family>/`. This change does not rewrite existing historical evidence or the functional module implementations.

**Moved files:** 83  
**Version families:** 21  
**Baseline commit:** `0176b638238c37b1e84f051c0b8efb7a7d71bf4f`

| File family | Latest root file | Older revisions originally present |
|---|---|---:|
| BUILD_INTEGRITY | `BUILD_INTEGRITY_V134.json` | 1 |
| CAPABILITIES_AND_LIMITS | `CAPABILITIES_AND_LIMITS_V134.md` | 3 |
| CHANGES | `CHANGES_V136.md` | 4 |
| CODE_REVIEW_INVENTORY | `CODE_REVIEW_INVENTORY_V134.csv` | 4 |
| DECISIONS_AND_SOURCES | `DECISIONS_AND_SOURCES_V134.md` | 3 |
| FILE_MANIFEST | `FILE_MANIFEST_V138.json` | 4 |
| MANIFEST | `MANIFEST_V167.json` | 6 |
| MODULE_INDEX | `MODULE_INDEX_V142.json` | 12 |
| NBC105_Analysis_Settings | `NBC105_Analysis_Settings_V109.py` | 1 |
| OpenSees_Analysis_Stack | `OpenSees_Analysis_Stack_V110.py` | 1 |
| REDUNDANCY_REVIEW | `REDUNDANCY_REVIEW_V133.json` | 1 |
| REGRESSION | `REGRESSION_V134.log` | 4 |
| RELEASE_NOTES | `RELEASE_NOTES_V167.md` | 2 |
| RELEASE | `RELEASE_V138.json` | 8 |
| REQUEST_COVERAGE | `REQUEST_COVERAGE_V134.md` | 1 |
| REVIEW | `REVIEW_V151.md` | 2 |
| SOURCE_CODE_MAP | `SOURCE_CODE_MAP_V134.md` | 3 |
| START_HERE | `START_HERE_V167.md` | 12 |
| VALIDATION | `VALIDATION_V134.md` | 3 |
| VALIDATION | `VALIDATION_V141.json` | 6 |
| VERIFICATION | `VERIFICATION_V130.json` | 4 |

## Runtime compatibility exceptions

- `NBC105_Analysis_Settings_V108.py` remains at the root alongside `NBC105_Analysis_Settings_V109.py` because the current GUI's generated analysis code imports V108 and resolves its path explicitly.
- `OpenSees_Analysis_Stack_V108.py` remains alongside V110 for the same reason. Moving these requires updating the exact import/export logic in `components/ui/application.py`, plus a Windows application smoke test. These two entries are deliberately not marked successfully archived.

## Move register

| Original | Archived location | Original Git blob SHA |
|---|---|---|
| `BUILD_INTEGRITY_V133.json` | [`archive/previous_versions/BUILD_INTEGRITY/BUILD_INTEGRITY_V133.json`](../../archive/previous_versions/BUILD_INTEGRITY/BUILD_INTEGRITY_V133.json) | `5efd892128ad5eab02b725bc0d6498164c39138a` |
| `CAPABILITIES_AND_LIMITS_V130.md` | [`archive/previous_versions/CAPABILITIES_AND_LIMITS/CAPABILITIES_AND_LIMITS_V130.md`](../../archive/previous_versions/CAPABILITIES_AND_LIMITS/CAPABILITIES_AND_LIMITS_V130.md) | `c7d41051e3fe31d94face15a7f3ce616e52ffcd5` |
| `CAPABILITIES_AND_LIMITS_V132.md` | [`archive/previous_versions/CAPABILITIES_AND_LIMITS/CAPABILITIES_AND_LIMITS_V132.md`](../../archive/previous_versions/CAPABILITIES_AND_LIMITS/CAPABILITIES_AND_LIMITS_V132.md) | `34abe2858aea36d180abf8e5283f0c11e00101bb` |
| `CAPABILITIES_AND_LIMITS_V133.md` | [`archive/previous_versions/CAPABILITIES_AND_LIMITS/CAPABILITIES_AND_LIMITS_V133.md`](../../archive/previous_versions/CAPABILITIES_AND_LIMITS/CAPABILITIES_AND_LIMITS_V133.md) | `f7bd3ecabc78a694e157ee0a8333854e840c9815` |
| `CHANGES_V131.md` | [`archive/previous_versions/CHANGES/CHANGES_V131.md`](../../archive/previous_versions/CHANGES/CHANGES_V131.md) | `685db91b713e27bb45d06ac2d379fef58c686dc3` |
| `CHANGES_V132.md` | [`archive/previous_versions/CHANGES/CHANGES_V132.md`](../../archive/previous_versions/CHANGES/CHANGES_V132.md) | `f2c33a4873671f970d435f1c75ed27ad97bdb498` |
| `CHANGES_V133.md` | [`archive/previous_versions/CHANGES/CHANGES_V133.md`](../../archive/previous_versions/CHANGES/CHANGES_V133.md) | `bd212a5f634e3d8bc3e0b9996e1c9a4760d67c7c` |
| `CHANGES_V134.md` | [`archive/previous_versions/CHANGES/CHANGES_V134.md`](../../archive/previous_versions/CHANGES/CHANGES_V134.md) | `4b94ae71407ba4a130073c5458530d0cb2a7497f` |
| `CODE_REVIEW_INVENTORY_V130.csv` | [`archive/previous_versions/CODE_REVIEW_INVENTORY/CODE_REVIEW_INVENTORY_V130.csv`](../../archive/previous_versions/CODE_REVIEW_INVENTORY/CODE_REVIEW_INVENTORY_V130.csv) | `5723e2f3d740cded803420b7384b6f5dfb3230fb` |
| `CODE_REVIEW_INVENTORY_V131.csv` | [`archive/previous_versions/CODE_REVIEW_INVENTORY/CODE_REVIEW_INVENTORY_V131.csv`](../../archive/previous_versions/CODE_REVIEW_INVENTORY/CODE_REVIEW_INVENTORY_V131.csv) | `b8d4bff565c43720c418534c33ed578be5f3389a` |
| `CODE_REVIEW_INVENTORY_V132.csv` | [`archive/previous_versions/CODE_REVIEW_INVENTORY/CODE_REVIEW_INVENTORY_V132.csv`](../../archive/previous_versions/CODE_REVIEW_INVENTORY/CODE_REVIEW_INVENTORY_V132.csv) | `10ba120390a114b2cb55499123d70fac9bfd178b` |
| `CODE_REVIEW_INVENTORY_V133.csv` | [`archive/previous_versions/CODE_REVIEW_INVENTORY/CODE_REVIEW_INVENTORY_V133.csv`](../../archive/previous_versions/CODE_REVIEW_INVENTORY/CODE_REVIEW_INVENTORY_V133.csv) | `5387a63b0d9a35a9636f24391716111b6219ce61` |
| `DECISIONS_AND_SOURCES_V130.md` | [`archive/previous_versions/DECISIONS_AND_SOURCES/DECISIONS_AND_SOURCES_V130.md`](../../archive/previous_versions/DECISIONS_AND_SOURCES/DECISIONS_AND_SOURCES_V130.md) | `8874250e2aeec2361de42c8e57ed17f0ac26e31d` |
| `DECISIONS_AND_SOURCES_V132.md` | [`archive/previous_versions/DECISIONS_AND_SOURCES/DECISIONS_AND_SOURCES_V132.md`](../../archive/previous_versions/DECISIONS_AND_SOURCES/DECISIONS_AND_SOURCES_V132.md) | `73e901db120cd6fb5042c8a5396669ef4f1b50e5` |
| `DECISIONS_AND_SOURCES_V133.md` | [`archive/previous_versions/DECISIONS_AND_SOURCES/DECISIONS_AND_SOURCES_V133.md`](../../archive/previous_versions/DECISIONS_AND_SOURCES/DECISIONS_AND_SOURCES_V133.md) | `f13b3da5cba88d60b34a35a272febb7af8b3f1ea` |
| `FILE_MANIFEST_V134.json` | [`archive/previous_versions/FILE_MANIFEST/FILE_MANIFEST_V134.json`](../../archive/previous_versions/FILE_MANIFEST/FILE_MANIFEST_V134.json) | `c9d3183759f33729d59b8f7d781ec80066a22254` |
| `FILE_MANIFEST_V135.json` | [`archive/previous_versions/FILE_MANIFEST/FILE_MANIFEST_V135.json`](../../archive/previous_versions/FILE_MANIFEST/FILE_MANIFEST_V135.json) | `6f41066d52c2aa235e76111fe2467a0ff0f4cffc` |
| `FILE_MANIFEST_V136.json` | [`archive/previous_versions/FILE_MANIFEST/FILE_MANIFEST_V136.json`](../../archive/previous_versions/FILE_MANIFEST/FILE_MANIFEST_V136.json) | `31541b3fbd9a7e06493e21ec53a303e48c4827e1` |
| `FILE_MANIFEST_V137.json` | [`archive/previous_versions/FILE_MANIFEST/FILE_MANIFEST_V137.json`](../../archive/previous_versions/FILE_MANIFEST/FILE_MANIFEST_V137.json) | `440bf810a041ad41bf9c1a4f207f0270ce695369` |
| `MANIFEST_V139.json` | [`archive/previous_versions/MANIFEST/MANIFEST_V139.json`](../../archive/previous_versions/MANIFEST/MANIFEST_V139.json) | `8f535e3491dde33d4a7d6edbfacc451e07d6c1fe` |
| `MANIFEST_V140.json` | [`archive/previous_versions/MANIFEST/MANIFEST_V140.json`](../../archive/previous_versions/MANIFEST/MANIFEST_V140.json) | `44e408736191c77a46db034016835081983f6e07` |
| `MANIFEST_V141.json` | [`archive/previous_versions/MANIFEST/MANIFEST_V141.json`](../../archive/previous_versions/MANIFEST/MANIFEST_V141.json) | `48b351546fa0e187b4e6f95744272e09576cd334` |
| `MANIFEST_V142.json` | [`archive/previous_versions/MANIFEST/MANIFEST_V142.json`](../../archive/previous_versions/MANIFEST/MANIFEST_V142.json) | `39c0fb6fa05fade96e5ab2f53a6d0e3d3580e309` |
| `MANIFEST_V143.json` | [`archive/previous_versions/MANIFEST/MANIFEST_V143.json`](../../archive/previous_versions/MANIFEST/MANIFEST_V143.json) | `e37d3164d1bd48bf15cef491b94c00e0d18cc0cf` |
| `MANIFEST_V144.json` | [`archive/previous_versions/MANIFEST/MANIFEST_V144.json`](../../archive/previous_versions/MANIFEST/MANIFEST_V144.json) | `8d48e3cea7078205a06844a05d0789c83135c829` |
| `MODULE_INDEX_V130.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V130.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V130.json) | `dce3c0045f28c3eb1f9c2882dd96d6253f444111` |
| `MODULE_INDEX_V131.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V131.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V131.json) | `22e005715f14a64dc88dc6a8ea712d95513cd68c` |
| `MODULE_INDEX_V132.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V132.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V132.json) | `2e0184eaab2f87a51cad53ee56ec594929034bc9` |
| `MODULE_INDEX_V133.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V133.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V133.json) | `a163392fd72bf2ff559cbd45628c7e6d14598d36` |
| `MODULE_INDEX_V134.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V134.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V134.json) | `2f21953cb61d7a1d179a85cc827f28a1c2b47e72` |
| `MODULE_INDEX_V135.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V135.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V135.json) | `1281ea23e2c6ffc8cc6a938a5c6f9d573d1b903b` |
| `MODULE_INDEX_V136.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V136.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V136.json) | `1281ea23e2c6ffc8cc6a938a5c6f9d573d1b903b` |
| `MODULE_INDEX_V137.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V137.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V137.json) | `507016bafd03d11a6255f8afe744038b81173870` |
| `MODULE_INDEX_V138.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V138.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V138.json) | `e87e2918e8d652854d00a4d53275dd6146719187` |
| `MODULE_INDEX_V139.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V139.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V139.json) | `e87e2918e8d652854d00a4d53275dd6146719187` |
| `MODULE_INDEX_V140.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V140.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V140.json) | `e87e2918e8d652854d00a4d53275dd6146719187` |
| `MODULE_INDEX_V141.json` | [`archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V141.json`](../../archive/previous_versions/MODULE_INDEX/MODULE_INDEX_V141.json) | `24a3261d9381dfe5b2ed6dd0e3344792939ce0b2` |
| `REDUNDANCY_REVIEW_V130.json` | [`archive/previous_versions/REDUNDANCY_REVIEW/REDUNDANCY_REVIEW_V130.json`](../../archive/previous_versions/REDUNDANCY_REVIEW/REDUNDANCY_REVIEW_V130.json) | `2c94512f62734f83976a2a527bd74880afbf774e` |
| `REGRESSION_V130.log` | [`archive/previous_versions/REGRESSION/REGRESSION_V130.log`](../../archive/previous_versions/REGRESSION/REGRESSION_V130.log) | `8d8b89265ae67e03e98eaee85f68ee8b6c70b670` |
| `REGRESSION_V131.log` | [`archive/previous_versions/REGRESSION/REGRESSION_V131.log`](../../archive/previous_versions/REGRESSION/REGRESSION_V131.log) | `8a2de58af3793bdebdf10e264d38a4e6173eac78` |
| `REGRESSION_V132.log` | [`archive/previous_versions/REGRESSION/REGRESSION_V132.log`](../../archive/previous_versions/REGRESSION/REGRESSION_V132.log) | `cedd6f8951ac02a2a8635698cc7304d840caeb61` |
| `REGRESSION_V133.log` | [`archive/previous_versions/REGRESSION/REGRESSION_V133.log`](../../archive/previous_versions/REGRESSION/REGRESSION_V133.log) | `9ea635c6b67c3b294ca14bbbe54b0ccdf17e4bff` |
| `RELEASE_NOTES_V146.md` | [`archive/previous_versions/RELEASE_NOTES/RELEASE_NOTES_V146.md`](../../archive/previous_versions/RELEASE_NOTES/RELEASE_NOTES_V146.md) | `20cb24f462d1bd9da861ef016dc35c3cdee4bbfe` |
| `RELEASE_NOTES_V147.md` | [`archive/previous_versions/RELEASE_NOTES/RELEASE_NOTES_V147.md`](../../archive/previous_versions/RELEASE_NOTES/RELEASE_NOTES_V147.md) | `bc18c6e0902c7286e244be9ce9c4494d40673e69` |
| `RELEASE_V130.json` | [`archive/previous_versions/RELEASE/RELEASE_V130.json`](../../archive/previous_versions/RELEASE/RELEASE_V130.json) | `d4128296e848a8957ef90b2f0ec0d6ba2509b225` |
| `RELEASE_V131.json` | [`archive/previous_versions/RELEASE/RELEASE_V131.json`](../../archive/previous_versions/RELEASE/RELEASE_V131.json) | `a6b6e902809de47ed1622bd79f21a881db307aad` |
| `RELEASE_V132.json` | [`archive/previous_versions/RELEASE/RELEASE_V132.json`](../../archive/previous_versions/RELEASE/RELEASE_V132.json) | `d8bcbe1bc116ed88247c9c8bc01a83ad66a8409b` |
| `RELEASE_V133.json` | [`archive/previous_versions/RELEASE/RELEASE_V133.json`](../../archive/previous_versions/RELEASE/RELEASE_V133.json) | `6e508717b0925dc6264e621088fe19745636d92e` |
| `RELEASE_V134.json` | [`archive/previous_versions/RELEASE/RELEASE_V134.json`](../../archive/previous_versions/RELEASE/RELEASE_V134.json) | `403a75445704ff2b6515653225ea325456a41688` |
| `RELEASE_V135.json` | [`archive/previous_versions/RELEASE/RELEASE_V135.json`](../../archive/previous_versions/RELEASE/RELEASE_V135.json) | `6a412d541fe7ca0040cd14556348fd595d86504e` |
| `RELEASE_V136.json` | [`archive/previous_versions/RELEASE/RELEASE_V136.json`](../../archive/previous_versions/RELEASE/RELEASE_V136.json) | `a0dffb1dd9830c7aa8d3f7f8d0bbaf9284312e32` |
| `RELEASE_V137.json` | [`archive/previous_versions/RELEASE/RELEASE_V137.json`](../../archive/previous_versions/RELEASE/RELEASE_V137.json) | `c0b2a5550a21fbcd3a4e1a8cff5637d5864b17ea` |
| `REQUEST_COVERAGE_V133.md` | [`archive/previous_versions/REQUEST_COVERAGE/REQUEST_COVERAGE_V133.md`](../../archive/previous_versions/REQUEST_COVERAGE/REQUEST_COVERAGE_V133.md) | `99ee4de89b27a32cd772eb909f2c3c3b4ee44cf9` |
| `REVIEW_V148.md` | [`archive/previous_versions/REVIEW/REVIEW_V148.md`](../../archive/previous_versions/REVIEW/REVIEW_V148.md) | `9b161945bf71b0b2f7a6ba6061c2aec66982cc15` |
| `REVIEW_V150.md` | [`archive/previous_versions/REVIEW/REVIEW_V150.md`](../../archive/previous_versions/REVIEW/REVIEW_V150.md) | `3bdf29c076eb1a1db933ee0e6567afbce361fab5` |
| `SOURCE_CODE_MAP_V131.md` | [`archive/previous_versions/SOURCE_CODE_MAP/SOURCE_CODE_MAP_V131.md`](../../archive/previous_versions/SOURCE_CODE_MAP/SOURCE_CODE_MAP_V131.md) | `9784a36f1b3be18019d42f9933e62c24fde0e670` |
| `SOURCE_CODE_MAP_V132.md` | [`archive/previous_versions/SOURCE_CODE_MAP/SOURCE_CODE_MAP_V132.md`](../../archive/previous_versions/SOURCE_CODE_MAP/SOURCE_CODE_MAP_V132.md) | `65de32a474fd9d5f6df8696a90398811c9883bdd` |
| `SOURCE_CODE_MAP_V133.md` | [`archive/previous_versions/SOURCE_CODE_MAP/SOURCE_CODE_MAP_V133.md`](../../archive/previous_versions/SOURCE_CODE_MAP/SOURCE_CODE_MAP_V133.md) | `c89e20f85f7ebd49496757d66bd35d9c12999507` |
| `START_HERE_V139.md` | [`archive/previous_versions/START_HERE/START_HERE_V139.md`](../../archive/previous_versions/START_HERE/START_HERE_V139.md) | `3fad0b61798238c7345b577d1cf90cdfab8a3188` |
| `START_HERE_V140.md` | [`archive/previous_versions/START_HERE/START_HERE_V140.md`](../../archive/previous_versions/START_HERE/START_HERE_V140.md) | `5375e6b9c295adf0c94a60bbc86bff81b9ab827a` |
| `START_HERE_V141.md` | [`archive/previous_versions/START_HERE/START_HERE_V141.md`](../../archive/previous_versions/START_HERE/START_HERE_V141.md) | `718997ed00e01768caf8421405b83b1a22e80b2c` |
| `START_HERE_V142.md` | [`archive/previous_versions/START_HERE/START_HERE_V142.md`](../../archive/previous_versions/START_HERE/START_HERE_V142.md) | `db5a798b9e19c66e8fc68fc2171f5ae9b3599e55` |
| `START_HERE_V143.md` | [`archive/previous_versions/START_HERE/START_HERE_V143.md`](../../archive/previous_versions/START_HERE/START_HERE_V143.md) | `edb78d5fa4561e71d9a850023304db254036f813` |
| `START_HERE_V144.md` | [`archive/previous_versions/START_HERE/START_HERE_V144.md`](../../archive/previous_versions/START_HERE/START_HERE_V144.md) | `89901c50f81be685248a3854dcffd099c3910f46` |
| `START_HERE_V152.md` | [`archive/previous_versions/START_HERE/START_HERE_V152.md`](../../archive/previous_versions/START_HERE/START_HERE_V152.md) | `0a04a45cae9cadf3bab308b4cb132264e2b48edf` |
| `START_HERE_V155.md` | [`archive/previous_versions/START_HERE/START_HERE_V155.md`](../../archive/previous_versions/START_HERE/START_HERE_V155.md) | `91877e5b36bc1aa609e040bb457456e6cae8e30f` |
| `START_HERE_V156.md` | [`archive/previous_versions/START_HERE/START_HERE_V156.md`](../../archive/previous_versions/START_HERE/START_HERE_V156.md) | `2900b16301cd959d47d1c10f0bfed75db6cc59cc` |
| `START_HERE_V159.md` | [`archive/previous_versions/START_HERE/START_HERE_V159.md`](../../archive/previous_versions/START_HERE/START_HERE_V159.md) | `e6c7a6f64a75802b0f47cbdf134e3a6719d2bd73` |
| `START_HERE_V160.md` | [`archive/previous_versions/START_HERE/START_HERE_V160.md`](../../archive/previous_versions/START_HERE/START_HERE_V160.md) | `1f6dd39c1262c2c1f22ef5e3f1bf887f7044f166` |
| `START_HERE_V161.md` | [`archive/previous_versions/START_HERE/START_HERE_V161.md`](../../archive/previous_versions/START_HERE/START_HERE_V161.md) | `2567d5945c6785688dd01e4b43ea8450213fb727` |
| `VALIDATION_V130.md` | [`archive/previous_versions/VALIDATION/VALIDATION_V130.md`](../../archive/previous_versions/VALIDATION/VALIDATION_V130.md) | `eedf450a50be44c9353276e93107ae321204dd74` |
| `VALIDATION_V132.md` | [`archive/previous_versions/VALIDATION/VALIDATION_V132.md`](../../archive/previous_versions/VALIDATION/VALIDATION_V132.md) | `8bcd774127720884e8e922388e435d538003b4f0` |
| `VALIDATION_V133.md` | [`archive/previous_versions/VALIDATION/VALIDATION_V133.md`](../../archive/previous_versions/VALIDATION/VALIDATION_V133.md) | `86e05803c219e0269739b643b2ca4bd2081e5323` |
| `VALIDATION_V135.json` | [`archive/previous_versions/VALIDATION/VALIDATION_V135.json`](../../archive/previous_versions/VALIDATION/VALIDATION_V135.json) | `ab64fb6987e1081a489b98c6faa9f2dd55d5a9d5` |
| `VALIDATION_V136.json` | [`archive/previous_versions/VALIDATION/VALIDATION_V136.json`](../../archive/previous_versions/VALIDATION/VALIDATION_V136.json) | `5808b5da6ab6433e49cc9f82bf574682765cdf0d` |
| `VALIDATION_V137.json` | [`archive/previous_versions/VALIDATION/VALIDATION_V137.json`](../../archive/previous_versions/VALIDATION/VALIDATION_V137.json) | `c5f23e02a104a70f3ed04e8756463f14a47d6075` |
| `VALIDATION_V138.json` | [`archive/previous_versions/VALIDATION/VALIDATION_V138.json`](../../archive/previous_versions/VALIDATION/VALIDATION_V138.json) | `14b322793719243de8a325739fcdf5d5907e9363` |
| `VALIDATION_V139.json` | [`archive/previous_versions/VALIDATION/VALIDATION_V139.json`](../../archive/previous_versions/VALIDATION/VALIDATION_V139.json) | `6067134b1f45579331fd17158dd0db50a432f720` |
| `VALIDATION_V140.json` | [`archive/previous_versions/VALIDATION/VALIDATION_V140.json`](../../archive/previous_versions/VALIDATION/VALIDATION_V140.json) | `b77f2be6169c44a8d6847612553a7aef26c45445` |
| `VERIFICATION_V118.json` | [`archive/previous_versions/VERIFICATION/VERIFICATION_V118.json`](../../archive/previous_versions/VERIFICATION/VERIFICATION_V118.json) | `cb0e670a0c1d90f6c556afff5c051bf2393bb523` |
| `VERIFICATION_V123.json` | [`archive/previous_versions/VERIFICATION/VERIFICATION_V123.json`](../../archive/previous_versions/VERIFICATION/VERIFICATION_V123.json) | `4807c694ff3960c4c8438b73d749f0d3fc15e6e8` |
| `VERIFICATION_V124.json` | [`archive/previous_versions/VERIFICATION/VERIFICATION_V124.json`](../../archive/previous_versions/VERIFICATION/VERIFICATION_V124.json) | `1712cfec9dc1fef18b39566f29c1700546722089` |
| `VERIFICATION_V125.json` | [`archive/previous_versions/VERIFICATION/VERIFICATION_V125.json`](../../archive/previous_versions/VERIFICATION/VERIFICATION_V125.json) | `7d4320ff6decdc8d5f30b8d85649faba3ad04fc9` |

## Notes

- Workflow launchers `01_...`, `02_...` etc. are functional execution steps, not semantic version numbers. They were left in place.
- Nested saved-project snapshots remain unchanged and already have their own folder.
- Old manifests and audit reports are historical evidence. They may name original root paths; those references describe their historical state.
- JSON per-file field guides are regenerated from the full checkout after these moves. Re-run the offline documentation generator whenever paths change.
