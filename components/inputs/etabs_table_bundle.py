"""[REF docs/source/components/inputs/etabs_table_bundle.py.md]
Source-EDB-bound ETABS workbook registration. No file moves or uploads.

This records workbook identities and verified sheet inventories. It is not a
numerical ETABS/OpenSees equivalence comparison.
"""
from __future__ import annotations
import hashlib
import json
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
