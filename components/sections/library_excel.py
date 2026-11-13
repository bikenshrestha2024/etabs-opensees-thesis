"""Non-destructive Excel snapshot of the *same* four material-library GUI tables.

When: explicitly requested from 02 Model / Materials + Sections.
What: source-bound snapshot, not approved nonlinear model parameters.
Where: selected model export/02_MODEL/MATERIAL_SECTION_LIBRARY/.
Why: the original GUI is read-only; the workbook makes parameter provenance
and unresolved calibration evident in independently filterable Excel sheets.
Units: preserve native mm/MPa metadata and source kN-m properties without
implicit conversions.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import re

SHEETS = (
    ("Section formulations", "section_formulations"),
    ("Parameter values and citations", "parameter_values"),
    ("Current source parameters", "source_parameters"),
    ("Validation and limits", "validation_limits"),
)

def library_tables(folder):
    """Single source of truth used by both GUI and Excel; never infer approval."""
    from OpenSees_Mapping_Audit_V125 import (
        library, parameter_sources, source_parameter_inventory, validation_inventory
    )
    return [
        ("Section formulations", library()),
        ("Parameter values and citations", parameter_sources()),
        ("Current source parameters", source_parameter_inventory(folder)),
        ("Validation and limits", validation_inventory()),
    ]


def _safe_excel_value(value):
    """Neutralize formula injection from imported ETABS labels/source metadata."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, ensure_ascii=False, default=str)
    value = str(value)
    if value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def _fingerprint(path):
    path = Path(path)
    if not path.is_file():
        return "NOT_PRESENT"
    return sha256(path.read_bytes()).hexdigest()


def export_material_section_library(folder, path=None, *, tables=None):
    """Write an immutable-by-name material+section workbook and return the real path.

    The workbook stores read-only source records, not an OpenSees input file.
    It will never silently overwrite a previous snapshot or alter the .EDB.
    Explicit `tables` permits deterministic tests, with no native ETABS access.
    """
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
    except ImportError as exc:
        raise RuntimeError("openpyxl is required. Install with conda-forge: conda install -c conda-forge openpyxl") from exc

    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"Selected model export folder does not exist: {folder}")
    tables = library_tables(folder) if tables is None else tables
    if path is None:
        outdir = folder / "02_MODEL" / "MATERIAL_SECTION_LIBRARY"
        outdir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = outdir / f"OpenSees_Material_Section_Library_{timestamp}.xlsx"
    else:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Existing review workbook will not be overwritten: {path}")

    wb = Workbook()
    metadata = wb.active
    metadata.title = "00_README_PROVENANCE"
    metadata_rows = [
        ("Report", "OpenSees material and section library — 02 Model"),
        ("Scope", "Source inventory and illustrative/current parameter records; not a design/certification document"),
        ("Generated UTC", datetime.now(timezone.utc).isoformat()),
        ("Selected model export", str(folder.resolve())),
        ("Model data SHA256", _fingerprint(folder / "OpenSees_Complete_Model_Data_V118.json")),
        ("Model config SHA256", _fingerprint(folder / "OpenSees_Complete_Model_Config_V118.json")),
        ("Source EDB", "Original model is not opened or modified by this exporter"),
        ("Analysis basis", "NBC 105:2025 governs seismic; IS 16700:2023 project-required initial P-Delta and conventional slab bending only"),
        ("Current source parameters", "Elastic ETABS source values, NOT cyclic/reinforcement calibration"),
        ("Parameter values and citations", "Editable examples/reference values; unverified for project until evidence accepted"),
        ("FVD / BRB", "Requires specific device/test source; example inputs do not authorize use"),
        ("Data handling", "Exports only to the selected local model folder; review before sharing"),
        ("Workflow", "Do not re-import this spreadsheet as solver settings without validated import and source-hash check"),
    ]
    for row in metadata_rows:
        metadata.append([_safe_excel_value(v) for v in row])
    metadata.column_dimensions["A"].width = 29
    metadata.column_dimensions["B"].width = 108
    metadata.freeze_panes = "B2"

    used = set()
    for title, rows in tables:
        # Excel limits worksheet names to 31 characters and prohibits []:*?/\\.
        name = re.sub(r'[\\/*?:\[\]]', "_", title)[:31]
        original = name
        suffix = 2
        while name in used:
            name = original[:27] + f"_{suffix}"
            suffix += 1
        used.add(name)
        sheet = wb.create_sheet(name)
        if not rows:
            sheet.append(["status", "NO_ROWS"])
            continue
        keys = list(dict.fromkeys(key for row in rows for key in row.keys()))
        sheet.append([_safe_excel_value(k) for k in keys])
        for row in rows:
            sheet.append([_safe_excel_value(row.get(k)) for k in keys])
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for col, key in enumerate(keys, 1):
            values = [str(r.get(key, "")) for r in rows[:100]]
            maxlen = max([len(str(key)), *(len(v) for v in values)], default=12)
            sheet.column_dimensions[get_column_letter(col)].width = min(64, max(15, maxlen + 2))
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=False)
                if isinstance(cell.value, str) and cell.value.startswith(("http://", "https://")):
                    cell.hyperlink = cell.value
                    cell.style = "Hyperlink"

    for sheet in wb:
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="17345A")
            cell.alignment = Alignment(vertical="center", wrap_text=True)
        sheet.row_dimensions[1].height = 28
    wb.save(path)
    return str(path)
