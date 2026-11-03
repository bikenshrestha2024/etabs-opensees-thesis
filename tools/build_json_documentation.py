"""Build exhaustive JSON content documentation from *actual* local repository files.

No network, no data mutation. Creates one Markdown document per JSON plus index.
Use with --check to ensure generated schema docs match checked-out JSON contents.
Keys, types and field paths are inspected recursively; not guessed from filename.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DOCS=Path("docs/json/files")
CLASSIFICATION=[
("Material_Catalog/","MATERIAL_PROFILE"),
("Research_Components/cards/","COMPONENT_BENCHMARK_CARD"),
("Research_Components/paper_specimens/","EXPERIMENTAL_SOURCE_REGISTER"),
("Saved_Project_V156/","IMMUTABLE_HISTORICAL_PROJECT"),
("Worked_Example_","HISTORICAL_EXAMPLE_OUTPUT"),
("Verification_","VALIDATION_EVIDENCE"),
("Calibration_","CALIBRATION_EVIDENCE"),
("Input_Records_","GROUND_MOTION_METADATA")
]

def group(path):
    for prefix,category in CLASSIFICATION:
        if path.startswith(prefix):return category
    name=Path(path).name.lower()
    if "manifest" in name or "file_hash" in name:return "FILE_PROVENANCE_MANIFEST"
    if "runconfig" in name or "config" in name:return "RUN_CONFIGURATION"
    if "summary" in name or "result" in name:return "RUN_RESULT_OR_REPORT"
    if "model" in name or "source" in name:return "ETABS_MODEL_OR_SOURCE_METADATA"
    return "PROJECT_DATA_OR_REPORT"

def scalar_type(v):
    if v is None:return "null"
    if isinstance(v,bool):return "boolean"
    if isinstance(v,int):return "integer"
    if isinstance(v,float):return "number"
    return type(v).__name__

def describe_fields(node, prefix="$", depth=0, acc=None, limit=1000):
    if acc is None:acc={}
    if len(acc)>=limit:return acc
    if isinstance(node,dict):
        if not node:acc[prefix]="object(empty)"
        for key,value in node.items():
            name=prefix+"."+str(key).replace("|","/")
            typ="object" if isinstance(value,dict) else "array" if isinstance(value,list) else scalar_type(value)
            acc.setdefault(name,typ)
            if depth<6:
                describe_fields(value,name,depth+1,acc,limit)
    elif isinstance(node,list):
        if not node:acc[prefix+"[]"]="array(empty)"
        else:
            seen=set()
            for value in node[:10]:
                typ="object" if isinstance(value,dict) else "array" if isinstance(value,list) else scalar_type(value)
                if typ in seen:continue
                seen.add(typ)
                acc.setdefault(prefix+"[]",typ)
                if depth<6:describe_fields(value,prefix+"[]",depth+1,acc,limit)
    return acc

def content_doc(root, path, obj):
    raw=path.read_bytes()
    rel=path.relative_to(root).as_posix()
    hashval=hashlib.sha256(raw).hexdigest()
    role=group(rel)
    fields=describe_fields(obj)
    out=[
      "# "+rel,
      "",
      "**Source:** ["+rel+"](../../../../"+rel+")",
      "**Classification:** "+role,
      "**SHA-256 (source bytes):** "+hashval,
      "**Size:** "+str(len(raw))+" bytes",
      "**Root JSON type:** "+("object" if isinstance(obj,dict) else "array" if isinstance(obj,list) else scalar_type(obj)),
      "**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.",
      "",
      "## Fields actually present",
      "",
      "| JSON path | Observed type |",
      "|---|---|",
    ]
    out += ["| "+k.replace("|","/")+" | "+v+" |" for k,v in fields.items()]
    out += ["",
      "## Interpretation and provenance",
      "",
      "- Source of truth: the original JSON file at the path above. This generated reference never changes original data.",
      "- This is an OBSERVED FIELD INVENTORY, not a formal JSON Schema or proof every nested record has identical keys.",
      "- Original units, code edition, specimen/ETABS source, record ID, solver version and experimental status must be checked within the source file or linked manifest.",
      "- A value without documented units/source must be classified UNVERIFIED, not automatically assumed kN-m-s.",
      "- For historical outputs do not use to populate current run configuration or calibrated material parameters.",
      "- Material/source specimens are not project-approved RC bar schedules or manufacturer-qualified dampers.",
      "- External data may be private. This script runs offline and does not upload file contents.",
      "",
      "## Validation requirements",
      "",
      "- Confirm valid UTF-8 JSON and expected field/type/units against the producing program.",
      "- Verify hashes, compare input and output manifests, and preserve experiment/case identity.",
      "- For nonlinear runs check G00–G10 acceptance gates and explicit failure/incomplete statuses.",
      "",
      "[All JSON files](../../00_ALL_JSON_FILES.md) · [Research citations](../../../00_RESEARCH_REFERENCES.md)"
    ]
    return "\n".join(out)+"\n"

def generate(root,*,check=False):
    root=root.resolve()
    paths=sorted(p for p in root.rglob("*.json") if
        ".git" not in p.parts and "docs" not in p.relative_to(root).parts
        and ".pytest_cache" not in p.parts)
    index=["# 00 — Comprehensive JSON documentation","",
        "Generated from directly parsed local JSON content. Each original JSON receives an observed key/type guide, source checksum and role, without rewriting its source.",
        "",
        "| JSON file | Guide | Category | Content parsing |",
        "|---|---|---|---|"]
    failures=[]
    for p in paths:
        rel=p.relative_to(root).as_posix()
        dest=root/DOCS/(rel+".md")
        try:
            obj=json.loads(p.read_text(encoding="utf-8-sig"))
            page=content_doc(root,p,obj)
            state="PARSED"
        except (UnicodeError,ValueError,OSError) as exc:
            state="INVALID_JSON"
            failures.append(rel+": "+str(exc))
            page="# "+rel+"\n\nINVALID_JSON: "+str(exc)+"\n"
        if check:
            if not dest.exists() or dest.read_text(encoding="utf-8")!=page:
                failures.append("Missing/stale documentation: "+rel)
        else:
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(page,encoding="utf-8")
        index.append("| "+rel+" | [Schema](files/"+rel+".md) | "+group(rel)+" | "+state+" |")
    summary="\n".join(index)+"\n"
    ix=root/"docs/json/00_ALL_JSON_FILES.md"
    if check:
        if not ix.exists() or ix.read_text(encoding="utf-8")!=summary:
            failures.append("Stale JSON index")
    else:
        ix.parent.mkdir(parents=True,exist_ok=True)
        ix.write_text(summary,encoding="utf-8")
    return {"files":len(paths),"issues":failures,"index":str(ix)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    report=generate(args.repo,check=args.check)
    print(json.dumps(report,indent=2))
    return 0 if not report["issues"] else 1

if __name__=="__main__":
    raise SystemExit(main())
