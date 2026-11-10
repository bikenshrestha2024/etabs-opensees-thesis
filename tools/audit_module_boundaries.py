"""Read-only repository-wide Python module/domain/duplicate audit.

Use: python tools/audit_module_boundaries.py --out D:/ThesisAudits/module_audit
No ETABS/OpenSeesPy required; never moves, imports, executes or deletes model code.
Git blob IDs are exact-content identifiers, NOT semantic redundancy evidence.
"""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ACTIVE_PREFIXES=("components/","src/","tools/","tests/")
ARCHIVE_PREFIXES=("Saved_Project_","archive/","Worked_Example_",
                  "Verification_","Research_Components/")
FORBIDDEN_ENGINE_IMPORTS=("comtypes","win32com","etabs",
                          "src.etabs_adapter","OpenSees_Project_Inputs_V123")

def tracked_paths(root=ROOT):
    result=subprocess.run(["git","ls-files","-z"],cwd=root,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError("git ls-files failed: "+result.stderr.decode(errors="replace"))
    return [x.decode("utf-8") for x in result.stdout.split(b"\0") if x]

def domain_for(path):
    p=path.replace("\\","/")
    if p.startswith(("src/thesis_core/","src/opensees_engine/")):
        return "OPENSEES_INDEPENDENT_CORE"
    if p.startswith(("01_ETABS/","src/etabs_adapter/")):
        return "ETABS_ONLY"
    if p.startswith(("02_OPENSEES/","components/modal/","components/response_spectrum/",
                     "components/nonlinear_time_history/","components/sections/",
                     "components/shared/")):
        return "OPENSEES_ANALYSIS"
    if p.startswith(("03_INTEGRATION/","components/inputs/","components/gravity/",
                     "components/equivalent_static/","components/validation/")):
        return "ETABS_OPENSEES_INTEGRATION"
    if p=="components/model/assembly.py":
        return "MIXED_SOURCE_ASSEMBLY_MIGRATION_REQUIRED"
    if p.startswith("components/model/"):
        return "OPENSEES_MODEL_PREPARATION"
    if p.startswith(("components/ui/","04_PYTHON/","tools/","tests/")):
        return "PYTHON_TOOLING_OR_TESTS"
    if p.startswith(ARCHIVE_PREFIXES):
        return "HISTORICAL_OR_SOURCE_COPY"
    if p.endswith(".py") and "/" not in p:
        return "ROOT_COMPAT_LAUNCHER_OR_TOOL"
    return "OTHER"

def inspect_python(file,relative):
    report={"path":relative,"domain":domain_for(relative),
            "parse_status":"PARSED","imports":[],"symbols":[],
            "forbidden_imports":[],"sha256":None}
    content=file.read_bytes()
    report["sha256"]=hashlib.sha256(content).hexdigest()
    try:
        tree=ast.parse(content.decode("utf-8-sig"),filename=relative)
    except (SyntaxError,UnicodeError) as exc:
        report["parse_status"]="SYNTAX_OR_ENCODING_ERROR"
        report["error"]=str(exc)
        return report
    names=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node,ast.ImportFrom):
            names.append("."*node.level+(node.module or ""))
    report["imports"]=sorted(set(names))
    report["symbols"]=sorted(set(node.name for node in tree.body
                                  if isinstance(node,(ast.FunctionDef,
                                                      ast.AsyncFunctionDef,
                                                      ast.ClassDef))))
    if report["domain"]=="OPENSEES_INDEPENDENT_CORE":
        report["forbidden_imports"]=[
            n for n in report["imports"] if n.lower().lstrip(".").startswith(
                tuple(prefix.lower() for prefix in FORBIDDEN_ENGINE_IMPORTS))]
    return report

def audit(root=ROOT):
    root=Path(root).resolve()
    tracked=tracked_paths(root)
    active=[p for p in tracked if p.endswith(".py") and (
        p.startswith(ACTIVE_PREFIXES) or "/" not in p)]
    reports=[]
    content_groups=defaultdict(list)
    for path in active:
        file=root/path
        if not file.is_file():
            raise FileNotFoundError("Tracked file missing: "+path)
        report=inspect_python(file,path)
        reports.append(report)
        content_groups[report["sha256"]].append(path)
    dup=[sorted(group) for group in content_groups.values() if len(group)>1]
    dup.sort(key=lambda x:(-len(x),x))
    blockers=[{"path":r["path"],"imports":r["forbidden_imports"]}
              for r in reports if r["forbidden_imports"]]
    failures=[{"path":r["path"],"error":r.get("error")}
              for r in reports if r["parse_status"]!="PARSED"]
    return {"schema":"source-boundary-audit-v1",
            "scope":"STATIC_ANALYSIS_ONLY_NO_SOLVER_EXECUTION",
            "active_python_files":len(reports),"modules":reports,
            "duplicate_content_groups_active":dup,
            "forbidden_independent_core_imports":blockers,
            "parse_failures":failures,
            "historical_copies_not_deleted":True,
            "note":"Exact hashes do not prove equivalent scientific roles; old snapshots intentionally retained"}

def save_audit(report,out):
    out=Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    (out/"MODULE_BOUNDARY_AUDIT.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    with (out/"MODULE_OWNERS.csv").open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.writer(f)
        writer.writerow(["Path","Domain","SHA256","Parse status",
                         "Imports","Top-level symbols","Forbidden import"])
        for r in report["modules"]:
            writer.writerow([r["path"],r["domain"],r["sha256"],
                             r["parse_status"],";".join(r["imports"]),
                             ";".join(r["symbols"]),";".join(r["forbidden_imports"])])
    lines=["# Static module boundary audit","",
           "Source files inspected: "+str(report["active_python_files"]),
           "Exact active duplicate groups: "+str(len(report["duplicate_content_groups_active"])),
           "Prohibited core imports: "+str(len(report["forbidden_independent_core_imports"])),
           "Parse failures: "+str(len(report["parse_failures"])),"",
           "No code was moved, deleted or executed. Native ETABS/OpenSees validation NOT RUN."]
    (out/"READ_FIRST.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return out

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    report=audit()
    save_audit(report,args.out)
    print("STATIC AUDIT:",report["active_python_files"],"files",
          "forbidden imports:",len(report["forbidden_independent_core_imports"]),
          "parse failures:",len(report["parse_failures"]))
    if report["forbidden_independent_core_imports"] or report["parse_failures"]:
        raise SystemExit(2)
