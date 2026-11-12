# Source guide — load_case_purpose.py

**What:** audit the declared purpose and individual load factors of gravity comparison and seismic mass/preload configurations.

**When:** on ETABS export review, model assembly, gravity case comparison, linear or nonlinear seismic analysis, and any changed occupancy load category.

**Why:** the gravity-only 100% dead + 100% all live (including roof live) and NBC 105:2025 seismic weight are intentionally different; mixing reactions is not an equivalence test.

**How:** `audit_load_case_purpose(profile, gravity_factors, mass_factors, category_overrides, present_patterns)` returns structured audit status, applied/expected pattern factors and explicit missing/mismatch flags. `classify_load_pattern` provides conservative name-based guesses, never auto-modifies material/load/mass.

**Where:** source `components/model/load_case_purpose.py`; integration `components/model/assembly.py::apply_gravity_profile`; review `07_REVIEW_MAIN/NBC105_2025_LOAD_CASE_PURPOSE_GUIDE.md`.

**Which:** named ETABS load patterns, user-reviewed categories (DEAD / STORAGE_LIVE / OTHER_LIVE / ROOF_LIVE), gravity and seismic mass factor maps; official NBC 105:2025 §5.2 Table 5-1 p. 30.

**Who:** project engineer identifies live category/occupancy; independent reviewer confirms code applicability; software maintainer validates that no physical model is silently changed.

**Tests:** `tests/test_nbc105_load_case_purpose.py`. **Limitation:** label/factor validation only, not physical mass reconciliation, P-Delta, ETABS equivalence or code acceptance. Cite official [DUDBC document](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf).

## 2026-11-12 — incomplete source-pattern fail-closed fix

**What:** a factor check with no available source load patterns is `REVIEW_REQUIRED`, not `MATCHES_DECLARED_PURPOSE_FOR_CLASSIFIED_PATTERNS`. A Boolean `True` or `False` is not a valid factor despite Python's Boolean/int subtype behavior.

**Why:** source conversion and factor dictionaries can both be empty during an incomplete export. Without this guard, a zero-row audit could falsely report success. The audit remains read-only: never invent source loads, patterns or coefficients.

**When:** configured seismic or full-gravity profile inspection. **How:** emit `NO_LOAD_PATTERNS_TO_AUDIT` or `EMPTY_SOURCE_PATTERN_SET` in the source report; reject Boolean factors explicitly. **Where:** `components/model/load_case_purpose.py`; tests `tests/test_nbc105_load_case_purpose.py`. **Which:** actual source-pattern set and factor maps. **Who:** researcher classifies occupancy; structural reviewer validates NBC factor purposes; maintainer checks software.

**Limitations:** this checks category/factor completeness only. It does not prove ETABS input identity, seismic mass distribution or that gravity preload factors are identical to NBC seismic-weight coefficients for every nonlinear method.
