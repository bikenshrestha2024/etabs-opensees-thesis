"""[REF docs/source/components/inputs/etabs_table_bundle.py.md]
Source-EDB-bound ETABS workbook registration. No file moves or uploads.

This records workbook identities and verified sheet inventories. It is not a
numerical ETABS/OpenSees equivalence comparison.
"""
from __future__ import annotations
import hashlib
import json
import math
import sqlite3
from collections import Counter
from contextlib import closing
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
_JOINT_RESPONSE_KEYS = ("Story", "Label", "Unique Name", *_CASE_COLUMNS)
_GLOBAL_REACTIONS = dict.fromkeys(("FX", "FY", "FZ"), "kN") | dict.fromkeys(("MX", "MY", "MZ"), "kN-m")
_DISPLACEMENTS = dict.fromkeys(("Ux", "Uy", "Uz"), "mm") | dict.fromkeys(("Rx", "Ry", "Rz"), "rad")
_VELOCITIES = dict.fromkeys(("UX", "UY", "UZ"), "mm/sec") | dict.fromkeys(("RX", "RY", "RZ"), "rad/sec")
_ACCELERATIONS = {"UX": "mm/sec²", "UY": "mm/sec²", "UZ": "mm/sec²",
                  "RX": "rad/sec²", "RY": "rad/sec²", "RZ": "rad/sec²"}
_LARGE_TABLES = {
    "Joint Velocities - Relative": (_JOINT_RESPONSE_KEYS, _VELOCITIES),
    "Joint Velocities - Absolute": (_JOINT_RESPONSE_KEYS, _VELOCITIES),
    "Joint Reactions": (_JOINT_RESPONSE_KEYS, _GLOBAL_REACTIONS),
    "Joint Drifts": (_JOINT_RESPONSE_KEYS, {"Disp X": "mm", "Disp Y": "mm", "Drift  X": "", "Drift Y": ""}),
    "Joint Displ Incl Int Mesh Jts": (_JOINT_RESPONSE_KEYS, _DISPLACEMENTS),
    "Joint Displacements - Absolute": (_JOINT_RESPONSE_KEYS, _DISPLACEMENTS),
    "Joint Displacements": (_JOINT_RESPONSE_KEYS, _DISPLACEMENTS),
    "Joint Design Reactions": (_JOINT_RESPONSE_KEYS, _GLOBAL_REACTIONS),
    "Joint Accelerations - Relative": (_JOINT_RESPONSE_KEYS, _ACCELERATIONS),
    "Joint Accelerations - Absolute": (_JOINT_RESPONSE_KEYS, _ACCELERATIONS),
}
_ELEMENT_JOINT_FORCES = dict.fromkeys(("F1", "F2", "F3"), "kN") | dict.fromkeys(("M1", "M2", "M3"), "kN-m")
_SHELL_RESPONSE_KEYS = ("Story", "Shell Object", "Unique Name", "Design Type", "Shell Element", "Joint",
                        *_CASE_COLUMNS)
_STRESSES = ("S11", "S22", "S12", "SMax", "SMin", "SVM")
_STRAINS = ("E11", "E22", "G12", "EMax", "EMin", "EVM")
_LARGE_TABLES.update({
    "Integrated Wall Reactions": (
        ("Story", "WallBay", "UniqueName", *_CASE_COLUMNS),
        _GLOBAL_REACTIONS | dict.fromkeys(("Global X", "Global Y", "Global Z"), "m")),
    "Element Stresses - Area Shells": (_SHELL_RESPONSE_KEYS, dict.fromkeys((
        *(f"{component} {face}" for face in ("Top", "Bottom") for component in _STRESSES),
        "S13 Average", "S23 Average", "SMaxV Average"), "MPa")),
    "Element Strains - Area Shells": (_SHELL_RESPONSE_KEYS, dict.fromkeys((
        *(f"{component} {face}" for face in ("Top", "Bottom") for component in _STRAINS),
        "G13 Average", "G23 Average", "GMaxV Average"), "mm/mm")),
    "Element NL Energy By Group": (("Group", *_CASE_COLUMNS), dict.fromkeys((
        "Internal Viscous Damping", "Internal Hysteretic Damping",
        "Support Viscous Damping", "Support Hysteretic Damping"), "kN-m")),
    "Element Joint Forces - Shells": (
        ("Story", "Shell Object", "Unique Name", "Shell Element", "Joint", *_CASE_COLUMNS), _ELEMENT_JOINT_FORCES),
    "Element Joint Forces - Frame": (
        ("Story", "Frame", "Unique Name", "Frame Element", "Joint", *_CASE_COLUMNS), _ELEMENT_JOINT_FORCES),
    **{
        f"Element Forces - {family}s": (
            ("Story", family, "Unique Name", *_CASE_COLUMNS, "Element", "Location"),
            _WALL_FORCES | {"Station": "m", "Elem Station": "m"})
        for family in ("Column", "Brace")
    },
})
_LARGE_TABLES.update({
    "Element Forces - Area Shells": (_SHELL_RESPONSE_KEYS,
        dict.fromkeys(("F11", "F22", "F12", "FMax", "FMin", "FVM", "V13", "V23", "VMax"), "kN/m")
        | dict.fromkeys(("M11", "M22", "M12", "MMax", "MMin"), "kN-m/m")),
    "Diaphragm Max Over Avg Drifts": ((*_STORY_CASE, "Item", "Label"),
        dict.fromkeys(("Max Drift", "Avg Drift", "Ratio"), "")
        | dict.fromkeys(("Max Loc X", "Max Loc Y", "Max Loc Z"), "m")),
    "Diaphragm Forces": (_JOINT_RESPONSE_KEYS,
        dict.fromkeys(("X-Coor", "Y-Coor", "Z-Coor"), "mm")
        | dict.fromkeys(("Applied Load FX", "Applied Load FY", "Reactive Force FX",
                         "Reactive Force FY", "Diaphragm Force FX", "Diaphragm Force FY"), "kN")),
    "Diaphragm CM Displacements": (("Story", "Diaphragm", *_CASE_COLUMNS, "Point"),
        {"UX": "mm", "UY": "mm", "RZ": "rad", **dict.fromkeys(("X", "Y", "Z"), "m"),
         "Diaphragm Mass X": "kg", "Diaphragm Mass Y": "kg", "Diaphragm MMI RZ": "ton-m²"}),
    "Diaphragm Accelerations": (("Story", "Diaphragm", *_CASE_COLUMNS),
        {f"{side} {axis}": unit for side in ("Max", "Min")
         for axis, unit in _ACCELERATIONS.items()}),
    "Centers Of Mass And Rigidity": (("Story", "Diaphragm"),
        dict.fromkeys(("Mass X", "Mass Y", "Cum Mass X", "Cum Mass Y"), "kg")
        | dict.fromkeys(("XCM", "YCM", "XCCM", "YCCM", "XCR", "YCR"), "m")),
})
_REFERENCE_TABLES.update(_LARGE_TABLES)
_REFERENCE_TITLES = {
    "Story Max Over Avg Disp": "Story Max Over Avg Displacements",
    "Joint Displ Incl Int Mesh Jts": "Joint Displacements (Including Internal Mesh Joints)",
    "Element NL Energy By Group": "Element Nonlinear Energy By Group",
    "Diaphragm CM Displacements": "Diaphragm Center Of Mass Displacements",
}
_REFERENCE_UNITS = {
    "mm": ("m", 1000),
    "mm/sec²": ("m/s²", 1000),
    "mm/sec": ("m/s", 1000),
    "rad/sec²": ("rad/s²", 1),
    "cyc/sec": ("Hz", 1),
    "rad/sec": ("rad/s", 1),
    "rad²/sec²": ("rad²/s²", 1),
    "sec": ("s", 1),
    "%": ("1", 100),
    "mm/mm": ("1", 1),
    "MPa": ("kN/m²", 0.001),
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


class _ReferenceRows:
    """Disk-backed rows, worksheet positions and duplicate aliases."""

    def __init__(self, connection):
        self.db = connection
        self.db.executescript("""
            PRAGMA foreign_keys = ON;
            PRAGMA cache_size = -65536;
            CREATE TABLE reference_tables (
                table_id INTEGER PRIMARY KEY, worksheet TEXT NOT NULL UNIQUE
            );
            CREATE TABLE reference_rows (
                table_id INTEGER NOT NULL REFERENCES reference_tables,
                worksheet_row INTEGER NOT NULL, case_name TEXT, values_json TEXT NOT NULL,
                record_key BLOB NOT NULL, PRIMARY KEY (table_id, worksheet_row),
                UNIQUE (table_id, record_key)
            ) WITHOUT ROWID;
            CREATE TABLE source_row_aliases (
                table_id INTEGER NOT NULL, worksheet_row INTEGER NOT NULL, retained_row INTEGER NOT NULL,
                PRIMARY KEY (table_id, worksheet_row),
                FOREIGN KEY (table_id, retained_row)
                    REFERENCES reference_rows(table_id, worksheet_row) ON DELETE CASCADE
            ) WITHOUT ROWID;
            CREATE INDEX aliases_retained_row ON source_row_aliases(table_id, retained_row);
        """)

    def start(self, title):
        try:
            return self.db.execute("INSERT INTO reference_tables(worksheet) VALUES (?)", (title,)).lastrowid
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"Reference table occurs in more than one workbook: {title}") from exc

    def add(self, table_id, row_number, case, values, key, repeatable):
        payload = json.dumps(values, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        key_text = json.dumps(key, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        digest = hashlib.sha256(key_text.encode("utf-8")).digest()
        written = self.db.execute("""
            INSERT INTO reference_rows VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(table_id, record_key) DO NOTHING
        """, (table_id, row_number, case, payload, digest))
        if written.rowcount:
            return True
        retained_row, original = self.db.execute("""
            SELECT worksheet_row, values_json FROM reference_rows WHERE table_id=? AND record_key=?
        """, (table_id, digest)).fetchone()
        if not repeatable or original != payload:
            title = self.db.execute("SELECT worksheet FROM reference_tables WHERE table_id=?",
                                    (table_id,)).fetchone()[0]
            raise ValueError(f"{title} row {row_number}: duplicate result key")
        self.db.execute("INSERT INTO source_row_aliases VALUES (?, ?, ?)", (table_id, row_number, retained_row))
        return False

    def rows(self, title):
        rows = self.db.execute("""
            SELECT worksheet_row, values_json FROM reference_rows JOIN reference_tables USING (table_id)
            WHERE worksheet=? ORDER BY worksheet_row
        """, (title,))
        return ([row_number, *json.loads(values)] for row_number, values in rows)

    def keep_cases(self, cases):
        if cases:
            self.db.execute("CREATE TEMP TABLE selected_cases(case_name TEXT PRIMARY KEY)")
            self.db.executemany("INSERT INTO selected_cases VALUES (?)", ((case,) for case in cases))
            self.db.execute("""
                DELETE FROM reference_rows WHERE case_name IS NOT NULL
                AND case_name NOT IN (SELECT case_name FROM selected_cases)
            """)
        self.db.execute("CREATE INDEX reference_case ON reference_rows(table_id, case_name)")


def _reference_header(sheet):
    sheet.reset_dimensions()
    rows = iter(sheet.values)
    title = next(rows, ())
    table_name = _REFERENCE_TITLES.get(sheet.title, sheet.title)
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


def _reference_row_flags(sheet_name, record):
    """Source-display diagnostics only; never alter a reported result."""
    flags = []
    average = {"Diaphragm Max Over Avg Drifts": "Avg Drift",
               "Story Max Over Avg Drifts": "Avg Drift",
               "Story Max Over Avg Disp": "Average"}.get(sheet_name)
    if average is not None and record[average] == 0:
        flags.append("ZERO_REPORTED_AVERAGE_RATIO_UNRESOLVED")
    if sheet_name == "Story Drifts" and record["Drift/"] == "1/0":
        flags.append("RECIPROCAL_DISPLAY_ONE_OVER_ZERO")
        if record["Drift"] != 0:
            flags.append("RECIPROCAL_DISPLAY_ONE_OVER_ZERO_NONZERO_DRIFT")
    return flags


def _field_availability_columns(sheet_name):
    if sheet_name == "Element Stresses - Area Shells":
        prefix, direct = "S", ("S11", "S22", "S12")
    elif sheet_name == "Element Strains - Area Shells":
        prefix, direct = "E", ("E11", "E22", "G12")
    elif sheet_name == "Element NL Energy By Group":
        return ("Internal Viscous Damping", "Internal Hysteretic Damping",
                "Support Viscous Damping", "Support Hysteretic Damping")
    else:
        return ()
    return tuple(f"{c} {face}" for face in ("Top", "Bottom")
                 for c in (*direct, prefix+"Max", prefix+"Min", prefix+"VM"))


def _field_availability_add(counts, fields, record):
    key = (record.get("Group"), record["Output Case"], record["Case Type"], record["Step Type"])
    group = counts.get(key)
    if group is None:
        group = counts[key] = [[0, 0, 0] for _ in fields]
    for column, count in zip(fields, group):
        value = record[column]
        count[0 if value is None else 1 if value == 0 else 2] += 1


def _field_availability_report(fields, counts):
    groups = []
    for (group, case, case_type, step_type), values in counts.items():
        flags = []
        if len(fields) == 4:
            if all(zero and not missing and not nonzero for missing, zero, nonzero in values):
                flags.append("ALL_REPORTED_ENERGY_ZERO_UNRESOLVED")
        else:
            for offset, face in ((0, "TOP"), (6, "BOTTOM")):
                direct, derived = values[offset:offset+3], values[offset+3:offset+6]
                if any(v[2] for v in direct) and all(v[1] and not v[0] and not v[2] for v in derived):
                    flags.append(f"{face}_ALL_REPORTED_DERIVED_ZERO_WITH_NONZERO_DIRECTIONAL_UNRESOLVED")
        groups.append({"group": group, "case": case, "case_type": case_type, "step_type": step_type,
                       "field_counts": {field: dict(zip(("missing", "zero", "nonzero"), value))
                                        for field, value in zip(fields, values)}, "flags": flags})
    return {"scope": "ALL_UNIQUE_SOURCE_ROWS_BEFORE_CASE_FILTER",
            "status": "REFERENCE_ONLY_OUTPUT_AVAILABILITY_UNRESOLVED", "groups": groups}


def _reference_table(sheet, store=None):
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
    large_table = sheet.title in _LARGE_TABLES
    repeatable = large_table or sheet.title == _FRAMES
    table_id = store.start(sheet.title) if store else None
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
    blank_measures = Counter()
    display_flags = {}
    imported = []
    unique_row_count = 0
    availability_fields = _field_availability_columns(sheet.title)
    availability_counts = {}
    for row_number, row in enumerate(rows, start=4):
        if all(value is None for value in row):
            continue
        source_row_count += 1
        context = f"{sheet.title} row {row_number}"
        if len(row) > len(headers) and any(value is not None for value in row[len(headers):]):
            raise ValueError(f"{context}: data outside the table columns")
        record = dict.fromkeys(headers)
        record.update(zip(headers, row))
        source_key = tuple(record.values()) if repeatable and store else None
        for column, (_, divisor) in normalized_units.items():
            value = record[column]
            if value is None and large_table:
                blank_measures[column] += 1
                continue
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
            elif not (value is None and (column == "Step Type" or (large_table and column in ("Label", "Location")))) and (
                    not isinstance(value, str) or not value.strip() or value.startswith(("=", "#"))):
                raise ValueError(f"{context}: invalid {column}")
        case = record[case_column] if case_column else None
        values = [record[column] for column in headers]
        key = source_key if source_key is not None else tuple(record[column] for column in identity_columns)
        if store:
            if not store.add(table_id, row_number, case, values, key, repeatable):
                continue
        elif key in key_seen:
            # Shell edges can share an element name and have distinct ordered
            # connectivity. Group only identical records from the frame sheet.
            if sheet.title == _FRAMES:
                duplicates.setdefault(key_seen[key], []).append(row_number)
                continue
            raise ValueError(f"{context}: duplicate result key")
        if not store:
            key_seen[key] = row_number
            imported.append([row_number, *values])
        unique_row_count += 1
        if availability_fields:
            _field_availability_add(availability_counts, availability_fields, record)
        for flag in _reference_row_flags(sheet.title, record):
            display_flags.setdefault(flag, []).append(row_number)
        if "Story" in record:
            story_names.add(record["Story"])
        if case is not None:
            case_counts[case] += 1
    result = {
        "table_title": name, "columns": ["worksheet_row", *headers],
        "source_units": measures, "units": {c: scale[0] for c, scale in normalized_units.items()},
        "case_column": case_column, "case_row_counts": dict(case_counts),
        "stories": sorted(story_names), "source_row_count": source_row_count,
        "unique_row_count": unique_row_count,
    }
    if availability_fields:
        result["source_field_availability"] = _field_availability_report(availability_fields, availability_counts)
    if sheet.title in ("Story Max Over Avg Drifts", "Story Max Over Avg Disp", "Story Drifts",
                       "Diaphragm Max Over Avg Drifts"):
        result["source_display_diagnostics"] = {
            "scope": "ALL_UNIQUE_SOURCE_ROWS_BEFORE_CASE_FILTER",
            "status": "REFERENCE_ONLY_NOT_NBC_TORSION_EVALUATION",
            "flag_counts": {flag: len(positions) for flag, positions in display_flags.items()},
            "worksheet_rows": display_flags,
        }
    if store:
        result["table_id"] = table_id
        result["duplicate_row_count"] = source_row_count - unique_row_count
        result["blank_measure_counts"] = dict(blank_measures)
    else:
        result["rows"] = imported
    if sheet.title == _FRAMES and not store:
        result["duplicate_worksheet_rows"] = [
            {"worksheet_row": original, "also_at": duplicates[original]} for original in sorted(duplicates)]
    return result


def _read_reference_workbook(book, entry, schemas, progress, store):
    sheet_names = set(entry["worksheets"])
    if not store and sheet_names & schemas.keys() & _LARGE_TABLES.keys():
        raise ValueError("Third- and fourth-lot tables require --reference-storage sqlite")
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
            tables[sheet.title] = _reference_table(sheet, store)
    if not any(table["unique_row_count"] for table in tables.values()):
        raise ValueError(f"The workbook has no supported reference rows: {Path(entry['path']).name}")
    return {
        "edb_sha256": None, "source_model_identity": "UNVERIFIED", "etabs_version": program.get("Version"),
        "reported_current_units": program.get("CurrUnits"),
        "unrecognized_sheets": sorted(sheet_names - schemas.keys() - {"Program Control"}),
    }, tables


def _modal_mass_reference_diagnostics(records):
    """Report source modal mass, not a native mass or code acceptance check."""
    grouped = {}
    for record in records:
        grouped.setdefault(record["Case"], []).append(record)
    result = {}
    for case, source in grouped.items():
        ordered = sorted(source, key=lambda record: record["Mode"])
        modes = [record["Mode"] for record in ordered]
        axes = {}
        for axis in ("UX", "UY", "UZ", "RX", "RY", "RZ"):
            cumulative = 0.0
            previous = 0.0
            residual = 0.0
            decreases = []
            invalid = []
            first_90 = None
            for record in ordered:
                value = record[axis]
                reported = record["Sum" + axis]
                cumulative += value
                residual = max(residual, abs(cumulative - reported))
                if reported < previous:
                    decreases.append(record["worksheet_row"])
                if not (0 <= value <= 1 and 0 <= reported <= 1):
                    invalid.append(record["worksheet_row"])
                if first_90 is None and reported >= 0.9:
                    first_90 = {"mode": record["Mode"], "period_s": record["Period"],
                                "worksheet_row": record["worksheet_row"]}
                previous = reported
            axes[axis] = {"reported_final_fraction": previous,
                          "sum_of_displayed_fractions": cumulative,
                          "max_cumulative_absolute_residual": residual,
                          "decreasing_cumulative_rows": decreases,
                          "out_of_range_rows": invalid,
                          "first_reported_90_percent": first_90}
        result[case] = {"modes": modes, "contiguous_from_one": modes == list(range(1, len(modes) + 1)),
                        "axes": axes}
    return {"status": "REFERENCE_ONLY_NOT_NATIVE_MASS_OR_CODE_ACCEPTANCE", "cases": result}


def _story_drift_joint_reference_diagnostics(joints, drifts):
    """Match source story and object label, then coordinates in metres."""
    from collections import defaultdict
    index = defaultdict(list)
    for joint in joints:
        index[(joint["Story"], joint["Object Label"])].append(
            tuple(joint["Global " + axis] for axis in "XYZ"))
    counts = Counter()
    exceptions = {}
    tolerance_m = 0.001
    for drift in drifts:
        candidates = index.get((drift["Story"], drift["Label"]), ())
        matches = sum(all(abs(drift[axis] - value) <= tolerance_m
                          for axis, value in zip("XYZ", point)) for point in candidates)
        if not candidates:
            status = "NO_STORY_LABEL_MATCH"
        elif matches == 0:
            status = "COORDINATE_MISMATCH"
        elif matches > 1:
            status = "AMBIGUOUS_COORDINATE_MATCH"
        else:
            status = "UNIQUE_COORDINATE_MATCH"
        counts[status] += 1
        if status != "UNIQUE_COORDINATE_MATCH":
            exceptions.setdefault(status, []).append(drift["worksheet_row"])
    return {"status": "REFERENCE_ONLY_NOT_NATIVE_TOPOLOGY_ACCEPTANCE",
            "coordinate_tolerance_m": tolerance_m, "counts": dict(counts),
            "exception_worksheet_rows": exceptions}


def _joint_response_identity_diagnostics(joints, responses):
    """Check unique source joint ID, story and object label; not restraint identity."""
    index = {r["Element Name"]: (r["Story"], r["Object Label"]) for r in joints}
    result = {}
    for name, records in responses.items():
        counts = Counter()
        exceptions = {}
        unresolved = set()
        for record in records:
            joint = record["Unique Name"]
            expected = index.get(joint)
            if expected is None:
                status = "UNKNOWN_JOINT_ID"
                unresolved.add(joint)
            elif record["Story"] != expected[0]:
                status = "STORY_MISMATCH"
            elif record["Label"] is None:
                status = "MISSING_RESPONSE_LABEL"
            elif record["Label"] != expected[1]:
                status = "LABEL_MISMATCH"
            else:
                status = "MATCHED"
            counts[status] += 1
            if status != "MATCHED":
                sample = exceptions.setdefault(status, [])
                if len(sample) < 100:
                    sample.append(record["worksheet_row"])
        result[name] = {"counts": dict(counts),
                        "unresolved_joint_ids": sorted(unresolved),
                        "exception_worksheet_row_samples": exceptions,
                        "exception_sample_limit_per_status": 100}
    return {"status": "REFERENCE_ONLY_NOT_NATIVE_CONSTRAINT_ACCEPTANCE",
            "scope": "ALL_UNIQUE_SOURCE_ROWS_BEFORE_CASE_FILTER",
            "tables": result}


def _static_reaction_reference_diagnostics(records):
    """Summarize compatible reported force groups; never sum envelopes or moments."""
    components = ("FX", "FY", "FZ", "MX", "MY", "MZ")
    groups = {}
    excluded = Counter()
    for record in records:
        key = tuple(record[c] for c in _CASE_COLUMNS)
        static = key[1] == "LinStatic" and (
            (key[2] is None and key[3] is None) or
            (key[2] == "Step By Step" and key[3] is not None))
        if not static:
            excluded[str(key[1]) + " | " + str(key[2])] += 1
            continue
        group = groups.setdefault(key, {"values": {}, "ambiguous": set(), "blank": set(),
                                         "row_count": 0})
        group["row_count"] += 1
        uid = record["Unique Name"]
        vector = tuple(record[c] for c in components)
        if uid in group["values"]:
            group["ambiguous"].add(uid)
        group["values"][uid] = vector
        if any(v is None for v in vector):
            group["blank"].add(uid)
    result = []
    for key, group in groups.items():
        values = group["values"]
        valid = not group["ambiguous"] and not group["blank"]
        entry = dict(zip(_CASE_COLUMNS, key))
        entry.update(row_count=group["row_count"], joint_count=len(values),
                     ambiguous_joint_ids=sorted(group["ambiguous"]),
                     incomplete_joint_ids=sorted(group["blank"]),
                     reported_force_sum_kN=None, nonzero_reaction_joint_ids=None,
                     zero_reaction_joint_ids=None)
        if valid:
            entry["reported_force_sum_kN"] = {
                c: math.fsum(vector[i] for vector in values.values())
                for i, c in enumerate(components[:3])}
            entry["nonzero_reaction_joint_ids"] = sorted(
                uid for uid, vector in values.items() if any(v != 0 for v in vector))
            entry["zero_reaction_joint_ids"] = sorted(
                uid for uid, vector in values.items() if all(v == 0 for v in vector))
        result.append(entry)
    return {"status": "REFERENCE_ONLY_NOT_PHYSICAL_SUPPORT_OR_EQUILIBRIUM_ACCEPTANCE",
            "scope": "ALL_UNIQUE_SOURCE_ROWS_BEFORE_CASE_FILTER",
            "groups": result, "excluded_row_counts_by_case_step_type": dict(excluded)}


def _frame_station_reference_diagnostics(records, family):
    """Describe reported station coverage; not native geometry or force acceptance."""
    cases, positions, groups = set(), {}, {}
    checked = blank_location = missing = negative = different = repeated = 0
    for record in records:
        checked += 1
        obj = (record['Story'], record[family], record['Unique Name'])
        case = tuple(record[c] for c in ('Output Case', 'Case Type', 'Step Type', 'Step Number'))
        station, elem_station = record['Station'], record['Elem Station']
        location = record['Location']
        blank_location += location is None
        missing += station is None or elem_station is None
        negative += any(v is not None and v < 0 for v in (station, elem_station))
        different += station is not None and elem_station is not None and station != elem_station
        pos = (record['Element'], station, elem_station, location)
        cases.add(case)
        positions.setdefault(obj, set()).add(pos)
        group = groups.setdefault((obj, case), set())
        repeated += pos in group
        group.add(pos)
    return {
        'scope': 'ALL_UNIQUE_SOURCE_ROWS_BEFORE_CASE_FILTER',
        'status': 'REFERENCE_ONLY_STATION_COVERAGE_NOT_NATIVE_VALIDATION',
        'checked_rows': checked, 'objects': len(positions), 'case_step_identities': len(cases),
        'missing_object_case_groups': len(positions)*len(cases)-len(groups),
        'position_coverage_difference_groups': sum(v != positions[obj] for (obj, _), v in groups.items()),
        'repeated_position_rows': repeated, 'blank_location_rows': blank_location,
        'missing_station_rows': missing, 'negative_station_rows': negative,
        'different_station_coordinate_rows': different,
    }


def _element_joint_force_reference_diagnostics(topology, responses, *, family):
    """Check exported positions only, not local axes or force equilibrium."""
    endpoints = ('Elm JtI', 'Elm JtJ') if family == 'Frame' else tuple(f'Elm Jt{i}' for i in range(1, 5))
    expected = set()
    for row in topology:
        if family == 'Frame' and row['Object Type'] != 'Frame':
            continue
        prefix = tuple(row[c] for c in ('Story', 'Object Label', 'Object Name', 'Element Name'))
        expected.update((*prefix, row[c]) for c in endpoints if row[c] is not None)
    observed, cases, groups = set(), set(), set()
    unmatched_rows = checked = 0
    samples = []
    for row in responses:
        position = tuple(row[c] for c in ('Story', 'Frame' if family == 'Frame' else 'Shell Object',
                                          'Unique Name', f'{family} Element', 'Joint'))
        case = tuple(row[c] for c in ('Output Case', 'Case Type', 'Step Type', 'Step Number'))
        checked += 1
        observed.add(position)
        cases.add(case)
        groups.add((position, case))
        if position not in expected:
            unmatched_rows += 1
            if len(samples) < 100:
                samples.append(row['worksheet_row'])
    return {'scope': 'ALL_UNIQUE_SOURCE_ROWS_BEFORE_CASE_FILTER',
            'status': 'REFERENCE_ONLY_POSITION_IDENTITY_NOT_FORCE_EQUILIBRIUM',
            'checked_rows': checked, 'expected_positions': len(expected),
            'observed_positions': len(observed), 'unmatched_response_rows': unmatched_rows,
            'unmatched_response_positions': len(observed - expected),
            'topology_positions_without_results': len(expected - observed),
            'case_step_identities': len(cases),
            'missing_observed_position_case_groups': len(observed) * len(cases) - len(groups),
            'unmatched_worksheet_row_samples': samples}


def _full_gravity_source_diagnostics(joints, reactions, story_forces):
    """Exact case/source identity and vertical cut check; not solver acceptance."""
    case = ('1. DL + LL', 'Combination', None, None)
    fields = ('Output Case', 'Case Type', 'Step Type', 'Step Number')
    components = ('FX', 'FY', 'FZ', 'MX', 'MY', 'MZ')
    def selected(row):
        return tuple(row[c] for c in fields) == case
    topology = {}
    ambiguous = set()
    for row in joints:
        uid = row['Element Name']
        if uid in topology:
            ambiguous.add(uid)
        topology[uid] = row
    source = [row for row in reactions if selected(row)]
    cuts = [row for row in story_forces if selected(row) and row['Story'] == 'Story1' and row['Location'] == 'Bottom']
    seen, unmatched, duplicates, invalid = set(), set(), set(), set()
    nonzero, zero = [], []
    for row in source:
        uid = row['Unique Name']
        if uid in seen:
            duplicates.add(uid)
        seen.add(uid)
        joint = topology.get(uid)
        if (uid in ambiguous or joint is None or row['Story'] != 'Base'
                or joint['Story'] != row['Story'] or joint['Object Label'] != row['Label']):
            unmatched.add(uid)
        vector = tuple(row[c] for c in components)
        if any(v is None or not math.isfinite(v) for v in vector):
            invalid.add(uid)
            continue
        (nonzero if any(v != 0 for v in vector) else zero).append(uid)
    cut = cuts[0]['P'] if len(cuts) == 1 else None
    valid = bool(source) and not (unmatched or duplicates or invalid) and cut is not None and math.isfinite(cut)
    total = math.fsum(row['FZ'] for row in source) if valid else None
    return {'status': 'REFERENCE_ONLY_NOT_NATIVE_SUPPORT_OR_SOLVER_ACCEPTANCE',
            'case': dict(zip(fields, case)), 'reaction_rows': len(source),
            'bottom_cut_rows': len(cuts), 'unmatched_joint_ids': sorted(unmatched),
            'duplicate_joint_ids': sorted(duplicates), 'invalid_joint_ids': sorted(invalid),
            'nonzero_reaction_joint_ids': sorted(nonzero), 'zero_reaction_joint_ids': sorted(zero),
            'reported_vertical_reaction_kN': total, 'reported_story1_bottom_P_kN': cut,
            'signed_vertical_difference_kN': total - cut if valid else None,
            'physical_support_mapping': 'NOT_VERIFIED', 'engineering_acceptance': 'NOT_VERIFIED'}


def _diaphragm_cm_reference_diagnostics(centers, displacements):
    """Match repeated floor mass/CM fields without summing response rows."""
    index, ambiguous = {}, set()
    for row in centers:
        key = (row["Story"], row["Diaphragm"])
        if key in index:
            ambiguous.add(key)
        index[key] = row
    pairs = (("X", "XCM"), ("Y", "YCM"),
             ("Diaphragm Mass X", "Mass X"), ("Diaphragm Mass Y", "Mass Y"))
    checked = matching = mismatched = missing = 0
    samples = []
    for row in displacements:
        checked += 1
        key = (row["Story"], row["Diaphragm"])
        baseline = index.get(key)
        if baseline is None or key in ambiguous:
            missing += 1
        elif all(row[a] is not None and baseline[b] is not None
                 and row[a] == baseline[b] for a, b in pairs):
            matching += 1
            continue
        else:
            mismatched += 1
        if len(samples) < 100:
            samples.append(row["worksheet_row"])
    return {"scope": "ALL_UNIQUE_SOURCE_ROWS_BEFORE_CASE_FILTER",
            "status": "REFERENCE_ONLY_NOT_NATIVE_MASS_OR_TORSION_ACCEPTANCE",
            "checked_rows": checked, "matching_rows": matching,
            "mismatched_rows": mismatched, "missing_reference_rows": missing,
            "ambiguous_center_keys": len(ambiguous), "exception_row_samples": samples}


def _reference_checks(tables, store=None):
    def rows(name):
        return store.rows(name) if store else tables[name]["rows"]

    modal = {}
    if _PERIODS in tables:
        baseline = tables[_PERIODS]
        case, mode, period = (baseline["columns"].index(c) for c in ("Case", "Mode", "Period"))
        periods = {(row[case], row[mode]): row[period] for row in rows(_PERIODS)}
        for name in _PERIOD_TABLES:
            if name not in tables:
                continue
            table = tables[name]
            case_name = "ModalCase" if name == "Response Spectrum Modal Info" else "Case"
            case, mode, period = (table["columns"].index(c) for c in (case_name, "Mode", "Period"))
            matched = 0
            for row in rows(name):
                key = (row[case], row[mode])
                if key in periods:
                    if row[period] != periods[key]:
                        raise ValueError(f"{name} row {row[0]}: conflicting modal period for {key}")
                    matched += 1
            modal[name] = {"matched_rows": matched, "unmatched_rows": table["unique_row_count"] - matched}

    connectivity = {}
    if _JOINTS in tables:
        joints = tables[_JOINTS]
        index = joints["columns"].index("Element Name")
        joint_ids = {row[index] for row in rows(_JOINTS)}
        for name in (_FRAMES, _AREAS):
            if name not in tables:
                continue
            table = tables[name]
            endpoints = [i for i, c in enumerate(table["columns"]) if c.startswith("Elm Jt")]
            missing = {row[i] for row in rows(name) for i in endpoints} - joint_ids
            connectivity[name] = {"checked_rows": table["unique_row_count"], "unresolved_joint_ids": sorted(missing)}
    checks = {"modal_periods": modal, "connectivity": connectivity}

    def records(name):
        columns = tables[name]["columns"]
        return (dict(zip(columns, row)) for row in rows(name))

    if "Modal Participating Mass Ratios" in tables:
        checks["modal_mass_reference"] = _modal_mass_reference_diagnostics(
            records("Modal Participating Mass Ratios"))
    if _JOINTS in tables and "Story Drifts" in tables:
        checks["story_drift_joint_reference"] = _story_drift_joint_reference_diagnostics(
            records(_JOINTS), records("Story Drifts"))
    joint_response_names = [name for name in tables
                            if name.startswith("Joint ") and "Unique Name" in tables[name]["columns"]]
    if _JOINTS in tables and joint_response_names:
        checks["joint_response_identity"] = _joint_response_identity_diagnostics(
            records(_JOINTS), {name: records(name) for name in joint_response_names})
    if "Joint Reactions" in tables:
        checks["static_reaction_reference"] = _static_reaction_reference_diagnostics(
            records("Joint Reactions"))
    if all(name in tables for name in (_JOINTS, "Joint Reactions", "Story Forces")):
        checks["full_gravity_source"] = _full_gravity_source_diagnostics(
            records(_JOINTS), records("Joint Reactions"), records("Story Forces"))
    station_checks = {}
    for family in ("Column", "Brace"):
        name = f"Element Forces - {family}s"
        if name in tables:
            station_checks[name] = _frame_station_reference_diagnostics(records(name), family)
    if station_checks:
        checks["frame_station_reference"] = station_checks
    if all(name in tables for name in ("Centers Of Mass And Rigidity", "Diaphragm CM Displacements")):
        checks["diaphragm_cm_reference"] = _diaphragm_cm_reference_diagnostics(
            records("Centers Of Mass And Rigidity"), records("Diaphragm CM Displacements"))
    element_joint_checks = {}
    for family, topology_name, result_name in (
            ("Shell", _AREAS, "Element Joint Forces - Shells"),
            ("Shell", _AREAS, "Element Forces - Area Shells"),
            ("Frame", _FRAMES, "Element Joint Forces - Frame")):
        if topology_name in tables and result_name in tables:
            element_joint_checks[result_name] = _element_joint_force_reference_diagnostics(
                records(topology_name), records(result_name), family=family)
    if element_joint_checks:
        checks["element_joint_force_reference"] = element_joint_checks
    return checks


def _read_analysis_reference(paths, cases, progress, schemas, legacy_first_lot, store=None):
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
        source, imported = _read_reference_workbook(book, entry, schemas, progress, store)
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
    checks = _reference_checks(tables, store)
    missing_cases = selected - {name for table in tables.values() for name in table["case_row_counts"]}
    if missing_cases:
        raise ValueError("Requested ETABS case absent: " + ", ".join(sorted(missing_cases)))
    if store:
        if progress:
            progress("Indexing SQLite reference rows")
        store.keep_cases(selected)
        for table in tables.values():
            table["stored_row_count"] = (sum(table["case_row_counts"].get(case, 0) for case in selected)
                                         if selected and table["case_column"] else table["unique_row_count"])
    elif selected:
        for table in tables.values():
            if table["case_column"]:
                i = table["columns"].index(table["case_column"])
                table["rows"] = [row for row in table["rows"] if row[i] in selected]
    common = {
        "status": "WORKBOOK_REFERENCE_ONLY", "engineering_acceptance": "NOT_VERIFIED",
        "selected_cases": list(requested), "tables": tables,
    }
    if not store and legacy_first_lot and len(files) == 1 and tables.keys() <= _FIRST_LOT_TABLES.keys():
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
        **common, "schema": "ETABS_ANALYSIS_SQLITE_REFERENCE_V1" if store else "ETABS_ANALYSIS_REFERENCE_V1",
        "files": files,
        "missing_tables": sorted((schemas.keys() if store else schemas.keys() - _LARGE_TABLES.keys())
                                 - tables.keys()), "checks": checks,
    }


def read_analysis_reference(paths, *, cases=(), progress=None, legacy_first_lot=False, row_database=None):
    """[REF docs/source/components/inputs/etabs_table_bundle.py.md]

    Read ETABS workbook tables as reference evidence.
    Cross-check reported modal periods and endpoint IDs before filtering exact cases.
    Supply a new SQLite path to stream third- and fourth-lot rows to disk.
    """
    if row_database is None:
        return _read_analysis_reference(paths, cases, progress, _REFERENCE_TABLES, legacy_first_lot)
    target = Path(row_database)
    with target.open("xb"):
        pass
    try:
        with closing(sqlite3.connect(target)) as db:
            with db:
                store = _ReferenceRows(db)
                report = _read_analysis_reference(paths, cases, progress, _REFERENCE_TABLES, False, store)
            if report["selected_cases"]:
                db.execute("VACUUM")
        report["row_storage"] = {"format": "sqlite-v1", "file": target.name, "sha256": _sha(target)}
        return report
    except BaseException:
        target.unlink(missing_ok=True)
        raise


def read_first_lot_reference(path, *, cases=(), progress=None):
    """[REF docs/source/components/inputs/etabs_table_bundle.py.md]

    Read one first-lot workbook with the original single-workbook schema.
    """
    source = Path(path).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in (".xlsx", ".xlsm"):
        raise ValueError("Select one local ETABS .xlsx or .xlsm analysis workbook")
    return _read_analysis_reference([source], cases, progress, _FIRST_LOT_TABLES, True)
