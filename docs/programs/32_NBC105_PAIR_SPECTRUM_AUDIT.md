# 32 — NBC 105:2025 dual-component spectrum and common scaling check

The codebase already implemented NBC dynamic site spectra and record-by-record candidate scaling in `components/response_spectrum/site_spectrum_and_scaling.py`. This stage adds `nbc_pair_spectrum_audit.py` to evaluate actual X and Y recorded accelerograms using that existing engine, preserving both source SHA256 values and the candidate diagnostics. It selects the smaller factor for both components (§9.3.2.2(d)) when each independently computed factor lies between 0.33 and 3 (§9.3.2.2(c)). Any out-of-bounds pair is marked REJECT and **not clipped**. It does not modify input PEER files.

Run the launcher (Spyder-compatible Python 3.12, NumPy/OpenSees signal reader installed) with actual ground motion paths and independently verified site parameters. Example only (numbers are NOT design inputs):

```powershell
python 32_NBC105_PAIR_SPECTRUM_AUDIT.py --x "D:/Records/Kobe_X.AT2" --y "D:/Records/Kobe_Y.AT2" --soil C --Z 0.45 --I 1 --omega-u 1.5 --r-mu 4 --t1-x 3.6 --t1-y 3.2 --tn-x 0.15 --tn-y 0.12 --output "D:/Thesis/Audits/Kobe_Pair_NBC105.json"
```

**Mathematics implemented by the existing project:** (Sa_{target}(T)=C(T)/\Omega_u), mean-ordinate screening factor (f=\overline{Sa_{target}}/\overline{Sa_{record}}); apply the smaller of fX, fY to both horizontal histories. NBC does not prescribe this mean-ordinate fitting algorithm or specify a numeric spectral-error tolerance; therefore it is recorded as *candidate scale only*, requiring independent approval of actual spectral matching and record selection. Axial wall and device calibration, P-Delta and the complete paired XY/YX transient remain separate gates.

The CLI verifies candidate ranges only. It does not automatically satisfy all parts of NBC 105, nor does it approve the model. Official source: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf, §9.3.2.2. Code tests use deliberately injected candidate factors and do not claim a numerical site spectrum was run in CI.
