# GUI, output provenance and public-repository security
**RV-SW-001:** P1 OPEN_HIGH — review GUI usability and reliable output export
**RV-SEC-001:** P0 INVESTIGATE — source/private evidence hygiene

The November 11 GUI shows crowded button rows, missing gravity 32/76/97 selection plot mode, empty ETABS comparison when native source not available, an apparent `'rz_32_kN'` missing field, duplicate/overlaid MRSM legend entries, missing SLS curves, and blank NLTH T1-X/Y input fields. The interface should display an explicit reason and repair action for each missing dataset, preserve copied run logs and provide scrollbars at every output viewport. Do not turn missing results into drawn zero curves.

**ZIP policy:** one case ZIP or all-module ZIP with nested Gravity, ESM, Modal, MRSM, LTH, NLTH, Comparisons, Logs, Plots and Reports, each with SHA256 manifest, run state, source EDB identity, user redaction summary and omitted-files list. Never silently include raw private EDB, user credential files or sensitive workbooks in a public upload. Avoid recursive packaging of old ZIPs and symlinks; output ZIPs for external sharing should be manually reviewed.

**Security audit limits:** previous tracked-file scan found no candidate secrets among inspected text files but omitted binary/LFS/historical content. Full Git history, LFS and third-party dependencies require independent examination, plus GitHub secret scanning and token rotation if a leak is found. No blanket claim that the public repo is clean.

**Implementation gate:** new GUI and exporter changes require Windows mouse-wheel scroll, keyboard scroll, ZIP integrity, output existence, copy-log and negative path/symlink/oversize tests. This REVIEW_MAIN commit adds **documentation only**, not a functional repair.
