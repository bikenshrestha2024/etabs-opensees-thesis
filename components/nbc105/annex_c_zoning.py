"""NBC 105:2025 Annex C Table C-1: the project rows only (seismic zoning factor Z).

[REF NBC105-2025 Annex C Table C-1, printed pp. 100-114; §4.1.4, printed p. 26]
Table C-1 is printed with the columns SN, District, Local Units and PGA; clause
4.1.4 calls the PGA column the seismic zoning factor Z and says the Table value
is taken (not interpolated from Figure 4-3) for listed municipalities. Only the
rows the project needs are transcribed in
``docs/nbc105/annex_c/TABLE_C1_PROJECT_ROWS.csv``: the header, the project row
(serial 346, Kathmandu, Kirtipur Nagarpalika, printed p. 106, value 0.35), its
same-district neighbours and two rows with other values that prove the column
alignment. Every row carries a SHA-256 of its whitespace-normalised printed text
and is verified on load (a changed row fails closed). All other rows of the
753-row table are EXTERNAL_DATA_REQUIRED: ``table_c1_value`` raises
``TableC1DataRequired`` for them instead of guessing.

The project does not use Figure 4-3 interpolation (see ``project_zoning_factor``).
Source-to-code review only; this is not a seismic hazard study and not
engineering acceptance of the building.
"""
from __future__ import annotations

import csv
import hashlib
import math
import re
from pathlib import Path

__all__ = ["TABLE_C1_CSV", "PROJECT_TABLE_C1_SN", "TableC1DataRequired", "TableC1IntegrityError",
           "load_table_c1_project_rows", "table_c1_value", "project_zoning_factor"]

TABLE_C1_CSV = Path(__file__).resolve().parents[2] / "docs" / "nbc105" / "annex_c" / "TABLE_C1_PROJECT_ROWS.csv"
PROJECT_TABLE_C1_SN = 346
PROJECT_DISTRICT = "Kathmandu"
PROJECT_LOCAL_UNIT = "Kirtipur Nagarpalika"
_ALLOWED_VALUES = (0.25, 0.30, 0.35, 0.40)   # Figure 4-3 legend contours; Table C-1 values seen are 0.25, 0.3, 0.35, 0.4


class TableC1DataRequired(ValueError):
    """The requested Table C-1 row is not transcribed (EXTERNAL_DATA_REQUIRED).

    [REF NBC105-2025 Annex C Table C-1, printed pp. 100-114]
    """


class TableC1IntegrityError(ValueError):
    """A transcribed Table C-1 row failed its hash, page or column check.

    [REF NBC105-2025 Annex C Table C-1, printed p. 106]
    """


def _norm(text):
    return re.sub(r"\s+", " ", text).strip()


def _sha(text):
    return hashlib.sha256(_norm(text).encode("utf-8")).hexdigest()


def load_table_c1_project_rows(path=None):
    """Load and verify the transcribed Table C-1 rows (header, rows, figure usage, scope).

    [REF NBC105-2025 Annex C Table C-1, printed p. 106 (project rows), p. 100 (start of Annex C)]
    Checks the row hashes, that the header names the value column PGA, that every
    ROW record is on the page stated, that its text equals ``SN District Local
    Unit value`` and that values are one of 0.25, 0.30, 0.35, 0.40. Raises
    ``TableC1IntegrityError`` on any mismatch.
    """
    file = Path(path) if path else TABLE_C1_CSV
    with open(file, encoding="utf-8", newline="") as fh:
        records = list(csv.DictReader(fh))
    if not records:
        raise TableC1IntegrityError("empty Table C-1 transcription")
    header = [r for r in records if r["record_type"] == "COLUMN_HEADER"]
    if len(header) != 1 or header[0]["source_text"] != "SN District Local Units PGA":
        raise TableC1IntegrityError("missing or altered column header definition")
    rows = {}
    for r in records:
        if _sha(r["source_text"]) != r["sha256"]:
            raise TableC1IntegrityError("hash mismatch for %r" % r["source_text"][:60])
        if r["record_type"] != "ROW":
            continue
        if r["source_text"] != "%s %s %s %s" % (r["sn"], r["district"], r["local_unit"], r["value"]):
            raise TableC1IntegrityError("row text and fields differ for serial " + r["sn"])
        value = float(r["value"])
        if not any(math.isclose(value, v, abs_tol=1e-12) for v in _ALLOWED_VALUES):
            raise TableC1IntegrityError("value outside the printed Table C-1 set for serial " + r["sn"])
        if r["printed_page"] != "106" or r["value_column_label"] != "PGA":
            raise TableC1IntegrityError("unexpected page or column label for serial " + r["sn"])
        rows[int(r["sn"])] = r
    if PROJECT_TABLE_C1_SN not in rows:
        raise TableC1IntegrityError("project row 346 missing")
    return {"header": header[0], "rows": rows,
            "figure_usage": [r for r in records if r["record_type"] == "FIGURE_USAGE"],
            "scope": [r for r in records if r["record_type"] == "SCOPE"]}


def table_c1_value(district, local_unit, *, path=None):
    """Return the transcribed Table C-1 row for (district, local unit) or raise.

    [REF NBC105-2025 Annex C Table C-1, printed p. 106; §4.1.4 printed p. 26]
    Names are compared case-insensitively on whitespace-normalised text with the
    printed spelling (for example "Kirtipur Nagarpalika"; Table 4-3 prints the
    same unit as "Kirtipur Municipality"). A unit that is not transcribed raises
    ``TableC1DataRequired``: the value is never guessed or interpolated.
    """
    data = load_table_c1_project_rows(path)
    d, u = _norm(str(district)).lower(), _norm(str(local_unit)).lower()
    for sn, r in sorted(data["rows"].items()):
        if r["district"].lower() == d and r["local_unit"].lower() == u:
            return {"sn": sn, "district": r["district"], "local_unit": r["local_unit"],
                    "z": float(r["value"]), "printed_page": int(r["printed_page"]),
                    "source": "NBC105_2025_ANNEX_C_TABLE_C1"}
    raise TableC1DataRequired("Table C-1 row for %s / %s is not transcribed (EXTERNAL_DATA_REQUIRED)" % (district, local_unit))


def project_zoning_factor(*, path=None):
    """Z for the project (Kathmandu, Kirtipur Nagarpalika, serial 346): 0.35.

    [REF NBC105-2025 Annex C Table C-1 serial 346, printed p. 106; §4.1.4, printed p. 26]
    Source: the Table C-1 value, which printed 4.1.4 says governs for listed
    municipalities. Figure 4-3 interpolation is NOT used (``figure_4_3_used`` is
    False); its legend contours (0.25, 0.30, 0.35, 0.40) are recorded in the CSV.
    """
    hit = table_c1_value(PROJECT_DISTRICT, PROJECT_LOCAL_UNIT, path=path)
    if hit["sn"] != PROJECT_TABLE_C1_SN:
        raise TableC1IntegrityError("project row serial is not 346")
    return {"z": hit["z"], "sn": hit["sn"], "printed_page": hit["printed_page"],
            "district": hit["district"], "local_unit": hit["local_unit"],
            "source": hit["source"], "figure_4_3_used": False,
            "basis": "TABLE_C1_VALUE_GOVERNS_FOR_LISTED_MUNICIPALITIES_4.1.4_P26"}
