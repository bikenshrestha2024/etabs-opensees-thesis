# nbc_pair_spectrum_audit.py — paired record candidate scale

**Source:** [nbc_pair_spectrum_audit.py](../../../../components/response_spectrum/nbc_pair_spectrum_audit.py)

**Code:** NBC 105:2025 §§9.3.2.2–9.3.2.3. Use the existing project response spectrum engine rather than duplicate it. Separate published scaling factors must each pass 0.33–3; use the lower on both pair components. Source files are read-only and SHA256 values stored.

**Limitations:** The existing method calculates a mean-spectrum candidate. It is NOT a verified code-specified fit tolerance, approved target, approved record set, or spectrum-match quality claim. Review periods/units/damping and independent site spectra.

**Tests:** [verify_nbc105_pair_spectrum_audit.py](../../../../tests/verify_nbc105_pair_spectrum_audit.py); injected candidate factors are logic tests, not a native spectral computation.

[Complete stage guide](../../../programs/32_NBC105_PAIR_SPECTRUM_AUDIT.md)
