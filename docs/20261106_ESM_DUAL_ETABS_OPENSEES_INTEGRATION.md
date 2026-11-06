# Dual equivalent-static modules — integrated into main ESM GUI

Open the existing `12_EQUIVALENT_STATIC.py` entry point and select **ESM analysis module**.

- **OpenSees Direct Equivalent Static** (default): existing repository NBC 105 ESM workflow, verified story seismic-weight ledger, X/Y force export and OpenSeesPy analysis runners. Existing Rayleigh period, ULS/SLS, earthquake-direction and torsion preflight requirements still apply.
- **ETABS Linked Equivalent Static**: select a local EDB, original NBC105 calculator workbook and original ETABS integrated Python calculation engine from the earlier user-supplied dual-module ZIP. The adapter populates a fresh workbook copy using the original ETABS/OAPI opening and wall geometry routine and original Python/Excel method. Provenance JSON includes SHA256 of EDB, source/output workbook and engine plus calculated Aw/T/C/k and original contribution row references.

ETABS mode can be launched from **ETABS Linked: populate original Excel**, or by selecting that mode and clicking **Calculate + export**. This is an on-demand local Windows path; it does NOT call the response-spectrum scaling operation, save the EDB, modify EQX/EQY or silently replace any workbook values. Do not confuse this with the older integrated ETABS response-spectrum updater.

**Important runtime dependency**: the uploaded original engine `etabs_nbc105_legacy_engine.py` and Excel calculator are *not* committed as copies to the public GitHub repository. Browse to your locally stored original files using the new dialog. The engineering geometry method deliberately remains in that original local engine and is not reimplemented with a substitute Aw formula.

**Validation gates**: check source EDB identity, units, individual opening assignments and continuous piers, representative X/Y wall contributions, ULS/SLS and adopted periods. The ETABS adapter has not been run against the user's Windows ETABS instance in CI; neither computational success nor a workbook export certifies NBC 105 acceptance. Independently verify OpenSees mass, geometry, reactions and ULS/SLS model equivalence before comparing results.

Run lightweight structural checks: `python -m unittest discover -s tests -p 'verify_esm_dual_module.py'`.
