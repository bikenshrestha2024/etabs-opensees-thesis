"""Classify user-selected ETABS Excel exports without changing original files.

[REF docs/source/components/inputs/etabs_excel_selection.py.md]
The analysed full table, the frame assignment export and the beam force
part(s) are different roles even when stored in the same local folder.
"""
from __future__ import annotations

import re
from pathlib import Path


def _sheetnames(path):
    from openpyxl import load_workbook
    book=load_workbook(path,read_only=True,data_only=True)
    try:
        return tuple(book.sheetnames)
    finally:
        book.close()


def _role(path):
    name=Path(path).stem.casefold()
    sheets=tuple(x.casefold() for x in _sheetnames(path))
    beam_sheets=[x for x in sheets if "element forces" in x and "beam" in x]
    if re.search(r"beam[ _-]*forces?[ _-]*element(?:[ _-]*\d+)?",name):
        return "beam"
    if "assignment export" in name or (
            "frame assigns - summary" in sheets and
            "material list by object type" in sheets):
        return "assignment"
    if "analysis export" in name or any(
            "joint reactions" in x or "base reactions" in x for x in sheets):
        return "analysis"
    if beam_sheets and len(beam_sheets)==len(sheets):
        return "beam"
    return "unclassified"


def classify_etabs_excel_selection(paths):
    """[REF docs/source/components/inputs/etabs_excel_selection.py.md]
    Assign all chosen files, preserving beam part ordering and ambiguity.
    """
    selected=[Path(p).expanduser().resolve() for p in paths]
    if not selected:
        raise ValueError("Select analysed ETABS export and all beam-force parts")
    if len({str(x).casefold() for x in selected})!=len(selected):
        raise ValueError("Duplicate workbook selection")
    groups={"analysis":[],"assignment":[],"beam":[],"unclassified":[]}
    for path in selected:
        if not path.is_file() or path.suffix.lower() not in (".xlsx",".xlsm"):
            raise ValueError("Missing or unsupported ETABS Excel file: "+str(path))
        groups[_role(path)].append(path)
    if groups["unclassified"]:
        raise ValueError("Unclassified ETABS Excel source(s): "+
                         ", ".join(x.name for x in groups["unclassified"]))
    if len(groups["assignment"])>1:
        raise ValueError("Multiple assignment exports selected; choose exact current source")
    # Full vs compressed analysis exports may coexist. Only one current
    # analyzed workbook can own the case, and users must choose it explicitly
    # when two distinct analysis files are present.
    if len(groups["analysis"])>1:
        raise ValueError(
            "Multiple analyzed exports selected. Choose ONE authoritative "
            "Analysis Export (usually *_compressed.xlsx), plus ALL beam parts.")
    return {
        "analysis":groups["analysis"][0] if groups["analysis"] else None,
        "assignment":groups["assignment"][0] if groups["assignment"] else None,
        "beam":sorted(groups["beam"],key=lambda p:p.name.casefold()),
    }


def discover_beam_force_parts(directory):
    """[REF docs/source/components/inputs/etabs_excel_selection.py.md]
    Return ordered Beam Forces Element 1/2/3 files without reading large cells.
    """
    root=Path(directory).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    parts={}
    for path in root.iterdir():
        if not path.is_file() or path.suffix.lower() not in (".xlsx",".xlsm"):
            continue
        match=re.search(r"beam[ _-]*forces?[ _-]*element[ _-]*(\d+)",
                        path.stem.casefold())
        if not match:
            continue
        index=int(match.group(1))
        if index in parts:
            raise ValueError(
                f"Multiple beam force workbooks claim Element {index}: "
                f"{parts[index].name} / {path.name}; manually choose exact parts.")
        parts[index]=path
    if not parts:
        raise ValueError("No Beam Forces Element numbered Excel parts in "+str(root))
    # A gap almost always represents an omitted split export. Do not publish
    # a plausibly complete source if one workbook is missing.
    indices=sorted(parts)
    if indices!=list(range(1,indices[-1]+1)):
        raise ValueError("Missing numbered beam-force part(s): "+str(
            sorted(set(range(1,indices[-1]+1))-set(indices))))
    return [parts[i] for i in indices]


def validate_full_table_selection(path):
    """[REF docs/source/components/inputs/etabs_excel_selection.py.md]
    Require the worksheet consumed by the offline gravity reaction reader.
    """
    source=Path(path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError("Analyzed full table missing: "+str(source))
    if source.suffix.lower() not in (".xlsx",".xlsm",".csv"):
        raise ValueError("Expected analyzed ETABS Excel or Joint Reactions CSV")
    if source.suffix.lower()==".csv":
        return source
    names=tuple(n.strip().casefold() for n in _sheetnames(source))
    if names and all("beam" in n and "force" in n for n in names):
        raise ValueError(
            "This is a BEAM-FORCE-ONLY workbook, not an analyzed ETABS "
            "Joint Reactions/full-table export. Select Analysis Export "
            "ULS 3 storey latest_compressed.xlsx in the full-table field, "
            "and select all Beam Forces Element parts separately.")
    if names.count("joint reactions") != 1:
        raise ValueError(
            "ETABS gravity comparison requires exactly one Joint Reactions worksheet. "
            "Partial analysis lots may be inspected with the multi-lot audit, "
            "but cannot replace the joint-reaction source.")
    return source


def _catalog_sha256(path):
    import hashlib
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def build_analysis_table_catalog(paths):
    """Index exact worksheet owners in explicitly selected local analysis lots.

    [REF docs/source/components/inputs/etabs_excel_selection.py.md]
    This checks sheet names and file identity, not the engineering contents,
    source EDB identity or permission to use partial data as solver inputs.
    Duplicate names remain ambiguous; no table is silently merged or chosen.
    """
    from openpyxl import load_workbook
    selected = [Path(p).expanduser().resolve(strict=True) for p in paths]
    if not selected or len({str(p).casefold() for p in selected}) != len(selected):
        raise ValueError("Select distinct analysis workbook lots")
    files, tables, digests = [], {}, set()
    for path in selected:
        if not path.is_file() or path.suffix.lower() not in (".xlsx", ".xlsm"):
            raise ValueError("Expected a local analysis workbook")
        before = _catalog_sha256(path)
        if before in digests:
            raise ValueError("Analysis lots have identical bytes")
        digests.add(before)
        with path.open("rb") as stream:
            book = load_workbook(stream, read_only=True, data_only=False, keep_links=False)
            try:
                names = [sheet.title for sheet in book.worksheets]
            finally:
                book.close()
        if not names or _catalog_sha256(path) != before:
            raise ValueError("Empty or modified analysis workbook")
        files.append({"path": str(path), "sha256": before, "worksheets": names})
        for name in names:
            tables.setdefault(name.strip().casefold(), []).append(
                {"file_index": len(files) - 1, "worksheet": name})
    return {"schema": "ETABS_ANALYSIS_TABLE_CATALOG_V1",
            "status": "REFERENCE_ROUTING_ONLY",
            "source_model_identity": "UNVERIFIED", "engineering_acceptance": "NOT_VERIFIED",
            "files": files, "tables": tables,
            "ambiguous_tables": sorted(name for name, owners in tables.items() if len(owners) != 1)}


def resolve_analysis_table(catalog, table_name):
    """Return the unique original path and exact worksheet title, after hashing.

    [REF docs/source/components/inputs/etabs_excel_selection.py.md]
    Callers must still validate headers, units, exact case/step keys, and EDB
    identity; a returned path is not a structural acceptance or a data merge.
    """
    if catalog.get("schema") != "ETABS_ANALYSIS_TABLE_CATALOG_V1":
        raise ValueError("Unsupported analysis table catalog")
    key = table_name.strip().casefold()
    owners = catalog["tables"].get(key, [])
    if len(owners) != 1:
        raise ValueError(f"Expected one owner for {table_name!r}; found {len(owners)}")
    owner = owners[0]
    entry = catalog["files"][owner["file_index"]]
    path = Path(entry["path"])
    if _catalog_sha256(path) != entry["sha256"]:
        raise ValueError("Analysis workbook bytes changed after indexing")
    from openpyxl import load_workbook
    with path.open("rb") as stream:
        book = load_workbook(stream, read_only=True, data_only=False, keep_links=False)
        try:
            matches = [s.title for s in book.worksheets if s.title.strip().casefold() == key]
        finally:
            book.close()
    if matches != [owner["worksheet"]] or _catalog_sha256(path) != entry["sha256"]:
        raise ValueError("Indexed worksheet identity changed")
    return path, owner["worksheet"]
