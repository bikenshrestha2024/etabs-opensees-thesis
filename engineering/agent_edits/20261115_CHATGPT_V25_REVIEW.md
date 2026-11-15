# V25 source editor attribution
Date: 2026-11-15. Target branch: `main`. Base SHA: `4e18cb32efcdb38ab110a6bbb4a3a7d3e655f723`.

Editor: ChatGPT/OpenAI GPT-6, connected GitHub repository API. No native ETABS/Windows desktop/OpenSees runtime was used.

Edited modules: `components/validation/saved_case_identity.py`, `components/gravity/etabs_reaction_support_filter.py`; tests `tests/test_saved_case_identity_v142.py`, `tests/verify_primary_32_support_reactions.py`; `.github/workflows/nltha-quality.yml`; respective source guides; V25 review records.

Scientific impact: safer handling of canonical result identity, stricter binary physical restraint input and atomic saved primary-32 reports. Does **not** change 32/76/97 model choices or perform numerical source equivalence. Original EDB/workbook and user earthquake inputs preserved.
