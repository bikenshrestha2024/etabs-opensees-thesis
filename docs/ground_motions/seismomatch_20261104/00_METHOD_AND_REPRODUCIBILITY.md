# Offline re-verification instructions

1. Keep the original 16 matched accelerograms in a local folder. Do not publish them to GitHub.
2. Pull latest `main`, then execute:

```powershell
python tools/verify_matched_waveforms.py --matched-dir "D:/Thesis/SeismoMatch/Matched" --output "D:/Thesis/SeismoMatch/Audits/Matched_Source_Integrity.json"
```

The tool reads the public CSV source register and compares the **exact SHA256, sampling dt, end time, and PGA** for all sixteen files; it does not alter time histories. The expected Loma Prieta end-duration difference is explicitly flagged in the pair summary. Source SHA mismatch blocks source-integrity confirmation.

If your local filenames differ only because a download client added a suffix, rename a **copy** to match the registered names; do not modify raw data to make the SHA pass.

For actual import, `source_records_already_scaled=true`, `scale=1.0`. `-factor=9.80665` converts g to SI. No additional SeismoMatch amplitude factor is applied.

The original study's complete 5%-damped response spectrum script, plots, per-original waveform comparisons and detailed JSON are in the separately generated verification ZIP attached in the ChatGPT conversation. This repository's standard-library verifier is for reproducible **waveform provenance**, not a fresh spectral fit. It must not be labeled NBC compliance solely because SHA/PGAs match.
