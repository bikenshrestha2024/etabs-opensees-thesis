"""[REF docs/source/components/inputs/etabs_table_bundle.py.md]
Source-EDB-bound ETABS workbook registration. No file moves or uploads.

This records workbook identities and verified sheet inventories. It is not a
numerical ETABS/OpenSees equivalence comparison.
"""
from __future__ import annotations
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

_REQUIRED_ASSIGNMENT_SHEETS=(
    "Material List by Object Type",
    "Material List by Section Prop",
    "Frame Assigns - Summary",
    "Frame Assigns - End Len Offsets",
    "Frame Assigns - Insertion Point",
    "Area Assigns - Insertion Point",
    "Load Pattern Definitions",
    "Shell Uniform Load Sets",
)

# ETABS table-specific headers and units observed in the first analysis lot.
# Each entry has text/step keys and the units required for its numeric fields.
_CASE_COLUMNS = ("Output Case", "Case Type", "Step Type", "Step Number")
_STORY_CASE = ("Story", *_CASE_COLUMNS)
_WALL_FORCES = dict.fromkeys(("P", "V2", "V3"), "kN") | dict.fromkeys(("T", "M2", "M3"), "kN-m")
_FIRST_LOT_TABLES = {
    "Tributary Area and LLRF": (
        ("Story", "Label", "Unique Name", "Type"), {"Tributary Area": "m²", "LLRF": ""}),
    "Total Energy Components": (_CASE_COLUMNS, dict.fromkeys((
        "Input Energy", "Kinetic Energy", "Potential Energy", "Global Damping Energy",
        "Link Damper Energy", "Link Hysteresis Energy", "Energy Error"), "kN-m")),
    "Story Stiffness": (_STORY_CASE, {
        "Shear X": "kN", "Drift X": "mm", "Stiff X": "kN/m",
        "Shear Y": "kN", "Drift Y": "mm", "Stiff Y": "kN/m"}),
    "Story Max Over Avg Drifts": (
        (*_STORY_CASE, "Direction"), {"Max Drift": "mm", "Avg Drift": "mm", "Ratio": ""}),
    "Story Max Over Avg Disp": (
        (*_STORY_CASE, "Direction"), {"Maximum": "mm", "Average": "mm", "Ratio": ""}),
    "Story Forces": ((*_STORY_CASE, "Location"),
                      dict.fromkeys(("P", "VX", "VY"), "kN") | dict.fromkeys(("T", "MX", "MY"), "kN-m")),
    "Story Drifts": ((*_STORY_CASE, "Direction", "Drift/", "Label"),
                      {"Drift": "", **dict.fromkeys(("X", "Y", "Z"), "m")}),
    "Story Accelerations": (_STORY_CASE, dict.fromkeys(("UX", "UY", "UZ"), "mm/sec²") |
                            dict.fromkeys(("RX", "RY", "RZ"), "rad/sec²")),
    "Spandrel Forces": ((*_STORY_CASE, "Spandrel", "Location"), _WALL_FORCES),
    "Response Spectrum Modal Info": (("SpecCase", "ModalCase", "Mode"), {
        "Period": "sec", "DampRatio": "", **dict.fromkeys(("U1Acc", "U2Acc", "U3Acc"), "mm/sec²"),
        **dict.fromkeys(("U1Amp", "U2Amp", "U3Amp"), "mm")}),
    "Pier Forces": ((*_STORY_CASE, "Pier", "Location"), _WALL_FORCES),
}
_OBJECT_COLUMNS = ("Story", "Element Name", "Object Type", "Object Label", "Object Name")
_JOINTS = "Objects and Elements - Joints"
_FRAMES = "Objects and Elements - Frames"
_AREAS = "Objects and Elements - Areas"
_PERIODS = "Modal Periods And Frequencies"
_MODE_COLUMNS = ("Case", "Mode")
_MODAL_DOF = ("UX", "UY", "UZ", "RX", "RY", "RZ")
_PERIOD_TABLES = (
    "Modal Participation Factors", "Modal Participating Mass Ratios", "Modal Direction Factors",
    "Response Spectrum Modal Info",
)
_REFERENCE_TABLES = _FIRST_LOT_TABLES | {
    _JOINTS: (_OBJECT_COLUMNS, dict.fromkeys(("Global X", "Global Y", "Global Z"), "mm")),
    _FRAMES: ((*_OBJECT_COLUMNS, "Elm JtI", "Elm JtJ"), {}),
    _AREAS: ((*_OBJECT_COLUMNS, "Elm Jt1", "Elm Jt2", "Elm Jt3", "Elm Jt4"), {}),
    _PERIODS: (_MODE_COLUMNS, {
        "Period": "sec", "Frequency": "cyc/sec", "CircFreq": "rad/sec", "Eigenvalue": "rad²/sec²"}),
    "Modal Participation Factors": (_MODE_COLUMNS, {
        "Period": "sec", **dict.fromkeys(_MODAL_DOF, "kN-m"), "ModalMass": "kN-m-s²", "ModalStiff": "kN-m"}),
    "Modal Participating Mass Ratios": (_MODE_COLUMNS, {
        "Period": "sec", **dict.fromkeys((*_MODAL_DOF, *("Sum" + dof for dof in _MODAL_DOF)), "")}),
    "Modal Load Participation Ratios": (("Case", "ItemType", "Item"), {"Static": "%", "Dynamic": "%"}),
    "Modal Direction Factors": (_MODE_COLUMNS, {"Period": "sec", **dict.fromkeys(("UX", "UY", "UZ", "RZ"), "")}),
}
_REFERENCE_UNITS = {
    "mm": ("m", 1000),
    "mm/sec²": ("m/s²", 1000),
    "rad/sec²": ("rad/s²", 1),
    "cyc/sec": ("Hz", 1),
    "rad/sec": ("rad/s", 1),
    "rad²/sec²": ("rad²/s²", 1),
    "sec": ("s", 1),
    "%": ("1", 100),
    "": ("1", 1),
}


def _sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()


def register_current_etabs_tables(export_dir, analysis, beam_forces, *,
                                  assignment=None):
    """[REF docs/source/components/inputs/etabs_table_bundle.py.md]
    Bind user-selected native tables to the source EDB without editing them.
    """
    from openpyxl import load_workbook
    from components.inputs.output_contract import atomic_json
    from components.inputs.project_workbooks import _source_edb_path
    root=Path(export_dir).expanduser().resolve()
    from components.inputs.output_layout import export_root_for
    if export_root_for(root)!=root:
        raise ValueError("Register ETABS native tables at the ORIGINAL export "
                         "root, not within 02_MODEL or an analysis run.")
    source=_source_edb_path(root)
    if not source or not Path(source).is_file():
        raise FileNotFoundError("Current source EDB unavailable; re-export before registration")
    edb=Path(source).expanduser().resolve()
    beam_forces = tuple(beam_forces)
    if not beam_forces:
        raise ValueError("Select at least one ETABS beam-force workbook")
    selected={
        "etabs_full_table":Path(analysis).expanduser().resolve(),
        **{f"etabs_beam_forces_element_{i}":Path(path).expanduser().resolve()
           for i,path in enumerate(beam_forces,start=1)}
    }
    if assignment is not None:
        selected["etabs_assignment"]=Path(assignment).expanduser().resolve()
    if len({str(p).casefold() for p in selected.values()})!=len(selected):
        raise ValueError("One ETABS workbook path was used for multiple distinct roles")
    if any(p.is_symlink() or any(parent.is_symlink() for parent in p.parents)
           for p in (root,edb,*selected.values())):
        raise ValueError("Refusing linked EDB or Excel paths")
    records={}
    entries={}
    for role,path in selected.items():
        if not path.is_file() or path.suffix.lower() not in (".xlsx",".xlsm"):
            raise FileNotFoundError("Missing genuine local Excel evidence for "+role+": "+str(path))
        book=load_workbook(path,read_only=True,data_only=True)
        try:
            sheets=list(book.sheetnames)
            if not sheets:
                raise ValueError("Empty workbook for role "+role)
            if role=="etabs_assignment":
                missing=sorted(set(_REQUIRED_ASSIGNMENT_SHEETS)-set(sheets))
                if missing:
                    raise ValueError("Native assignment workbook missing: "+", ".join(missing))
        finally:
            book.close()
        digest=_sha(path)
        entries[role]={"path":str(path),"sha256":digest}
        records[role]={
            "source_path":str(path),"sha256":digest,"sheets":sheets,
            "size_bytes":path.stat().st_size,
            "identity":"EXACT_BYTES_REGISTERED_NATIVE_TABLE_INTERPRETATION_PENDING",
        }
    if "etabs_assignment" not in entries and set(_REQUIRED_ASSIGNMENT_SHEETS).issubset(
            set(records["etabs_full_table"]["sheets"])):
        entries["etabs_assignment"]=dict(entries["etabs_full_table"])
        records["etabs_assignment"]=dict(records["etabs_full_table"])
    beam_hashes=[records[f"etabs_beam_forces_element_{i}"]["sha256"]
                 for i in range(1,len(beam_forces)+1)]
    if len(set(beam_hashes))!=len(beam_hashes):
        raise ValueError("Beam force parts have identical bytes; check duplicated uploads")
    destination=root/"01_ETABS_EXPORT"/"00_MANIFEST"/"PROJECT_SOURCES.private.json"
    destination.parent.mkdir(parents=True,exist_ok=True)
    edbsha=_sha(edb)
    if destination.is_file():
        prior=json.loads(destination.read_text(encoding="utf-8-sig"))
        if prior.get("source_edb_sha256")!=edbsha:
            raise ValueError("Existing ETABS workbook registry belongs to another EDB")
        old=prior.get("sources",{})
    else:
        old={}
    # The registry is a private local input inventory, not a solver result.
    # Re-registration must not retain stale beam parts from an older selection.
    old={k:v for k,v in old.items() if not k.startswith("etabs_beam_forces_element_")
         and (k != "etabs_assignment" or k in entries)}
    manifest={
        "schema":"CURRENT_ETABS_WORKBOOKS_SHA256_V1",
        "source_edb_sha256":edbsha,
        "source_edb_path":str(edb),
        "sources":{**old,**entries},
        "source_workbook_inventory":records,
        "engineering_status":"REGISTERED_SHEETS_AND_SOURCE_HASH_ONLY_NOT_STRUCTURAL_VALIDATION",
    }
    atomic_json(destination,manifest)
    return destination,manifest


def audit_analysis_workbooks(paths, *, progress=None):
    """[REF docs/source/components/inputs/etabs_table_bundle.py.md]

    Read every populated worksheet cell in all explicitly selected lots.
    Inventory only: no source data merges, solver input adoption or approval.
    Formula text is read, not evaluated; cached formula results are not checked.
    Report local sheet identity, row/cell counts and overlapping table names.
    """
    import math
    from collections import defaultdict
    from openpyxl import load_workbook
    from components.validation.etabs_native_quantity_tables import evidence_families
    selected=[Path(p).expanduser().resolve() for p in paths]
    if not selected or len({str(p).casefold() for p in selected})!=len(selected):
        raise ValueError("Select distinct analysis workbook lots")
    files=[]; errors=[]; names=defaultdict(list); contents=defaultdict(list)
    for index,path in enumerate(selected,1):
        record=dict(lot=index,source_path=str(path),worksheets=[],status="NOT_READ")
        files.append(record)
        try:
            if not path.is_file() or path.suffix.lower() not in (".xlsx",".xlsm"):
                raise ValueError("Missing or unsupported workbook")
            before=_sha(path)
            record.update(sha256=before,size_bytes=path.stat().st_size)
            book=load_workbook(path,read_only=True,data_only=False)
            try:
                record["sheet_names"]=list(book.sheetnames)
                record["worksheet_count"]=len(book.worksheets)
                record["nonworksheet_names"]=[n for n in book.sheetnames
                                             if n not in {s.title for s in book.worksheets}]
                for sheet in book.worksheets:
                    rowinfo=dict(sheet=sheet.title,state=sheet.sheet_state,
                        status="NOT_READ",nonempty_rows=0,populated_cells=0,
                        numeric_cells=0,formula_cells=0,error_cells=0,
                        nonfinite_numeric_cells=0,last_populated_row=0,
                        last_populated_column=0,
                        candidate_evidence_families=evidence_families(
                            {"key":sheet.title,"name":sheet.title}),
                        first_three_populated_rows=[])
                    record["worksheets"].append(rowinfo)
                    if progress:progress(f"Lot {index}: reading {sheet.title}")
                    try:
                        # Exported dimensions can be wrong. Stream actual row
                        # XML rather than trusting the advertised used range.
                        sheet.reset_dimensions()
                        digest=hashlib.sha256()
                        for rn,row in enumerate(sheet.iter_rows(),1):
                            cells=[]
                            for cn,cell in enumerate(row,1):
                                val=cell.value
                                if val is None:continue
                                typ=cell.data_type
                                rowinfo["populated_cells"]+=1
                                rowinfo["last_populated_column"]=max(
                                    rowinfo["last_populated_column"],cn)
                                if typ=="f":rowinfo["formula_cells"]+=1
                                elif typ=="e":rowinfo["error_cells"]+=1
                                elif isinstance(val,(int,float)) and not isinstance(val,bool):
                                    rowinfo["numeric_cells"]+=1
                                    if isinstance(val,float) and not math.isfinite(val):
                                        rowinfo["nonfinite_numeric_cells"]+=1
                                        val=str(val)
                                # Include actual typed cell content, coordinates
                                # and formula text. Non-primitive values (dates,
                                # array formulas) retain a stable representation.
                                if not isinstance(val,(str,int,float,bool)):
                                    if hasattr(val,"isoformat"):val=val.isoformat()
                                    elif hasattr(val,"__dict__"):val=vars(val)
                                    else:raise ValueError("Unsupported cell value type: "+type(val).__name__)
                                cells.append((cn,typ,val))
                            if cells:
                                rowinfo["nonempty_rows"]+=1
                                rowinfo["last_populated_row"]=rn
                                line=json.dumps([rn,cells],ensure_ascii=False,
                                                sort_keys=True,default=str)
                                digest.update(line.encode("utf-8")+b"\\n")
                                if len(rowinfo["first_three_populated_rows"])<3:
                                    rowinfo["first_three_populated_rows"].append(
                                        dict(row=rn,cells=cells[:40]))
                        rowinfo.update(status="ALL_POPULATED_CELLS_SCANNED",
                                       content_sha256=digest.hexdigest())
                        identity=dict(lot=index,sheet=sheet.title)
                        names[sheet.title.strip().casefold()].append(identity)
                        contents[digest.hexdigest()].append(identity)
                    except Exception as exc:
                        rowinfo.update(status="SHEET_SCAN_FAILED",error=type(exc).__name__+": "+str(exc))
                        errors.append(dict(lot=index,sheet=sheet.title,error=rowinfo["error"]))
            finally:
                book.close()
            if _sha(path)!=before:
                raise ValueError("Workbook bytes changed during scan")
            record["status"]=("ALL_WORKSHEETS_SCANNED" if record["worksheets"] and
                all(s["status"]=="ALL_POPULATED_CELLS_SCANNED" for s in record["worksheets"])
                else "INCOMPLETE_WORKSHEET_SCAN")
        except Exception as exc:
            record.update(status="WORKBOOK_SCAN_FAILED",error=type(exc).__name__+": "+str(exc))
            errors.append(dict(lot=index,error=record["error"]))
    sheets=[s for f in files for s in f["worksheets"]]
    families=defaultdict(list)
    for f in files:
        for s in f["worksheets"]:
            if s["status"]=="ALL_POPULATED_CELLS_SCANNED":
                for family in s["candidate_evidence_families"]:
                    families[family].append(dict(lot=f["lot"],sheet=s["sheet"],
                                                 nonempty_rows=s["nonempty_rows"]))
    complete=all(f["status"]=="ALL_WORKSHEETS_SCANNED" for f in files)
    return dict(schema="ETABS_MULTI_LOT_ALL_SHEET_AUDIT_V1",
        status="ALL_WORKSHEETS_SCANNED_NOT_ENGINEERING_VALIDATION" if complete else "INCOMPLETE_SCAN",
        engineering_acceptance="NOT_VERIFIED",source_model_identity="NOT_ESTABLISHED_BY_SCAN",
        files=files,worksheet_count=len(sheets),
        fully_scanned_worksheets=sum(s["status"]=="ALL_POPULATED_CELLS_SCANNED" for s in sheets),
        nonempty_rows=sum(s["nonempty_rows"] for s in sheets),
        populated_cells=sum(s["populated_cells"] for s in sheets),
        repeated_sheet_names=[v for v in names.values() if len(v)>1],
        identical_populated_cell_content=[v for v in contents.values() if len(v)>1],
        candidate_evidence_families=dict(families),errors=errors,
        limitations=["Private local diagnostic; no table rows are combined or deduplicated.",
                     "Names are discovery hints, not validated result schemas or units.",
                     "Row counts include header and unit rows; formula caches not evaluated.",
                     "Repeated names or identical populated cells require source review before combining.",
                     "Not proof of same EDB, complete analysis cases, native analytical mesh or engineering equivalence."])


def _reference_header(sheet):
    sheet.reset_dimensions()
    rows = iter(sheet.values)
    title = next(rows, ())
    table_name = ("Story Max Over Avg Displacements"
                  if sheet.title == "Story Max Over Avg Disp" else sheet.title)
    if not title or not isinstance(title[0], str) or title[0].split(":", 1)[0] != "TABLE" \
            or title[0].partition(":")[2].strip() != table_name or any(title[1:]):
        raise ValueError(f"{sheet.title}: expected ETABS table title in row 1")
    headers = next(rows, ())
    if not headers or any(not isinstance(h, str) or not h.strip() for h in headers) \
            or len(set(headers)) != len(headers):
        raise ValueError(f"{sheet.title}: missing or repeated column headers in row 2")
    units = next(rows, ())
    return table_name, headers, units, rows


def _program_control(sheet):
    _, headers, _, rows = _reference_header(sheet)
    records = (row for row in rows if any(value is not None for value in row))
    row = next(records, ())
    record = dict(zip(headers, row))
    fields = ("ProgramName", "Version", "CurrUnits")
    if (next(records, None) is not None or any(value is not None for value in row[len(headers):])
            or not all(isinstance(record.get(field), str) and record[field].strip()
                       and not record[field].startswith(("=", "#")) for field in fields)
            or record["ProgramName"] != "ETABS"):
        raise ValueError("Program Control: expected one ETABS record with version and displayed units")
    return {field: record[field] for field in fields}


def _reference_table(sheet):
    name, headers, unit_row, rows = _reference_header(sheet)
    keys, measures = _REFERENCE_TABLES[sheet.title]
    if set(headers) != set(keys) | measures.keys():
        raise ValueError(f"{sheet.title}: column headers do not match the ETABS reference schema")
    source_units = dict(zip(headers, unit_row))
    for column in headers:
        expected = measures.get(column, "")
        observed = source_units.get(column)
        if ("" if observed is None else observed) != expected:
            raise ValueError(f"{sheet.title}: unexpected unit for {column}; expected {expected or 'blank'}")
    if any(unit_row[len(headers):]):
        raise ValueError(f"{sheet.title}: unexpected unit outside the table")
    normalized_units = {column: _REFERENCE_UNITS.get(unit, (unit, 1)) for column, unit in measures.items()}
    case_column = next((c for c in ("Output Case", "SpecCase", "Case") if c in keys), None)
    # The drift table identifies one result per story, direction, case and step.
    # Its controlling point label and formatted reciprocal drift are attributes.
    identity_columns = {
        "Story Drifts": tuple(column for column in keys if column not in ("Drift/", "Label")),
        _JOINTS: ("Element Name",),
        _FRAMES: headers,
        _AREAS: ("Object Type", "Element Name"),
    }.get(sheet.title, keys)
    key_seen = {}
    duplicates = {}
    source_row_count = 0
    story_names = set()
    case_counts = Counter()
    imported = []
    for row_number, row in enumerate(rows, start=4):
        if all(value is None for value in row):
            continue
        source_row_count += 1
        context = f"{sheet.title} row {row_number}"
        if len(row) > len(headers) and any(value is not None for value in row[len(headers):]):
            raise ValueError(f"{context}: data outside the table columns")
        record = dict.fromkeys(headers)
        record.update(zip(headers, row))
        for column, (_, divisor) in normalized_units.items():
            value = record[column]
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f"{context}: {column} requires a finite numeric value")
            if divisor != 1:
                record[column] = value / divisor
        for column in keys:
            value = record[column]
            if column == "Mode":
                if isinstance(value, str) and value.isascii() and value.isdecimal():
                    value = int(value)
                if type(value) is not int or value < 1:
                    raise ValueError(f"{context}: invalid mode number")
                record[column] = value
            elif column == "Step Number":
                if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
                    raise ValueError(f"{context}: invalid step number")
            elif (column, value) != ("Step Type", None) and (
                    not isinstance(value, str) or not value.strip() or value.startswith(("=", "#"))):
                raise ValueError(f"{context}: invalid {column}")
        key = tuple(record[column] for column in identity_columns)
        if key in key_seen:
            # Shell edges can share an element name and have distinct ordered
            # connectivity. Group only identical records from the frame sheet.
            if sheet.title == _FRAMES:
                duplicates.setdefault(key_seen[key], []).append(row_number)
                continue
            raise ValueError(f"{context}: duplicate result key")
        key_seen[key] = row_number
        if "Story" in record:
            story_names.add(record["Story"])
        case = record[case_column] if case_column else None
        if case is not None:
            case_counts[case] += 1
        imported.append([row_number, *(record[column] for column in headers)])
    result = {
        "table_title": name, "columns": ["worksheet_row", *headers],
        "source_units": measures, "units": {c: scale[0] for c, scale in normalized_units.items()},
        "case_column": case_column, "case_row_counts": dict(case_counts),
        "stories": sorted(story_names), "source_row_count": source_row_count,
        "unique_row_count": len(imported), "rows": imported,
    }
    if sheet.title == _FRAMES:
        result["duplicate_worksheet_rows"] = [
            {"worksheet_row": original, "also_at": duplicates[original]} for original in sorted(duplicates)]
    return result


def _read_reference_workbook(book, entry, schemas, progress):
    sheet_names = set(entry["worksheets"])
    program = {}
    if "Program Control" in sheet_names:
        program = _program_control(book["Program Control"])
    elif not (sheet_names & (schemas.keys() - _FIRST_LOT_TABLES.keys())):
        raise ValueError("ETABS Program Control worksheet is required")
    tables = {}
    for sheet in book.worksheets:
        if sheet.title in schemas:
            if progress:
                progress(f"Reading {sheet.title}")
            tables[sheet.title] = _reference_table(sheet)
    if not any(table["rows"] for table in tables.values()):
        raise ValueError(f"The workbook has no supported reference rows: {Path(entry['path']).name}")
    return {
        "edb_sha256": None, "source_model_identity": "UNVERIFIED", "etabs_version": program.get("Version"),
        "reported_current_units": program.get("CurrUnits"),
        "unrecognized_sheets": sorted(sheet_names - schemas.keys() - {"Program Control"}),
    }, tables


def _reference_checks(tables):
    modal = {}
    if _PERIODS in tables:
        baseline = tables[_PERIODS]
        case, mode, period = (baseline["columns"].index(c) for c in ("Case", "Mode", "Period"))
        periods = {(row[case], row[mode]): row[period] for row in baseline["rows"]}
        for name in _PERIOD_TABLES:
            if name not in tables:
                continue
            table = tables[name]
            case_name = "ModalCase" if name == "Response Spectrum Modal Info" else "Case"
            case, mode, period = (table["columns"].index(c) for c in (case_name, "Mode", "Period"))
            matched = 0
            for row in table["rows"]:
                key = (row[case], row[mode])
                if key in periods:
                    if row[period] != periods[key]:
                        raise ValueError(f"{name} row {row[0]}: conflicting modal period for {key}")
                    matched += 1
            modal[name] = {"matched_rows": matched, "unmatched_rows": len(table["rows"]) - matched}

    connectivity = {}
    if _JOINTS in tables:
        joints = tables[_JOINTS]
        index = joints["columns"].index("Element Name")
        joint_ids = {row[index] for row in joints["rows"]}
        for name in (_FRAMES, _AREAS):
            if name not in tables:
                continue
            table = tables[name]
            endpoints = [i for i, c in enumerate(table["columns"]) if c.startswith("Elm Jt")]
            missing = {row[i] for row in table["rows"] for i in endpoints} - joint_ids
            connectivity[name] = {"checked_rows": len(table["rows"]), "unresolved_joint_ids": sorted(missing)}
    return {"modal_periods": modal, "connectivity": connectivity}


def _read_analysis_reference(paths, cases, progress, schemas, legacy_first_lot):
    from components.inputs.etabs_excel_selection import build_analysis_table_catalog

    paths = tuple(paths)
    requested = tuple(cases)
    if any(not isinstance(c, str) or not c.strip() for c in requested) or len(set(requested)) != len(requested):
        raise ValueError("Specify distinct, nonblank exact ETABS case names")
    selected = set(requested)
    metadata = []
    tables = {}

    def inspect(book, entry, file_index):
        if progress and len(paths) > 1:
            progress(f"Workbook {file_index + 1}: {Path(entry['path']).name}")
        source, imported = _read_reference_workbook(book, entry, schemas, progress)
        metadata.append(source)
        for name, table in imported.items():
            table["file_index"] = file_index
            tables.setdefault(name, table)

    catalog = build_analysis_table_catalog(paths, inspect_workbook=inspect)
    owners = catalog["tables"]
    shared = [name for name in schemas
              if len({owner["file_index"] for owner in owners.get(name.casefold(), ())}) > 1]
    if shared:
        raise ValueError("Reference table occurs in more than one workbook: " + ", ".join(sorted(shared)))
    files = [{**entry, **source} for entry, source in zip(catalog["files"], metadata)]
    checks = _reference_checks(tables)
    missing_cases = selected - {name for table in tables.values() for name in table["case_row_counts"]}
    if missing_cases:
        raise ValueError("Requested ETABS case absent: " + ", ".join(sorted(missing_cases)))
    if selected:
        for table in tables.values():
            if table["case_column"]:
                i = table["columns"].index(table["case_column"])
                table["rows"] = [row for row in table["rows"] if row[i] in selected]
    common = {
        "status": "WORKBOOK_REFERENCE_ONLY", "engineering_acceptance": "NOT_VERIFIED",
        "selected_cases": list(requested), "tables": tables,
    }
    if legacy_first_lot and len(files) == 1 and tables.keys() <= _FIRST_LOT_TABLES.keys():
        source = metadata[0]
        unknown = source.pop("unrecognized_sheets")
        source["workbook_path"] = files[0]["path"]
        source["workbook_sha256"] = files[0]["sha256"]
        for table in tables.values():
            table.pop("file_index")
            table.pop("unique_row_count")
        return {
            **common, "schema": "ETABS_FIRST_LOT_REFERENCE_V1", "source": source,
            "missing_tables": sorted(_FIRST_LOT_TABLES.keys() - tables.keys()), "unrecognized_sheets": unknown,
        }
    return {
        **common, "schema": "ETABS_ANALYSIS_REFERENCE_V1", "files": files,
        "missing_tables": sorted(schemas.keys() - tables.keys()), "checks": checks,
    }


def read_analysis_reference(paths, *, cases=(), progress=None, legacy_first_lot=False):
    """[REF docs/source/components/inputs/etabs_table_bundle.py.md]

    Read first- and second-lot tables as ETABS reference evidence.
    Cross-check reported modal periods and endpoint IDs before filtering exact cases.
    """
    return _read_analysis_reference(paths, cases, progress, _REFERENCE_TABLES, legacy_first_lot)


def read_first_lot_reference(path, *, cases=(), progress=None):
    """[REF docs/source/components/inputs/etabs_table_bundle.py.md]

    Read one first-lot workbook with the original single-workbook schema.
    """
    source = Path(path).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in (".xlsx", ".xlsm"):
        raise ValueError("Select one local ETABS .xlsx or .xlsm analysis workbook")
    return _read_analysis_reference([source], cases, progress, _FIRST_LOT_TABLES, True)
