"""Reproducible inventory and source-symbol discovery; NOT a semantic-review certificate.

Run within a Git checkout. Does not import or execute thesis modules, use ETABS,
read untracked files, or publish engineering data. Outputs are case-local.
"""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone

PYTHON_ROOTS = ("components/", "src/", "tools/", "ai/", "Research_Components/")
ARCHIVE_ROOTS = ("archive/", "Saved_Project_", "Worked_Example_", "Verification_",
                 "Regression_Trial_", "Recovered_1s_Trial_")
DERIVED_SUFFIXES = {".json", ".jsonl", ".csv", ".log", ".xlsx", ".png",
                    ".gif", ".html", ".at2", ".coords"}


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args],
                            check=True, capture_output=True)
    return result.stdout


def classify(path):
    p = path.replace("\\", "/")
    if p.startswith(("tests/", ".github/")):
        return "REGRESSION_AND_CI"
    if p.startswith(ARCHIVE_ROOTS):
        return "HISTORICAL_PROVENANCE"
    if p.startswith(PYTHON_ROOTS):
        return "ACTIVE_OR_RESEARCH_SOURCE"
    if "/" not in p and p.endswith((".py", ".bat")):
        return "ACTIVE_LAUNCHER_OR_COMPATIBILITY"
    if p.startswith(("docs/", "KNOWLEDGE_BASE/", "LITERATURE/", "REVIEW_MAIN/")):
        return "DOCUMENTATION_AND_LITERATURE"
    if Path(p).suffix.lower() in DERIVED_SUFFIXES:
        return "MODEL_DERIVED_OR_INPUT_RECORD"
    return "UNCLASSIFIED_MANUAL_TRIAGE"


def _symbols(module, file_sha256):
    rows = []
    class Walker(ast.NodeVisitor):
        def __init__(self): self.stack=[]
        def visit_ClassDef(self, node):
            rows.append({
                "symbol":".".join(self.stack+[node.name]),
                "kind":"class", "start_line":node.lineno,
                "end_line":node.end_lineno, "sha256_file":file_sha256,
                "review_status":"DISCOVERED_NOT_SEMANTICALLY_REVIEWED",
                "reviewer":"", "caller_contract":"", "test_evidence":""
            })
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()
        def visit_FunctionDef(self, node): self._func(node, "function")
        def visit_AsyncFunctionDef(self, node): self._func(node, "async_function")
        def _func(self, node, kind):
            name=".".join(self.stack+[node.name])
            rows.append({
                "symbol": name, "kind": kind,
                "start_line": node.lineno, "end_line": node.end_lineno,
                "sha256_file": file_sha256,
                "review_status": "DISCOVERED_NOT_SEMANTICALLY_REVIEWED",
                "reviewer": "", "caller_contract": "", "test_evidence": ""
            })
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()
    Walker().visit(module)
    return rows


def _risks(tree):
    flags = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            n = node.func
            label = n.id if isinstance(n, ast.Name) else (
                n.attr if isinstance(n, ast.Attribute) else "")
            if label in ("eval", "exec", "Popen", "run", "check_call",
                         "system", "__import__", "import_module", "loads"):
                if label == "loads":
                    continue
                flags.append((node.lineno, label))
        elif isinstance(node, ast.Import):
            for n in node.names:
                if n.name in ("ctypes", "comtypes", "win32com"):
                    flags.append((node.lineno, "NATIVE_API_IMPORT"))
    return flags


def collect(root):
    root=Path(root).resolve()
    if not (root / ".git").exists():
        raise ValueError("Repository root must be a Git checkout")
    head=git(root, "rev-parse", "HEAD").decode().strip()
    raw=git(root, "ls-files", "-s", "-z").split(b"\0")
    files=[]; symbols=[]; edges=[]; duplicate=defaultdict(list)
    failures=[]; patterns=[]; by_category=Counter()
    for entry in raw:
        if not entry: continue
        stat, rel=entry.split(b"\t", 1)
        mode, blob, stage=stat.decode().split()
        path=rel.decode("utf-8", "surrogateescape")
        category=classify(path)
        by_category[category]+=1
        duplicate[blob].append(path)
        full=root / path
        file_record={"path":path,"git_blob_sha1":blob,"git_mode":mode,
                     "category":category,"is_python":path.endswith(".py"),
                     "exists":full.exists() or full.is_symlink(),
                     "semantic_status":"NOT_REVIEWED"}
        files.append(file_record)
        if not path.endswith(".py") or full.is_symlink() or not full.is_file():
            continue
        try:
            source=full.read_bytes()
            digest=hashlib.sha256(source).hexdigest()
            tree=ast.parse(source, filename=path)
            file_record["sha256"]=digest
            records=_symbols(tree,digest)
            for item in records: symbols.append({"path":path,**item})
            for n in ast.walk(tree):
                if isinstance(n,ast.Import):
                    for alias in n.names:
                        edges.append((path,alias.name,False,n.lineno))
                elif isinstance(n,ast.ImportFrom):
                    edges.append((path,"."*n.level+(n.module or ""),True,n.lineno))
            for line,pattern in _risks(tree):
                patterns.append({"path":path,"line":line,"pattern":pattern,
                                 "status":"CANDIDATE_NEEDS_MANUAL_REVIEW"})
        except (SyntaxError, UnicodeError, OSError, ValueError) as exc:
            failures.append({"path":path,"type":type(exc).__name__,
                             "line":getattr(exc,"lineno",None)})
    duplicate_groups=[{"sha1":sha,"count":len(items),"sample":items[:5]}
                      for sha,items in duplicate.items() if len(items)>1]
    duplicates_by_category=Counter()
    for g in duplicate_groups:
        duplicates_by_category["groups"]+=1
        duplicates_by_category["extra_files"]+=g["count"]-1
    return {
        "head":head,"schema":"TRACKED_TREE_DISCOVERY_V1",
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "tracked_files":len(files),
        "categories":dict(sorted(by_category.items())),
        "python_files":sum(f["is_python"] for f in files),
        "symbols_discovered":len(symbols),
        "ast_issues":failures,
        "duplicate_blob_groups":duplicate_groups,
        "duplicate_counts":dict(duplicates_by_category),
        "files":files, "symbols":symbols,
        "import_edges":edges, "risk_patterns":patterns,
        "acceptance":{
            "S1_DISCOVERY":"COMPLETED_AT_PINNED_HEAD",
            "S2_COMPLETE_SEMANTIC_REVIEW":"NOT_VERIFIED",
            "S3_DEPENDENCY_RUNTIME_VALIDATION":"NOT_VERIFIED",
            "S4_OUTPUT_CONTRACT":"NOT_VERIFIED",
            "S5_NATIVE_WINDOWS_REGRESSION":"NOT_RUN",
            "S6_ETABS_OPENSEES_EQUIVALENCE":"NOT_VERIFIED",
            "S7_FULL_NLTHA":"NOT_VERIFIED"
        }
    }


def write_report(result, out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    def save_csv(name, columns, rows):
        with (out/name).open("w", newline="", encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
            writer.writeheader();writer.writerows(rows)
    save_csv("TRACKED_INVENTORY.csv",
             ["path","git_blob_sha1","git_mode","category","is_python","exists","sha256","semantic_status"],
             result["files"])
    save_csv("SYMBOL_DISCOVERY_NOT_REVIEWED.csv",
             ["path","symbol","kind","start_line","end_line","sha256_file",
              "review_status","reviewer","caller_contract","test_evidence"],
             result["symbols"])
    save_csv("IMPORT_EDGES.csv",["source","imported","relative","line"],
             [dict(zip(["source","imported","relative","line"],r))
              for r in result["import_edges"]])
    save_csv("SUSPICIOUS_PATTERN_QUEUE.csv",
             ["path","line","pattern","status"],result["risk_patterns"])
    summary={k:v for k,v in result.items() if k not in (
        "files","symbols","import_edges","risk_patterns","duplicate_blob_groups")}
    summary["duplicate_blob_examples"]=result["duplicate_blob_groups"][:25]
    (out/"DISCOVERY_SUMMARY.json").write_text(json.dumps(
        summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# Repository source discovery — not a semantic certificate","",
           "HEAD: `"+result["head"]+"`","",
           f"- Tracked files: {result['tracked_files']:,}",
           f"- Python files: {result['python_files']:,}",
           f"- Discovered Python symbols: {result['symbols_discovered']:,}",
           f"- Python parse issues: {len(result['ast_issues'])}",
           f"- Duplicate Git blob groups: {len(result['duplicate_blob_groups'])}",
           "",
           "## Acceptance boundaries", "",
           "S1 source discovery completed. All symbols in the CSV are explicitly "
           "DISCOVERED_NOT_SEMANTICALLY_REVIEWED. Automated AST discovery is "
           "not a function-by-function semantic audit. Native ETABS/OpenSees "
           "checks are not executed.", "", "## Classification"]
    lines += [f"- {k}: {v}" for k,v in result["categories"].items()]
    (out/"READ_ME_FIRST.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=".")
    p.add_argument("--out",default="AUDIT_RUNS/semantic_discovery")
    args=p.parse_args()
    result=collect(args.root)
    out=write_report(result,args.out)
    summary={"head":result["head"],"output":str(out),
             "tracked_files":result["tracked_files"],
             "python_files":result["python_files"],
             "symbols":result["symbols_discovered"],
             "ast_errors":len(result["ast_issues"]),
             "duplicate_blob_groups":len(result["duplicate_blob_groups"]),
             "risk_pattern_queue":len(result["risk_patterns"]),
             "semantic_review_verified":False}
    print(json.dumps(summary,indent=2))
    return 2 if result["ast_issues"] else 0


if __name__=="__main__":
    raise SystemExit(main())
