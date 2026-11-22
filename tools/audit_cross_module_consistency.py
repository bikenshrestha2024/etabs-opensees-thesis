"""Cross-module source consistency, duplicate-code and reference audit.

[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]
Static-only: parses active Python once; does not import app modules, execute
ETABS/OpenSees, relocate old files, or assert engineering compliance.
AST clone groups are *review candidates*, not automatic delete instructions.
"""
from __future__ import annotations

import argparse
import ast
import copy
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

_REPO=Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0,str(_REPO))

from tools.audit_live_output_writers import source_files,scan_source
from tools.audit_module_boundaries import domain_for

MODULE_FAMILIES={
    "components/inputs/":"SOURCE_INPUTS",
    "components/model/":"MODEL",
    "components/gravity/":"GRAVITY",
    "components/equivalent_static/":"ESM",
    "components/modal/":"MODAL",
    "components/response_spectrum/":"MRSM",
    "components/linear_time_history/":"LTHA",
    "components/nonlinear_time_history/":"NLTHA",
    "components/nbc105/":"NBC105",
    "components/sections/":"SECTIONS",
    "components/validation/":"VALIDATION",
    "components/ui/":"GUI",
    "components/shared/":"SHARED",
    "tools/":"TOOLING",
    "src/":"CORE_OR_ADAPTER",
}
_SOURCE_VERSION=re.compile(
    r"(?i)NBC105_2025_95m_12m_MODEL_ALIGNED_V10[_\-]([0-9]+)")

def owner(relative):
    """[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]"""
    return next((name for prefix,name in MODULE_FAMILIES.items()
                 if relative.startswith(prefix)),"ROOT_ENTRYPOINT")


def _symbol_scope(tree, relative):
    """Record real Python shadowing, including methods inside each class."""
    conflicts=[]
    nodes=[(relative,tree.body)]
    for node in ast.walk(tree):
        if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
            nodes.append((relative+":"+str(getattr(node,"lineno",0))+
                          ":"+node.name,node.body))
    for scope,statements in nodes:
        defs=defaultdict(list)
        for node in statements:
            if isinstance(node,(ast.ClassDef,ast.FunctionDef,
                                ast.AsyncFunctionDef)):
                defs[node.name].append(node.lineno)
        for name,lines in sorted(defs.items()):
            if len(lines)>1:
                conflicts.append({
                    "source":relative,"scope":scope,"symbol":name,
                    "lines":lines,"finding":"SHADOWED_DEFINITION_REVIEW"})
    return conflicts


def _normalized_function(node):
    """Stable identical function BODY fingerprint, ignoring name and docstring.

    Argument and code statements stay unchanged to avoid claiming merely
    similar expressions are identical. Large functions only (>=25 AST nodes).
    """
    fresh=copy.deepcopy(node)
    fresh.name="_function_candidate"
    if (fresh.body and isinstance(fresh.body[0],ast.Expr)
            and isinstance(fresh.body[0].value,ast.Constant)
            and isinstance(fresh.body[0].value.value,str)):
        fresh.body=fresh.body[1:]
    count=sum(1 for line in ast.walk(fresh))
    if count<25 or not fresh.body:
        return None
    return hashlib.sha256(ast.dump(fresh,include_attributes=False).encode()).hexdigest()


def _interlinks(tree, relative):
    from_owner=owner(relative)
    links=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            names=[alias.name for alias in node.names]
        elif isinstance(node,ast.ImportFrom):
            names=[node.module] if node.level==0 and node.module else []
        else:
            continue
        for name in names:
            if not name or not name.startswith("components."):
                continue
            parts=name.split(".")
            if len(parts)<2:
                continue
            to_owner=owner("components/"+parts[1]+"/")
            links.add((from_owner,to_owner))
    return links


def scan_consistency(root):
    """[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]"""
    root=Path(root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    shadowed=[]
    clones=defaultdict(list)
    versions=[]
    edges=Counter()
    owners=Counter()
    errors=[]
    n=0
    for path in source_files(root):
        rel=path.relative_to(root).as_posix()
        n+=1
        owners[owner(rel)]+=1
        try:
            code=path.read_text(encoding="utf-8-sig")
            tree=ast.parse(code,filename=rel)
        except (UnicodeError,OSError,SyntaxError) as exc:
            errors.append({"source":rel,"type":type(exc).__name__,
                           "line":getattr(exc,"lineno",None)})
            continue
        shadowed.extend(_symbol_scope(tree,rel))
        for frm,to in _interlinks(tree,rel):
            edges[(frm,to)]+=1
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                fingerprint=_normalized_function(node)
                if fingerprint:
                    clones[fingerprint].append({
                        "source":rel,"function":node.name,"line":node.lineno})
            elif isinstance(node,ast.Constant) and isinstance(node.value,str):
                for match in _SOURCE_VERSION.finditer(node.value):
                    versions.append({
                        "source":rel,"line":node.lineno,
                        "version":"V10_"+match.group(1),
                        "status":("HISTORICAL_VERSION_REFERENCE_REVIEW"
                                  if int(match.group(1))<7
                                  else "VERSION_LITERAL_REQUIRES_SOURCE_HASH")})
    # Reuse the canonical writer/reader detector rather than maintaining a
    # competing list of path markers or file I/O methods.
    writers=scan_source(root)
    clone_groups=[{"fingerprint":digest,"occurrences":sorted(rows,
                  key=lambda x:(x["source"],x["line"]))}
                  for digest,rows in clones.items()
                  if len({x["source"] for x in rows})>1]
    clone_groups.sort(key=lambda x:(-len(x["occurrences"]),x["fingerprint"]))
    links=[{"from_owner":src,"to_owner":dst,"source_files_with_import":count}
           for (src,dst),count in sorted(edges.items())]
    return {
        "schema":"THESIS_ACTIVE_MODULE_INTEGRATION_AUDIT_V1",
        "scope":"STATIC_AST_NO_NATIVE_SOLVER_NO_MODEL_APPROVAL",
        "active_sources_scanned":n,"owner_counts":dict(sorted(owners.items())),
        "shadowed_definitions":shadowed,
        "cross_file_exact_body_clone_candidates":clone_groups,
        "versioned_workbook_literal_review":versions,
        "module_owner_import_links":links,
        "writer_reader_totals":writers["totals"],
        "parse_errors":errors+writers["parse_errors"],
        "acceptance":"OPEN_UNTIL_SEMANTIC_AND_NATIVE_ENGINEERING_REVIEW",
        "historical_files_mutated":False,
    }


def _write_csv(path,fields,rows):
    with path.open("w",newline="",encoding="utf-8-sig") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        for item in rows:
            writer.writerow({k:(json.dumps(item[k],ensure_ascii=False)
                               if isinstance(item.get(k),(list,dict))
                               else item.get(k,"")) for k in fields})


def save(report,directory):
    """[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]"""
    target=Path(directory).expanduser()
    target.mkdir(parents=True,exist_ok=True)
    (target/"01_ALL_MODULE_CONSISTENCY.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    _write_csv(target/"02_SHADOWED_DEFINITIONS.csv",
               ("source","scope","symbol","lines","finding"),
               report["shadowed_definitions"])
    clone_rows=[dict(fingerprint=group["fingerprint"],**item)
                for group in report["cross_file_exact_body_clone_candidates"]
                for item in group["occurrences"]]
    _write_csv(target/"03_DUPLICATE_FUNCTION_CANDIDATES.csv",
               ("fingerprint","source","function","line"),clone_rows)
    _write_csv(target/"04_INTERMODULE_IMPORTS.csv",
               ("from_owner","to_owner","source_files_with_import"),
               report["module_owner_import_links"])
    _write_csv(target/"05_WORKBOOK_VERSION_REFERENCES.csv",
               ("source","line","version","status"),
               report["versioned_workbook_literal_review"])
    return target


def main(argv=None):
    """[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]"""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=Path,default=_REPO)
    parser.add_argument("--report-dir",type=Path)
    parser.add_argument("--fail-on-parse",action="store_true")
    parser.add_argument("--fail-on-shadowed",action="store_true")
    args=parser.parse_args(argv)
    result=scan_consistency(args.repo)
    if args.report_dir:
        save(result,args.report_dir)
    print(json.dumps({
        "active_sources_scanned":result["active_sources_scanned"],
        "owner_counts":result["owner_counts"],
        "shadowed_definition_count":len(result["shadowed_definitions"]),
        "cross_file_clone_group_count":len(
            result["cross_file_exact_body_clone_candidates"]),
        "versioned_workbook_literals":len(result["versioned_workbook_literal_review"]),
        "owner_links":len(result["module_owner_import_links"]),
        "parse_error_count":len(result["parse_errors"]),
        "acceptance":result["acceptance"],
    },indent=2))
    return 2 if ((args.fail_on_parse and result["parse_errors"])
                 or (args.fail_on_shadowed and result["shadowed_definitions"])) else 0


if __name__=="__main__":
    raise SystemExit(main())
