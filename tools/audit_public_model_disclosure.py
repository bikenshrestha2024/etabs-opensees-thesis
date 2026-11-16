"""Public tracked-file disclosure preflight (metadata only).

No content of model-derived evidence is read, copied, uploaded or printed.
This checks the current Git index, NOT full commit history or confidentiality.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess

FORBIDDEN_PUBLIC_PREFIXES=(
    "New_Export_Viewer_Diagnostic/",
    "Viewer_Preview_V141/",
)
CANDIDATE_NAMES={
    "OpenSees_Complete_Model_Data_V118.json",
    "OpenSees_Element_Connectivity.json",
    "OpenSees_Source_Model_Metadata_V118.json",
    "OpenSees_Complete_Export_Report_V118.json",
}


def tracked_paths(root):
    root=Path(root).resolve()
    r=subprocess.run(["git","-C",str(root),"ls-files","-z"],
                     check=True,capture_output=True)
    return sorted(x.decode("utf-8","surrogateescape")
                  for x in r.stdout.split(b"\0") if x)


def review(paths):
    paths=tuple(paths)
    forbidden=sorted(p for p in paths
                     if p.startswith(FORBIDDEN_PUBLIC_PREFIXES))
    other_candidates=sorted(p for p in paths
                            if Path(p).name in CANDIDATE_NAMES
                            and p not in forbidden)
    return {
        "schema":"PUBLIC_MODEL_DISCLOSURE_PATH_REVIEW_V1",
        "status":"BLOCKED_CURRENT_PUBLIC_TRACKING" if forbidden else
                 "NO_FORBIDDEN_VIEWER_FILES_IN_CURRENT_INDEX",
        "forbidden_paths":forbidden,
        "other_model_candidates_need_manual_review":other_candidates,
        "history_review_required":True,
        "content_review_performed":False,
        "native_model_verified":False,
        "warning":"Path-level classification cannot determine confidentiality. "
                  "Older Git commits and GitHub forks may retain past files.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",default=".")
    p.add_argument("--output",default=None)
    args=p.parse_args()
    result=review(tracked_paths(args.repo))
    if args.output:
        path=Path(args.output)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],
        "forbidden_path_count":len(result["forbidden_paths"]),
        "other_model_candidates":len(result["other_model_candidates_need_manual_review"]),
        "history_review_required":True,
    }))
    return 2 if result["forbidden_paths"] else 0


if __name__=="__main__":
    raise SystemExit(main())
