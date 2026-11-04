# Stage 34 — NBC 105:2025 Soil C and Soil D targets for RC dual wall system

**Authoritative code:** [Nepal Government NBC 105:2025 official copy](https://ebps.kathmandu.gov.np/UploadFiles/NBC_105_2025_Sesmic_Design.pdf); **§4.1.1 Eq 4.1(1)**, **§4.1.2 Figure 4-2 / Eq 4.1(2), Table 4-1**, **§5.3 Table 5-2**, **§9.3.2.2(a–d)**.

**Important revision:** The research inputs include two possible soil response spectra, **Soil C and Soil D**, for the same **reinforced-concrete dual system with shear walls**. A previous 16-component waveform audit calculated conditional PSA deviations against ONLY a reconstructed Soil-C target plateau 0.625g. Never label those results as Soil-D matching. A target is not proof the record was matched against it.

## 1. Structural system (must match verified design)

NBC 105:2025 Table 5-2, Dual Systems, RC shear wall (item 19):
`R_mu=3.5`, `Omega_u=1.4`, `Omega_s=1.2`. These are not the factors for RC moment-resisting-only systems (`4, 1.5, 1.25`), nor RC shear-wall-only system (`3,1.3,1.15`). Project structural-system assignment requires actual frame/wall dual lateral action and detailing.

## 2. Soil C/D modal/NLTHA shape (§4.1.2)

| Parameter | Soil C | Soil D |
|---|---:|---:|
| Ta (s) | 0.1 | 0.5 |
| Tc (s) | 1.0 | 2.0 |
| Td (s) | 4.0 | 5.0 |
| alpha | 2.5 | 2.25 |

The equations for the **Figure 4-2 modal/NLTHA** spectral shape (NOT ESM shape):

```text
Ch(T) = 1 + (alpha - 1)*(T/Ta)         for 0 <= T < Ta
Ch(T) = alpha                           for Ta <= T < Tc
Ch(T) = alpha*Tc/T                      for Tc <= T < Td
Ch(T) = alpha*Tc*Td/T^2                 for Td <= T <= 6s
C(T) = Ch(T)*Z*I
Sa_target_ULS(T) = C(T)/Omega_u = Ch(T)*Z*I/1.4
```

Do not extend beyond 6 seconds without an independently reviewed engineering basis. NBC §9.3.2.2(b) also calls for modal interval `[Tn90, sqrt(R_mu)*T1]`: actual building T1 and mass-participation Tn90 may require explicit period-range interpretation.

### Illustrative zoning and importance only

If (and only if) **Z=.35**, **I=1.0**, these parameters produce C peak `2.5*.35/1.4 = 0.625g` and D peak `2.25*.35/1.4 = 0.5625g`. These are numeric examples, not verified site/importance values. Note also C and D have different plateau durations and long-period response: comparing merely peak ordinate values is insufficient.

**Critical site eligibility:** NBC §4.1.3.1 requires measured **Vs30 for height >40m**. Soil D must not be applied to a specific location purely because a separate D target spectrum exists. Document geotechnical Vs30, site location, site classification, Z and I for each actual model case.

## 3. Generate distinct C and D target files

Python 3.12, Spyder or terminal. All program dependencies are Python standard library.

```powershell
python 34_NBC105_RC_DUAL_C_D_TARGETS.py --Z 0.35 --I 1.0 --output "D:/Thesis/Target_Spectra" --step 0.005
```

Replace both Z and I with **actual reviewed** design values. Outputs:

- `NBC105_2025_RC_DUAL_Soil_C_ULS_Target_g.csv` — columns `T_s,Sa_g`.
- `NBC105_2025_RC_DUAL_Soil_D_ULS_Target_g.csv` — separate D target, not a relabel.
- `NBC105_2025_RC_DUAL_C_D_Target_Metadata.json` — system factors, actual entered Z/I, soil-specific Ta/Tc/Td/alpha, output destinations and nonapproval status.

The generator refuses extrapolation outside the Figure 4-2 0–6 s published domain. Source checks reject nonfinite inputs and swapped target curves. Regression `python tests/verify_nbc105_dual_target.py` compares piecewise breakpoints, 3s differences and cross-soil mismatch.

## 4. Check original SeismoMatch target and every matched suite

1. For EACH SeismoMatch project/session, store source target-curve file with SHA256, declared `soil_type`, `Z`, `I`, `Omega_u`, and matching period interval.
2. Explicitly label eight ground-motion pairs as belonging to the Soil C suite or Soil D suite. The same input records *could* be independently processed against both targets, but that requires independently saved, separately hashed matched output histories. **One file is not by itself proof of two target matches.**
3. Compare matched 5%-damped PSA against the **corresponding** C or D target on an identical period grid. Store actual error norms, maximum deviation, matching criteria and source hashes separately.
4. Verify original SeismoMatch component scale factors 0.33–3.0 and lower-of-pair rule (§9.3.2.2), then import *already-matched* Acc(g) at additional OpenSees `scale=1.0` and unit conversion factor 9.80665 m/s² per g.
5. Check source waveforms for Gorkha duration and Loma Prieta one-sample mismatch, and review actual current T1X/T1Y/Tn90X/Tn90Y.
6. Structural-system status and geotechnical soil type must be independently verified. Passing a target-generation unit test is not NBC compliance.

## 5. CI and limitations

- Core implementation: [`nbc105_dual_target.py`](../../components/response_spectrum/nbc105_dual_target.py).
- Program: [`34_NBC105_RC_DUAL_C_D_TARGETS.py`](../../34_NBC105_RC_DUAL_C_D_TARGETS.py).
- Regression: [`tests/verify_nbc105_dual_target.py`](../../tests/verify_nbc105_dual_target.py).
- This change **does not rerun the actual 16 matched accelerograms against Soil D** and does not alter any accelerogram. It corrects the scope, creates independent source targets, and provides auditable inputs for full matching verification.
