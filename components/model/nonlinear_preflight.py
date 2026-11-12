"""Dependency inventory, never automatic approval of physical calibration."""
from pathlib import Path
import json,hashlib,importlib.util,datetime

def inventory(folder):
    folder=Path(folder).resolve();name='OpenSees_Complete_Model_Config_V118.json'
    path=folder/name;cfg=json.loads(path.read_text(encoding='utf-8-sig')) if path.is_file() else {}
    refs=['OpenSees_Complete_Model_Data_V118.json','OpenSees_Load_Conversion_Audit.json','OpenSees_Complete_Story_Masters_V118.csv',name,'OpenSees_Complete_Nonlinear_Model.py']
    files=[dict(file=n,exists=(folder/n).is_file()) for n in refs]
    # The exploratory literature cards are not equivalent to the
    # production project-specific material definition referenced below.
    # Report their separate presence instead of implying they are missing.
    repository_root = Path(__file__).resolve().parents[2]
    research_cards = sorted(
        path.name for path in (repository_root / "Material_Catalog").glob("*.json")
    ) if (repository_root / "Material_Catalog").is_dir() else []
    internal_research_implementation = (
        repository_root / "components" / "nonlinear_time_history"
        / "material_source_sets.py"
    ).is_file()
    material=cfg.get('nonlinear_materials_file')
    mp=Path(material) if material else None
    if mp and not mp.is_absolute():mp=folder/mp
    missing=[x['file'] for x in files if not x['exists']]
    if not mp or not mp.is_file():missing.append('Project nonlinear material definitions file')
    if not cfg.get('nonlinear_wall_fsam_tags'):missing.append('Project wall property-to-FSAM region tags')
    if cfg.get('nonlinear_parameters_reviewed') is not True:missing.append('Reviewed project reinforcement, confinement and cyclic parameters')
    modules={n:importlib.util.find_spec(n) is not None for n in ['openseespy','numpy','scipy','threadpoolctl','openpyxl','matplotlib']}
    return dict(
        created_at=datetime.datetime.now().astimezone().isoformat(),
        folder=str(folder), files=files, python_dependencies=modules,
        material_file=str(mp) if mp else None,
        production_material_status=(
            "CONFIGURED_EXTERNAL_FILE_EXISTS" if mp and mp.is_file()
            else "CONFIGURED_EXTERNAL_FILE_NOT_FOUND" if mp
            else "NOT_CONFIGURED_EXTERNAL_FILE"
        ),
        research_material_sources=dict(
            research_cards_found=len(research_cards),
            catalog_filenames=research_cards,
            material_source_sets_module_present=internal_research_implementation,
            assessment="REFERENCE_ONLY_NOT_PROJECT_CALIBRATION",
        ),
        wall_fsam_mappings=cfg.get('nonlinear_wall_fsam_tags',{}),
        blockers=missing, approval=False,
        scope='Dependency discovery only. Literature material cards may exist in the repository while no external project material file is configured. No project reinforcement, wall tag mapping, or calibration approval is inferred.',
        next_steps=[
            'Select exact OpenSees_Complete_Nonlinear_Model.py in the model-bound dashboard and record its SHA256.',
            'Inspect literature catalog/source sets separately; do not copy specimen values as approved project definitions.',
            'Provide actual frame bar layout, wall reinforcement/regions and source material definitions; update only reviewed project configuration.',
            'Run applicable member/wall cyclic comparisons, initial modal audit, gravity and signed P-Delta checks.',
            'Rebind changed model as an UNAPPROVED draft, inspect evidence, and only then save review claims.'
        ])

def launch(parent,folder):
    import tkinter as tk
    from tkinter import ttk
    report=inventory(folder);win=tk.Toplevel(parent);win.title('Nonlinear dependency preflight - available files and missing project inputs');win.geometry('1000x650')
    from tkinter.scrolledtext import ScrolledText
    box=ScrolledText(win,wrap='word');box.pack(fill='both',expand=True);box.insert('end',json.dumps(report,indent=2))
    def save():
        out=Path(folder)/'OpenSees_Analysis_Results'/'Nonlinear_Dependency_Preflight_V160.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2),encoding='utf8')
    ttk.Button(win,text='Save dependency inventory (does not approve model)',command=save).pack(anchor='w')
    return win
