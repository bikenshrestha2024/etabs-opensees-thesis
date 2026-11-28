"""[REF docs/source/tools/audit_beam_force_shards.py.md]
Audit the three ETABS ``Element Forces - Beams`` workbooks as one sharded table.

Workbooks are opened read-only and streamed; the report keeps names, SHA-256 and
aggregate counts, never rows or local paths. Not engineering acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BEAM_SHEET = "Element Forces - Beams"
FRAME_SHEET = "Objects and Elements - Frames"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def stream_table(path, sheet):
    """Yield dict rows of an ETABS table sheet (row 1 title, row 2 names, row 3 units)."""
    import openpyxl
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        worksheet = workbook[sheet]
        worksheet.reset_dimensions()
        names = None
        for index, row in enumerate(worksheet.iter_rows(values_only=True)):
            if index == 1:
                names = [str(v) if v is not None else "" for v in row]
            elif index >= 3 and names:
                if any(v is not None for v in row):
                    yield dict(zip(names, row))
    finally:
        workbook.close()


def frame_story_map(path):
    return {str(r["Element Name"]): str(r["Story"]) for r in stream_table(path, FRAME_SHEET)}


def build_document(beam_paths, frame_workbook=None):
    from components.validation.etabs_beam_force_shards import audit_beam_force_shards
    frames = frame_story_map(frame_workbook) if frame_workbook else None
    shards = [(f"beam_{i}", stream_table(p, BEAM_SHEET)) for i, p in enumerate(beam_paths, 1)]
    doc = audit_beam_force_shards(shards, frame_elements=frames)
    doc["ingested_files"] = [{"shard": f"beam_{i}", "file_name": Path(p).name, "sha256": _sha256(p),
                              "size_bytes": Path(p).stat().st_size} for i, p in enumerate(beam_paths, 1)]
    if frame_workbook:
        doc["frame_table_source"] = {"file_name": Path(frame_workbook).name, "sha256": _sha256(frame_workbook)}
    return doc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--beam-files", type=Path, nargs="+", required=True)
    parser.add_argument("--frame-workbook", type=Path, help="Workbook with 'Objects and Elements - Frames' (second lot)")
    parser.add_argument("--output", type=Path, required=True, help="New JSON file; never overwritten")
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("--output exists; refusing to overwrite")
    doc = build_document(args.beam_files, args.frame_workbook)
    args.output.write_text(json.dumps(doc, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {args.output.name}: {doc['union_status']}, {len(doc['findings'])} findings")
    return 0 if doc["union_status"] == "UNION_COMPLETE_AND_CONSISTENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
