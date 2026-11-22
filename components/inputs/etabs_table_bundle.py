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
    old={k:v for k,v in old.items() if not k.startswith("etabs_beam_forces_element_")}
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
