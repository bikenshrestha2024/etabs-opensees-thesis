"""37 — read-only NLTHA thesis evidence dashboard (JSON, Excel CSV, PNG).

Example:
python 37_THESIS_EVIDENCE_DASHBOARD.py --manifest "D:/Thesis/Audits/thesis_evidence.json" --output-dir "D:/Thesis/Audits/Dashboard" --png

A green status verifies local source-file identity, NOT engineering acceptance.
"""
from components.validation.thesis_evidence_dashboard import main
if __name__=="__main__":
    raise SystemExit(main())
