"""Refresh already-exported Plotly source views without ETABS or model assembly.

[REF docs/source/components/ui/saved_view_refresh.py.md]
Only HTML/CSS/JavaScript presentation is modified. Original source JSON/CSV,
FE mesh, model config, restraints and numerical calculation files stay untouched.
Legacy trace-heavy HTML keeps its original trace count: the refresh is for UI,
not a replacement for generating new batched figures.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

VIEW_FILES = (
    "OpenSees_Structural_Elements_By_Storey.html",
    "OpenSees_Element_Connectivity_3D.html",
    "OpenSees_Load_Assignment_3D.html",
    "OpenSees_Load_Assignment_Floor_Plan.html",
)
LOAD_FILES = frozenset(VIEW_FILES[2:])
STYLE_ID = "saved-load-view-style-v171"
SCRIPT_ID = "saved-load-view-script-v171"
MARKER = "SAVED_VIEW_PREFS_V171"
STYLE = r"""<style id="saved-load-view-style-v171">
#shared-id-controls-v122.load-view-collapsed{position:sticky!important;top:0!important;z-index:35!important;min-height:38px!important;padding:0 10px!important}
#shared-id-controls-v122.load-view-collapsed .viewer-main,
#shared-id-controls-v122.load-view-collapsed .viewer-advanced,
#shared-id-controls-v122.load-view-collapsed .viewer-status{display:none!important}
#shared-id-controls-v122 #toggle-shared-inspector-v171{
 cursor:pointer;display:inline-block;padding:7px 10px;margin:4px 0;
 border:1px solid #b7c5d8;border-radius:6px;color:#17385b;background:#e8effa;
 font:600 12px system-ui,Segoe UI,sans-serif
}
#shared-id-controls-v122 #toggle-shared-inspector-v171:focus-visible{outline:3px solid #2762b3}
#load-pattern-legend-v171{display:flex;gap:6px;align-items:center;flex-wrap:wrap;
 max-width:100%;padding:7px 12px;margin:4px 12px;border:1px solid #e2e8f0;
 border-radius:8px;background:#f8fafc;font:12px system-ui,Segoe UI,sans-serif}
#load-pattern-legend-v171 .pattern-token{display:inline-flex;align-items:center;gap:5px;
 border:1px solid #e2e8f0;padding:4px 7px;border-radius:5px;background:#fff}
#load-pattern-legend-v171 .pattern-color{width:10px;height:10px;border-radius:2px;display:inline-block}
@media(max-width:620px){#load-pattern-legend-v171{margin:4px;gap:3px}}
</style>"""
SCRIPT = r"""<script id="saved-load-view-script-v171">
(function(){
"use strict";
const MARKER="SAVED_VIEW_PREFS_V171";
const filename=__FILE__;
function init(){
 const gd=document.querySelector(".plotly-graph-div");
 if(!gd || !Array.isArray(gd.data)){return;}
 const shared=document.getElementById("shared-id-controls-v122");
 if(shared){
   let toggle=document.getElementById("toggle-shared-inspector-v171");
   if(!toggle){
     toggle=document.createElement("button");
     toggle.id="toggle-shared-inspector-v171";toggle.type="button";
     toggle.setAttribute("aria-controls","shared-id-controls-v122");
     shared.prepend(toggle);
   }
   const updateLabel=()=>{
     const closed=shared.classList.contains("load-view-collapsed");
     toggle.textContent=closed?"Show element inspector / exact IDs":"Hide element inspector";
     toggle.setAttribute("aria-expanded",String(!closed));
   };
   shared.classList.add("load-view-collapsed");
   toggle.addEventListener("click",()=>{shared.classList.toggle("load-view-collapsed");updateLabel();});
   updateLabel();
 }
 const loadView=filename.indexOf("Load_Assignment")>=0;
 if(!loadView){return;}
 // User can always select All storeys. Initially show just the highest
 // explicitly exported storey to prevent displaying 25 stacked load layers.
 const storey=document.getElementById("storyFilter");
 if(storey){
   const options=[...storey.options].filter(o=>o.value!=="all"&&o.value!=="");
   const numeric=options.filter(o=>Number.isFinite(Number(o.value)));
   const first=numeric.sort((a,b)=>Number(b.value)-Number(a.value))[0]||options[0];
   if(first){storey.value=first.value;storey.dispatchEvent(new Event("change",{bubbles:true}));}
 }
 // The custom legend presents one swatch per actual load pattern.
 // Existing Plotly trace geometry, per-object hover and filtering remain intact.
 const patterns=new Map();
 for(const trace of gd.data){
   const label=String(trace.name||"");
   if(label==="Frame skeleton"||label==="Storey elevation grid"||label==="Supports")continue;
   const pattern=label.split("|")[0].replace(/ UDL arrows$/,"").trim();
   if(!pattern || /highlight|selected element/i.test(pattern))continue;
   if(!patterns.has(pattern)){
     let color=(trace.line&&trace.line.color)||trace.fillcolor||trace.color||"#64748b";
     if(typeof color!=="string" || !/^#[0-9a-fA-F]{3,8}$/.test(color))color="#64748b";
     patterns.set(pattern,color);
   }
 }
 if(patterns.size && !document.getElementById("load-pattern-legend-v171")){
   const panel=document.createElement("div");
   panel.id="load-pattern-legend-v171";
   panel.setAttribute("aria-label","One legend item per load pattern");
   const heading=document.createElement("strong");
   heading.textContent="Load patterns:";
   panel.appendChild(heading);
   for(const [name,color] of patterns){
     const token=document.createElement("span");token.className="pattern-token";
     const swatch=document.createElement("span");swatch.className="pattern-color";
     swatch.style.backgroundColor=color;
     const label=document.createElement("span");label.textContent=name;
     token.append(swatch,label);panel.appendChild(token);
   }
   gd.parentElement.insertBefore(panel,gd);
 }
 if(typeof Plotly!=="undefined" && patterns.size){
   Plotly.relayout(gd,{showlegend:false}).catch(()=>{});
 }
}
if(document.readyState==="complete"){init();}
else{window.addEventListener("load",init,{once:true});}
})();
</script>"""


def enhance_saved_html(content: str, name: str) -> str:
    """[REF docs/source/components/ui/saved_view_refresh.py.md] Idempotent load UI."""
    if name not in VIEW_FILES:
        raise ValueError("Not an approved ETABS source view: " + name)
    if "plotly-graph-div" not in content:
        raise ValueError("View lacks a Plotly graph marker: " + name)
    if name not in LOAD_FILES:
        return content  # Structural and exact-ID connection pages retain full inspector.
    if not re.search(r"</body\s*>", content, flags=re.I):
        raise ValueError("View has no closing body tag: " + name)
    without = re.sub(
        rf'<style id="{STYLE_ID}">.*?</style>', "", content, flags=re.S)
    without = re.sub(
        rf'<script id="{SCRIPT_ID}">.*?</script>', "", without, flags=re.S)
    payload = STYLE + SCRIPT.replace("__FILE__", json.dumps(name))
    # Inject after any existing selector script, without altering Plotly data.
    return re.sub(r"</body\s*>", lambda _: payload + "</body>",
                  without, count=1, flags=re.I)


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def refresh_saved_views(root: str | Path) -> dict:
    """[REF docs/source/components/ui/saved_view_refresh.py.md] Atomic offline refresh.

    A private backup of all four existing HTML bytes is taken before writing.
    Missing source audit files or incomplete export folders fail closed.
    """
    folder = Path(root).expanduser().resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(str(folder))
    # A source audit is necessary to prevent arbitrary HTML patching.
    source = folder / "OpenSees_Element_Connectivity.json"
    if not source.is_file() or source.is_symlink():
        raise FileNotFoundError("Expected ETABS source connectivity JSON not found")
    report = folder / "OpenSees_Complete_Export_Report_V118.json"
    if not report.is_file() or report.is_symlink():
        raise FileNotFoundError("Completed OpenSees export report not found")
    completed = json.loads(report.read_text(encoding="utf-8-sig"))
    if not isinstance(completed, dict) or completed.get("assembly_errors") != []:
        raise ValueError("Do not refresh unverified/incomplete conversion output")
    changes = {}
    for name in VIEW_FILES:
        path = folder / name
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError("Required source view missing: " + str(path))
        old = path.read_bytes()
        revised = enhance_saved_html(old.decode("utf-8-sig"), name).encode("utf-8")
        changes[name] = (old, revised)
    if not any(old != new for old, new in changes.values()):
        return {"status": "UNCHANGED", "files": len(changes),
                "model_unchanged": True}
    diagnostics = folder / "09_SOFTWARE_DIAGNOSTICS" / "VIEW_REFRESH_BACKUP"
    if diagnostics.is_symlink():
        raise ValueError("Backup directory must not be a symbolic link")
    backup = diagnostics / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup.mkdir(parents=True, exist_ok=False)
    manifest = []
    for name,(old,new) in changes.items():
        (backup / name).write_bytes(old)
        manifest.append(dict(name=name, original_sha256=_hash(old),
                             new_sha256=_hash(new), changed=(old != new)))
    (backup / "VIEW_REFRESH_MANIFEST.json").write_text(json.dumps(
        {"scope":"HTML_PRESENTATION_ONLY", "entries":manifest,
         "source_connectivity_sha256":_hash(source.read_bytes()),
         "complete_export_report_sha256":_hash(report.read_bytes()),
         "no_etabs_or_opensees_solver_run":True},
         indent=2), encoding="utf-8")
    written = []
    try:
        for name,(old,new) in changes.items():
            if old == new:continue
            path=folder/name
            with tempfile.NamedTemporaryFile(dir=folder, prefix=".view-refresh-",
                                             suffix=".html", delete=False) as tmp:
                tmp.write(new)
                tmp_name=Path(tmp.name)
            try:
                os.replace(tmp_name,path)
            finally:
                tmp_name.unlink(missing_ok=True)
            written.append(name)
    except Exception:
        for name in written:
            (folder/name).write_bytes(changes[name][0])
        raise
    return {"status":"HTML_UPDATED", "files":len(changes),
            "changed":written, "backup":str(backup),
            "model_unchanged":True,
            "note":"Does not re-batch legacy Plotly traces; fresh exports use latest batching"}


def main(argv=None):
    """[REF docs/source/components/ui/saved_view_refresh.py.md] Standalone CLI."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export_folder",help="Completed ETABS-to-OpenSees export root")
    args=parser.parse_args(argv)
    print(json.dumps(refresh_saved_views(args.export_folder),indent=2))


if __name__=="__main__":
    main()
