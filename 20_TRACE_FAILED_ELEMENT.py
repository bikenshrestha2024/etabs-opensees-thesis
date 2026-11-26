"""Read-only diagnostic for a reported OpenSees solver element tag.

Usage:
    python 20_TRACE_FAILED_ELEMENT.py "D:\\Thesis Opensees\\Etabs Nodes Export\\OpenSees_Analysis_Results\\RUN_FOLDER" --tag 110280

Run against the *same isolated_model directory* that generated the failure.
Does not run, modify or approve structural analysis.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


MAP_FILE = "OpenSees_Complete_Element_Map_V118.json"
DATA_FILE = "OpenSees_Complete_Model_Data_V118.json"


def read_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def find_candidates(folder: Path):
    if (folder / MAP_FILE).is_file():
        return [folder]
    if (folder / "isolated_model" / MAP_FILE).is_file():
        return [folder / "isolated_model"]
    mapped = {p.parent for p in folder.rglob(MAP_FILE)}
    if mapped:
        return sorted(mapped)
    if (folder / DATA_FILE).is_file():
        return [folder]
    if (folder / "isolated_model" / DATA_FILE).is_file():
        return [folder / "isolated_model"]
    return sorted({p.parent for p in folder.rglob(DATA_FILE)})


def add_element_metadata(match, element, data):
    nodes = element.get("nodes", [])
    coordinates = {str(node): data.get("nodes", {}).get(str(node)) for node in nodes}
    match.update(category=element.get("category"), node_tags=nodes,
                 node_coordinates=coordinates, properties=element.get("properties"),
                 source_element=element)


def trace(folder: Path, tag: int):
    mapping_file = folder / MAP_FILE
    data_file = folder / DATA_FILE
    map_exists = mapping_file.is_file()
    mapping = read_json(mapping_file) if map_exists else {}
    data = read_json(data_file) if data_file.is_file() else None
    matches = []
    for source_key, solver_tags in mapping.items():
        if isinstance(solver_tags, list) and tag in solver_tags:
            source_type, _, object_name = source_key.partition(":")
            match = {"source_key": source_key, "source_type": source_type,
                     "object_name": object_name, "solver_tag": tag}
            source_collection = {"FRAME": "frames", "AREA": "shells"}.get(source_type)
            if isinstance(data, dict) and source_collection:
                # Assembly appends solver tags in the same order as the
                # serialized cells or frame segments of each source object.
                elements = [
                    element for element in data.get(source_collection, [])
                    if str(element.get("object")) == object_name
                ]
                if (len(elements) == len(solver_tags)
                        and all(type(value) is int for value in solver_tags)
                        and solver_tags == sorted(set(solver_tags))):
                    add_element_metadata(match, elements[solver_tags.index(tag)], data)
                else:
                    match["metadata_status"] = "MAP_AND_MODEL_SEGMENTS_DISAGREE"
            matches.append(match)
    mapping_method = "element_map" if map_exists else "unavailable"
    if not map_exists and isinstance(data, dict):
        frame_first_tag = 100001
        frame_count = len(data.get("frames", []))
        shell_first_tag = frame_first_tag + frame_count
        if frame_first_tag <= tag < shell_first_tag:
            source_type = "FRAME"
            element = data["frames"][tag - frame_first_tag]
        elif shell_first_tag <= tag < shell_first_tag + len(data.get("shells", [])):
            source_type = "AREA"
            element = data["shells"][tag - shell_first_tag]
        else:
            element = None
            source_type = None
        if element is not None:
            object_name = str(element.get("object"))
            match = {
                "source_key": f"{source_type}:{object_name}",
                "source_type": source_type,
                "object_name": object_name,
                "solver_tag": tag,
            }
            add_element_metadata(match, element, data)
            matches.append(match)
            mapping_method = "deterministic_tag_range_fallback"
    return {"isolated_model": str(folder.resolve()), "tag": tag,
            "element_map_found": map_exists, "mapping_method": mapping_method,
            "model_data_found": data is not None,
            "matches": matches,
            "warning": "First non-finite response after solver failure may be a downstream symptom, not the initiating element."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="Failed run or isolated_model directory")
    parser.add_argument("--tag", type=int, default=110280)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if not args.folder.is_dir():
        parser.error(f"Directory not found: {args.folder}")
    candidates = find_candidates(args.folder)
    if not candidates:
        parser.error(f"{MAP_FILE} not found under {args.folder}")
    reports = [trace(folder, args.tag) for folder in candidates]
    report = {"status": "FOUND" if any(r["matches"] for r in reports) else "NOT_FOUND",
              "searched_models": len(reports), "results": reports}
    output = args.output or (args.folder / f"Failed_Element_{args.tag}_Trace.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"status": report["status"], "searched_models": len(reports),
                      "matches": sum(len(r["matches"]) for r in reports),
                      "report": str(output)}, indent=2))
    if report["status"] != "FOUND":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
