# SeismoMatch matched accelerogram provenance and NBC 105 period fitting audit

**Code:** [seismomatch_audit.py](../../../../components/nonlinear_time_history/seismomatch_audit.py)

**Source:** NBC 105:2025 §§4.1.1–4.1.2 and 9.3.2.2, official DUDBC PDF https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf

**Inputs:** original matching output file X/Y paths, declared source-processing state and OpenSees extra pair scale. Optional previously verified T1_X, T1_Y, Tn90_X, Tn90_Y, R_mu and fitting start/end.

**Behavior:** Identifies export headers from SeismoMatch (matched outputs with `Time Step` and `Acc(g)`), computes exact input SHA256, REJECTS a second amplitude scale if the source is already matched, and requires final OpenSees pair-scale 1.0 for matched exports. Only the source-acceleration conversion 9.80665 (for source `g` and model m/s²) is applied. It separately checks whether the stated fitting period range covers `[Tn90, sqrt(R_mu)*T1]` for both horizontal modal axes.

**Critical limitations:** Export accelerograms do NOT by themselves prove SeismoMatch's original independent component scale factors (0.33–3), the lower-of-two paired application, target spectral fit tolerance, or source/site record suitability. Do not calculate a nominal SeismoMatch factor from `PGA_matched/PGA_original` because the wavelet adjustment changes the time-domain waveform. Require original SeismoMatch session/report and independently checked spectra. For the study's reported `R_mu=3.5`, an example period `T1=3.622 s` implies an upper interval near `6.78 s`, beyond the chosen 6 s. The site's modal periods and the code's figure/equation upper-6-s limit require reviewer interpretation.

**Tests:** `tests/verify_seismomatch_audit.py`. All checks are source/metadata diagnostics, not full-building NLTHA validation.
