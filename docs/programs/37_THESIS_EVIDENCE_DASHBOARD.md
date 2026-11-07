# 37 — Thesis Evidence Dashboard

**Entry point:** [37_THESIS_EVIDENCE_DASHBOARD.py](../../37_THESIS_EVIDENCE_DASHBOARD.py). Core: [thesis_evidence_dashboard.py](../../components/validation/thesis_evidence_dashboard.py).

A stand-alone, read-only **stage and file identity screen** for the thesis. It does not run OpenSees or ETABS, and does not qualify NBC 105 compliance. It uses a user-authored manifest containing stage status and independently recorded SHA256 of actual local evidence files. Missing files, changed SHA256 and premature stage VERIFICATION are blocked. The status `EVIDENCE_READY` is never promoted automatically.

Example manifest (replace each stage after actual experiments with its own files and hashes):

```json
{
  "stages": {
    "00_PROVENANCE": {"status": "BLOCKED", "evidence": []},
    "01_ETABS_OPENSEES_GEOMETRY": {"status": "NOT_STARTED", "evidence": []}
  }
}
```

Run from repository root:

```powershell
python 37_THESIS_EVIDENCE_DASHBOARD.py --manifest "D:/Thesis/Audits/thesis_evidence.json" --output-dir "D:/Thesis/Audits/Dashboard" --png
```

Outputs: `Thesis_Evidence_Dashboard.json`, `Thesis_Evidence_Dashboard.csv` (open in Excel), optionally `Thesis_Evidence_Dashboard.png` (Matplotlib). Exit code **2** means the identity screen is incomplete, not a solver failure; exit code **0** only means that all user-declared stage evidence file identities matched and were declared verified, NOT that the engineering passed.

For a reference evidence entry, compute the independent file digest using Windows PowerShell `Get-FileHash -Algorithm SHA256 "D:/Thesis/..." `. For a stage to be declared VERIFIED, attach its actual evidence (for example ETABS source exports and comparison, native gravity/modal logs, native wall experiment overlay, accepted full time histories). These SHA digests do not analyze physical response.

Review existing native analysis/calibration gates under `components/nonlinear_time_history/`, especially `full_record_gate.py`, `soil_c_physics_preflight.py`, `variant_comparison.py` and `device_recording.py`. This dashboard is an organizational record only.

Required engineering order: 00 provenance → 01 3D geometry → 02 gravity/mass → 03 wall calibration → 04 frame/device calibration → 05 modal/damping → 06 NBC paired-motion audit → 07 ZERO/X/Y/XY diagnostic → 08 complete XY/YX NLTHA → 09 M0–M6 comparison → 10 reporting/review.

Primary standards and interpretation source: [DUDBC NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf). Refer to the repository's `docs/00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md` clause ledger for project-specific claimed §9.3 requirements, and independently verify every quoted clause against the actual issued code PDF; foreign standards are supplementary unless adopted by the project authority.
