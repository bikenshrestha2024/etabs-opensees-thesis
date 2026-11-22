"""Ensure every current component package documents its actual Python modules.

[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]
Only reads current files; never follows links, executes modules, migrates
outputs or assumes a documented module has passed engineering acceptance.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

_LINK=re.compile(r"\[([^\]\n]+\.py)\]\(([^)]+\.py)\)")

def audit(root):
    """[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]"""
    root=Path(root).expanduser().resolve(strict=True)
    components=root/"components"
    packages=[]
    problems=[]
    if not components.is_dir() or components.is_symlink():
        raise ValueError("No safe components/ directory")
    for folder in sorted(components.iterdir()):
        if not folder.is_dir() or folder.is_symlink():
            continue
        py=sorted(p.name for p in folder.glob("*.py")
                  if p.is_file() and not p.is_symlink())
        if not py:
            continue
        readme=folder/"README.md"
        if readme.is_symlink() or not readme.is_file():
            missing=py
            stale=[]
        else:
            text=readme.read_text(encoding="utf-8-sig")
            linked={name for name,target in _LINK.findall(text)
                    if name==target}
            missing=sorted(set(py)-linked)
            stale=sorted(linked-set(py))
        status="CURRENT" if not missing and not stale else "STALE_COMPONENT_INDEX"
        packages.append({"module":folder.name,"sources":len(py),
                         "missing_links":missing,"stale_links":stale,
                         "status":status})
        if status!="CURRENT":
            problems.append({"module":folder.name,
                             "missing_links":missing,"stale_links":stale})
    return {"schema":"THESIS_COMPONENT_README_CONSISTENCY_V1",
            "scope":"STATIC_CURRENT_SOURCE_NAVIGATION_NO_ENGINEERING_ACCEPTANCE",
            "packages":packages,"issues":problems,
            "packaging_status":"CURRENT" if not problems else "INCOMPLETE",
            "source_files_moved":False}


def main(argv=None):
    """[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]"""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output",type=Path)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args(argv)
    report=audit(args.root)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"module_count":len(report["packages"]),
                      "issues":report["issues"],"status":report["packaging_status"]},
                     indent=2))
    return 2 if args.check and report["issues"] else 0


if __name__=="__main__":
    raise SystemExit(main())
