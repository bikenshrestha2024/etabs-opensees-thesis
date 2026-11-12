# Source guide — load_case_purpose.py

**What:** audit the declared purpose and individual load factors of gravity comparison and seismic mass/preload configurations.

**When:** on ETABS export review, model assembly, gravity case comparison, linear or nonlinear seismic analysis, and any changed occupancy load category.

**Why:** the gravity-only 100% dead + 100% all live (including roof live) and NBC 105:2025 seismic weight are intentionally different; mixing reactions is not an equivalence test.

**How:** `audit_load_case_purpose(profile, gravity_factors, mass_factors, category_overrides, present_patterns)` returns structured audit status, applied/expected pattern factors and explicit missing/mismatch flags. `classify_load_pattern` provides conservative name-based guesses, never auto-modifies material/load/mass.

**Where:** source `components/model/load_case_purpose.py`; integration `components/model/assembly.py::apply_gravity_profile`; review `07_REVIEW_MAIN/NBC105_2025_LOAD_CASE_PURPOSE_GUIDE.md`.

**Which:** named ETABS load patterns, user-reviewed categories (DEAD / STORAGE_LIVE / OTHER_LIVE / ROOF_LIVE), gravity and seismic mass factor maps; official NBC 105:2025 §5.2 Table 5-1 p. 30.

**Who:** project engineer identifies live category/occupancy; independent reviewer confirms code applicability; software maintainer validates that no physical model is silently changed.

**Tests:** `tests/test_nbc105_load_case_purpose.py`. **Limitation:** label/factor validation only, not physical mass reconciliation, P-Delta, ETABS equivalence or code acceptance. Cite official [DUDBC document](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf).
