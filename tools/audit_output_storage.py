"""Read-only output storage audit for the ETABS-to-OpenSees thesis.

[REF docs/source/tools/audit_output_storage.py.md]
Python 3.12, standard library only. Does not delete, rewrite, rename or
deduplicate original solver evidence. Use --root with the chosen project
output root. If no --root is supplied, choose a folder via tkinter.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import io
import re
import shutil
import sys
import tempfile
from xml.etree import ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, BadZipFile


def _refuse_linked_chain(path):
    """Refuse linked roots/parents before resolve or output creation."""
    candidate=Path(path).expanduser()
    if any(part.is_symlink() for part in (candidate,*candidate.parents)):
        raise ValueError("Refusing linked disk-audit source or output path")
    return candidate


def _sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


_SHEET_XML = re.compile(r"^xl/worksheets/[^/]+\.xml$")
_XL_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_MAX_EMBEDDED_WORKBOOK_BYTES = 512 * 1024 * 1024


def _check_archive(archive):
    names=archive.namelist()
    if len(names)!=len(set(names)):
        raise ValueError("Duplicate archive member names")
    bad=archive.testzip()
    if bad is not None:
        raise ValueError("CRC failure: "+bad)
    return names


def _workbook_formula_inventory(archive, names):
    """Stream worksheet XML. A cache is evidence of a saved value, not correctness."""
    if "xl/workbook.xml" not in names:
        raise ValueError("Missing Excel workbook XML")
    with archive.open("xl/workbook.xml") as stream:
        ET.parse(stream)
    sheets=[]
    for name in sorted(n for n in names if _SHEET_XML.fullmatch(n)):
        formulas=missing=errors=0
        with archive.open(name) as stream:
            # Retain child formula/value nodes until their containing cell closes.
            stack=[]
            for event,elem in ET.iterparse(stream,events=("start","end")):
                if event=="start":
                    stack.append(elem)
                    continue
                if elem.tag==_XL_NS+"c":
                    if elem.find(_XL_NS+"f") is not None:
                        formulas+=1
                        value=elem.find(_XL_NS+"v")
                        if value is None or value.text is None or not value.text.strip():
                            missing+=1
                        elif elem.get("t")=="e":
                            errors+=1
                    elem.clear()
                elif elem.tag==_XL_NS+"row":
                    if len(stack)>1:
                        stack[-2].remove(elem)
                    elem.clear()
                stack.pop()
        sheets.append(dict(worksheet_xml=name,formula_cells=formulas,
                           missing_cached_formula_values=missing,cached_formula_errors=errors))
    return dict(formula_cells=sum(s["formula_cells"] for s in sheets),
                missing_cached_formula_values=sum(s["missing_cached_formula_values"] for s in sheets),
                cached_formula_errors=sum(s["cached_formula_errors"] for s in sheets),
                worksheets=sheets)


def _embedded_evidence(archive, names):
    """Inspect supported members directly, without extracting or executing them."""
    records=[]
    for name in names:
        if name.endswith("/"):
            continue
        ext=Path(name).suffix.lower()
        if ext not in {".xlsx",".xlsm",".json",".jsonl",".png",".log",".txt",".csv",".zip"}:
            continue
        item={"member":name}
        try:
            if ext in {".xlsx",".xlsm"}:
                if archive.getinfo(name).file_size>_MAX_EMBEDDED_WORKBOOK_BYTES:
                    item["status"]="REVIEW_REQUIRED_EMBEDDED_WORKBOOK_SIZE_LIMIT"
                else:
                    with tempfile.SpooledTemporaryFile(max_size=8*1024*1024) as buffer:
                        with archive.open(name) as source:
                            shutil.copyfileobj(source,buffer)
                        buffer.seek(0)
                        with ZipFile(buffer) as workbook:
                            item["excel_formula_inventory"]=_workbook_formula_inventory(workbook,_check_archive(workbook))
                    item["status"]="EXCEL_XML_CHECKED"
            elif ext==".zip":
                item["status"]="REVIEW_REQUIRED_NESTED_ZIP_NOT_INSPECTED"
            else:
                with archive.open(name) as raw:
                    if ext==".png":
                        if raw.read(8)!=b"\x89PNG\r\n\x1a\n":
                            raise ValueError("Invalid PNG signature")
                        item["status"]="PNG_SIGNATURE_CHECKED"
                    else:
                        with io.TextIOWrapper(raw,encoding="utf-8-sig",errors="strict") as stream:
                            if ext==".json":
                                json.load(stream)
                                item["status"]="JSON_PARSED"
                            else:
                                for line in stream:
                                    if ext==".jsonl" and line.strip():
                                        json.loads(line)
                                item["status"]="JSONL_PARSED" if ext==".jsonl" else "TEXT_READ"
        except (OSError,ValueError,BadZipFile,RuntimeError,NotImplementedError,ET.ParseError) as exc:
            item.update(status="FORMAT_CHECK_FAILED",error=str(exc))
        records.append(item)
    return records


def _archive_manifest_checks(archive, names):
    """Verify known package manifest references against exact archive bytes."""
    registered=set(names)
    verified={}
    reports=[]
    for name in sorted(names):
        base=PurePosixPath(name).name
        if base not in {"ZIP_SHA256_MANIFEST.json","EVIDENCE_MANIFEST.json",
                        "REVIEW_MANIFEST.json","ESM_Export_Manifest.json"}:
            continue
        report={"manifest":name,"matched":0,"failed":0,"alias_matched":0,"issues":[]}
        try:
            with archive.open(name) as raw:
                data=json.load(io.TextIOWrapper(raw,encoding="utf-8-sig"))
            if not isinstance(data,dict):
                raise ValueError("Expected manifest object")
            parent=PurePosixPath(name).parent
            if base=="ZIP_SHA256_MANIFEST.json":
                rows=[{"path":p,"sha256":h} for p,h in data["files"].items()]
            elif base=="REVIEW_MANIFEST.json":
                rows=data["collected"]
            elif base=="EVIDENCE_MANIFEST.json":
                rows=[dict(row,path=row["archive_path"]) for row in data["files"]]
            else:
                rows=[dict(row,path=row["snapshot_path"]) for row in data["files"]]
            if not isinstance(rows,list) or not rows:
                raise ValueError("Missing or empty registered file inventory")
            seen=set()

            def check(row, alias=False):
                try:
                    rel=row["same_content_as" if alias else "path"]
                    if not isinstance(rel,str) or not rel or any(p in ("",".","..") for p in rel.split("/")) or "\\" in rel or ":" in rel:
                        raise ValueError("Unsafe relative manifest member")
                    member=str(parent/PurePosixPath(rel))
                    if member not in registered or member.endswith("/"):
                        raise ValueError("Registered member missing: "+member)
                    if not alias:
                        if member in seen:
                            raise ValueError("Repeated registered member")
                        seen.add(member)
                    elif member not in seen:
                        raise ValueError("Alias target is not a registered member")
                    expected=row["sha256"]
                    if not isinstance(expected,str) or not re.fullmatch(r"[0-9a-fA-F]{64}",expected):
                        raise ValueError("Invalid SHA256 reference")
                    if member not in verified:
                        with archive.open(member) as source:
                            verified[member]=hashlib.file_digest(source,"sha256").hexdigest()
                    if verified[member]!=expected.lower():
                        raise ValueError("SHA256 mismatch")
                    if "bytes" in row and row["bytes"]!=archive.getinfo(member).file_size:
                        raise ValueError("Byte count mismatch")
                    report["alias_matched" if alias else "matched"]+=1
                except (KeyError,TypeError,ValueError,OSError,RuntimeError) as exc:
                    report["failed"]+=1
                    report["issues"].append({"reference":str(row.get("path","")) if isinstance(row,dict) else repr(row),"reason":str(exc)})
            for row in rows:
                check(row)
            if base=="REVIEW_MANIFEST.json":
                for row in data.get("duplicates",[]):
                    check(row,alias=True)
            declared=data.get("file_count",data.get("unique_file_count"))
            if declared is not None and declared!=len(rows):
                raise ValueError("Declared manifest count differs from registered rows")
        except (KeyError,AttributeError,TypeError,ValueError,OSError,RuntimeError) as exc:
            report["failed"]+=1
            report["issues"].append({"reason":str(exc)})
        reports.append(report)
    return reports


def _validate_container(path, details):
    """Read-only format checks; never execute archive members or formulas."""
    ext=path.suffix.lower()
    if ext == ".json":
        with path.open("r",encoding="utf-8-sig") as stream:
            json.load(stream)
        return "JSON_PARSED"
    if ext in {".zip",".xlsx",".xlsm",".docx",".pptx"}:
        with ZipFile(path) as archive:
            names=_check_archive(archive)
            if ext in {".xlsx",".xlsm"}:
                details["excel_formula_inventory"]=_workbook_formula_inventory(archive,names)
            elif ext==".zip":
                details["embedded_evidence"]=_embedded_evidence(archive,names)
                details["archive_manifest_checks"]=_archive_manifest_checks(archive,names)
        return "ZIP_CRC_CHECKED"
    if ext == ".png":
        with path.open("rb") as stream:
            if stream.read(8)!=b"\x89PNG\r\n\x1a\n":
                raise ValueError("Invalid PNG signature")
        return "PNG_SIGNATURE_CHECKED"
    if ext in {".log",".txt",".csv",".jsonl"}:
        with path.open("r",encoding="utf-8-sig",errors="strict") as stream:
            for line in stream:
                if ext == ".jsonl" and line.strip():
                    json.loads(line)
        return "TEXT_READ" if ext!=".jsonl" else "JSONL_PARSED"
    return "NOT_FORMAT_CHECKED"


def scan_output(root, *, max_large=50, hash_duplicates=True,
                include_entries=False, validate_files=False):
    """Inventory actual bytes and content-identical files without mutation.

    A file's location and basename have no effect on the SHA identity.
    Two distinct solver runs often differ only slightly; those files are
    NOT duplicates and must never be deleted based on name alone.
    Symlinked files/directories are intentionally not followed.
    """
    root = _refuse_linked_chain(root).resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    entries = []
    errors = []
    def walk_error(exc):
        errors.append({"path":str(exc.filename or root),"error":str(exc)})
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False, onerror=walk_error):
        dirnames[:] = [d for d in dirnames if not (Path(dirpath) / d).is_symlink()]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.is_symlink():
                continue
            try:
                stat = path.stat()
                rel = path.relative_to(root)
                entries.append({
                    "relative_path": str(rel).replace("\\", "/"),
                    "bytes": stat.st_size,
                    "extension": path.suffix.lower() or "(none)",
                    "module_folder": rel.parts[0] if len(rel.parts) > 1
                                     else "(root)",
                })
            except OSError as exc:
                errors.append({"path": str(path), "error": str(exc)})
    by_module = defaultdict(lambda: {"bytes": 0, "count": 0})
    by_type = defaultdict(lambda: {"bytes": 0, "count": 0})
    by_size = defaultdict(list)
    for item in entries:
        by_module[item["module_folder"]]["bytes"] += item["bytes"]
        by_module[item["module_folder"]]["count"] += 1
        by_type[item["extension"]]["bytes"] += item["bytes"]
        by_type[item["extension"]]["count"] += 1
        # Zero-byte files are allowed but should not produce vast false duplicate reports.
        if item["bytes"]:
            by_size[item["bytes"]].append(item)
    duplicates = []
    if hash_duplicates:
        for size, candidates in by_size.items():
            if len(candidates) < 2:
                continue
            groups = defaultdict(list)
            for item in candidates:
                try:
                    groups[_sha256(root / item["relative_path"])].append(item)
                except OSError as exc:
                    errors.append({"path": item["relative_path"], "error": str(exc)})
            for digest, group in groups.items():
                if len(group) > 1:
                    duplicates.append({
                        "sha256": digest, "bytes_per_file": size,
                        "repeat_count": len(group),
                        "redundant_bytes": (len(group) - 1) * size,
                        "paths": [x["relative_path"] for x in group],
                        "review_only": True,
                    })
    validation_counts=defaultdict(int)
    embedded_counts=defaultdict(int)
    formula_totals={"workbook_instances":0,"formula_cells":0,
                    "missing_cached_formula_values":0,"cached_formula_errors":0}
    review_required=0
    manifest_totals={"manifests":0,"matched":0,"alias_matched":0,"failed":0}
    if validate_files:
        for item in entries:
            try:
                status=_validate_container(root/item["relative_path"],item)
            except (OSError, ValueError, BadZipFile, RuntimeError, NotImplementedError, ET.ParseError) as exc:
                status="FORMAT_CHECK_FAILED"
                errors.append({"path":item["relative_path"],"error":str(exc)})
            item["format_check"]=status
            validation_counts[status]+=1
            for manifest in item.get("archive_manifest_checks",[]):
                manifest_totals["manifests"]+=1
                for key in ("matched","alias_matched","failed"):
                    manifest_totals[key]+=manifest[key]
                if manifest["failed"]:
                    review_required+=1
            for member in item.get("embedded_evidence",[]):
                embedded_counts[member["status"]]+=1
                if member["status"]=="FORMAT_CHECK_FAILED":
                    errors.append({"path":item["relative_path"]+"!/"+member["member"],"error":member["error"]})
                elif member["status"].startswith("REVIEW_REQUIRED"):
                    review_required+=1
            for record in [item,*item.get("embedded_evidence",[])]:
                book=record.get("excel_formula_inventory")
                if book is not None:
                    formula_totals["workbook_instances"]+=1
                    for key in ("formula_cells","missing_cached_formula_values","cached_formula_errors"):
                        formula_totals[key]+=book[key]
                    if book["missing_cached_formula_values"] or book["cached_formula_errors"]:
                        review_required+=1
    result = {
        "schema": "etabs-opensees-output-size-audit-v1",
        "status": "DISK_FOOTPRINT_ONLY_NOT_ENGINEERING_EQUIVALENCE",
        "source_root": str(root),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "total_files": len(entries),
        "total_bytes": sum(x["bytes"] for x in entries),
        "module_folders": dict(sorted(by_module.items(),
                                      key=lambda pair: -pair[1]["bytes"])),
        "extensions": dict(sorted(by_type.items(),
                                  key=lambda pair: -pair[1]["bytes"])),
        "largest_files": sorted(entries, key=lambda x: -x["bytes"])[:max_large],
        "exact_duplicate_groups": sorted(duplicates,
                                         key=lambda x: -x["redundant_bytes"]),
        "exact_duplicate_redundant_bytes": sum(
            g["redundant_bytes"] for g in duplicates),
        "scan_errors": errors,
        "hash_duplicates": bool(hash_duplicates),
        "format_checks_requested": bool(validate_files),
        "format_check_counts": dict(validation_counts),
        "embedded_format_check_counts":dict(embedded_counts),
        "excel_formula_cache_inventory":formula_totals,
        "archive_manifest_inventory":manifest_totals,
        "file_evidence_review_required_count":review_required,
        "action": "REPORT_ONLY_NO_DELETION",
    }
    if include_entries:
        result["files"]=sorted(entries,key=lambda item:item["relative_path"])
    return result


def write_report(report, destination):
    """Write only to a fresh dedicated review directory; never alter source runs."""
    out = _refuse_linked_chain(destination).resolve()
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("Report destination already contains files: " + str(out))
    out.mkdir(parents=True, exist_ok=True)
    for name in ("JSON", "CSV", "REPORT"):
        (out / name).mkdir(exist_ok=False)
    (out / "JSON" / "DISK_AUDIT.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    with (out / "CSV" / "LARGEST_FILES.csv").open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=(
            "relative_path", "bytes", "extension", "module_folder"),extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report["largest_files"])
    with (out / "CSV" / "EXACT_DUPLICATES.csv").open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.writer(fp)
        writer.writerow(("sha256", "bytes_per_file", "repeat_count",
                         "redundant_bytes", "relative_path"))
        for group in report["exact_duplicate_groups"]:
            for path in group["paths"]:
                writer.writerow((group["sha256"], group["bytes_per_file"],
                                 group["repeat_count"], group["redundant_bytes"], path))
    mib = 1024 ** 2
    lines = [
        "# Disk footprint — read-only evidence inventory",
        "",
        "**This is not permission to delete raw engineering results.**",
        "",
        "Root: `" + report["source_root"] + "`",
        "",
        "Total: **{:.2f} MiB** in {} files.".format(
            report["total_bytes"] / mib, report["total_files"]),
        "",
        "Exact duplicate footprint (review candidates only): **{:.2f} MiB**.".format(
            report["exact_duplicate_redundant_bytes"] / mib),
        "",
        "## Top-level folder sizes",
        "",
        "| Folder | Size (MiB) | Files |",
        "|---|---:|---:|",
    ]
    for name, info in report["module_folders"].items():
        lines.append("| `{}` | {:.2f} | {} |".format(
            name.replace("|", "/"), info["bytes"] / mib, info["count"]))
    lines.extend([
        "",
        "## Engineering storage rules",
        "",
        "Source model JSON, original ETABS EDB and verified Excel calculations, "
        "native logs, stage results and SHA evidence must remain immutable.",
        "Repeated derived PNG/PDF/ZIP packages may be copied rather than linked. "
        "Use exact SHA matching and provenance mapping before proposing cleanup.",
        "A matching basename or similar size does not establish duplication. "
        "This program NEVER deletes, overwrites, moves or hardlinks files.",
        "",
        "## Outstanding",
        "",
        "Classify the largest files as raw or derived, verify active case readers, "
        "preserve a sole authoritative result for each source/case, then review "
        "potential archival actions manually. Native ETABS/OpenSees physics "
        "equivalence is not assessed by disk size.",
    ])
    (out / "REPORT" / "READ_FIRST.md").write_text("\n".join(lines) + "\n",
                                       encoding="utf-8")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Existing project output root")
    parser.add_argument("--out", help="New report folder (outside the audited root preferred)")
    parser.add_argument("--no-hash", action="store_true",
                        help="Fast size-only inventory; no duplicate SHA checks")
    parser.add_argument("--validate-files",action="store_true",
                        help="Check supported file formats and embedded Excel formula caches")
    args = parser.parse_args(argv)
    root = args.root
    if not root:
        from tkinter import Tk, filedialog
        top = Tk()
        top.withdraw()
        try:
            root = filedialog.askdirectory(title="Select original project output root")
        finally:
            top.destroy()
    if not root:
        raise SystemExit("No output directory selected; nothing modified.")
    # Save local diagnostics in the selected case's canonical output stage.
    # The report describes the source snapshot BEFORE these new files are made;
    # previous saved audits are counted on subsequent disk inventories.
    if args.out:
        dest = Path(args.out)
    else:
        from components.inputs.output_layout import export_root_for
        dest = (export_root_for(root) / "09_SOFTWARE_DIAGNOSTICS" /
                "DISK_AUDITS" / "RUNS" /
                datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ"))
    report = scan_output(root, hash_duplicates=not args.no_hash,
                         include_entries=args.validate_files,validate_files=args.validate_files)
    result = write_report(report, dest)
    print("DISK AUDIT (NO FILES REMOVED):", result)
    print("Total bytes:", report["total_bytes"],
          "| identical-file candidates:", report["exact_duplicate_redundant_bytes"])
    return 2 if report["scan_errors"] or report["file_evidence_review_required_count"] else 0


if __name__ == "__main__":
    if not __package__:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    raise SystemExit(main())
