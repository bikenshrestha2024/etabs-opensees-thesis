"""[REF docs/source/components/gravity/output_ownership.py.md]
One physical owner for newly generated gravity reports, indexes and reviews.

A source export owns one 02_GRAVITY stage. A case workspace is either the
automatic stage RUNS/<model> or an explicitly selected external workspace.
These helpers never move/rename historic results or claim solver equivalence.
"""
from __future__ import annotations
from pathlib import Path
import re

SECTIONS = {
    "INDEXES": "00_INDEXES",
    "LOGS": "01_LOGS",
    "SOLVER": "02_RESULTS",
    "EXCEL": "03_EXCEL",
    "FIGURES": "04_FIGURES",
    "COMPARISONS": "05_COMPARISONS",
    "REVIEWS": "06_REVIEW",
    "UPLOADS": "07_EXPORT_ZIP",
}
SCENARIOS = (
    "ETABS_NONZERO_REACTION_DIAGNOSTIC",
    "ETABS_SOURCE_SUPPORTS",
    "CONTINUOUS_WALL_BASE_FIXED",
)


def _unlinked(path):
    """Reject redirects that could escape source-owned directories."""
    path=Path(path).expanduser()
    if any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError("Refusing symlinked gravity destination: "+str(path))
    return path.resolve()


def section(root, kind, *, create=False):
    """[REF docs/source/components/gravity/output_ownership.py.md]
    Stage-local section path; no mkdir unless explicitly requested."""
    path=_unlinked(root)
    if kind not in SECTIONS:
        raise ValueError("Unknown gravity output class: "+str(kind))
    dest=path/SECTIONS[kind]
    if create:
        _unlinked(dest).mkdir(parents=True,exist_ok=True)
    return dest


def model_workspace(model_path, *, selected=None):
    """[REF docs/source/components/gravity/output_ownership.py.md] Choose the gravity workspace for a model."""
    from components.inputs.output_layout import export_root_for, owned_run_destination

    model = _unlinked(model_path)
    root = export_root_for(model.parent)
    variants = root / '02_MODEL' / 'REBUILDS' / 'VERIFIED_CLEAR_BEAM'
    label = model.stem
    if model.parent.parent == variants:
        label += '__' + model.parent.name
    return owned_run_destination(model.parent, 'GRAVITY', label, selected=selected)


def rebuild_source_folder(model_path):
    """[REF docs/source/components/gravity/output_ownership.py.md] Recover the source of a bound rebuild."""
    import json
    from components.inputs.output_layout import export_root_for

    source = _unlinked(model_path).parent
    root = export_root_for(source)
    if source == root and not source.name.casefold().startswith('verified_clear_beam_'):
        return root
    variants = root / '02_MODEL' / 'REBUILDS' / 'VERIFIED_CLEAR_BEAM'
    status = source / 'CLEAR_BEAM_REBUILD_STATUS.json'
    if source.parent == variants and status.is_file() and not status.is_symlink():
        evidence = json.loads(status.read_text(encoding='utf-8-sig'))
        original = evidence.get('original_source_dir') if isinstance(evidence,dict) else None
        if (original and evidence.get('status') == 'EXPORT_VERIFIED_NOT_GRAVITY_SOLVED'
                and _unlinked(original) == root):
            return root
    raise ValueError('Select the original ETABS export or a saved rebuild with matching source provenance.')


def case_directory(root, scenario, profile, token, *, create=False):
    """[REF docs/source/components/gravity/output_ownership.py.md]
    Return an immutable run folder; never overwrite a previous run."""
    from components.inputs.output_contract import safe_component
    if scenario not in SCENARIOS:
        raise ValueError("Invalid gravity support strategy")
    name=safe_component(profile)
    run=safe_component(token)
    dest=section(root,"SOLVER")/scenario/name/run
    if create:
        _unlinked(dest).mkdir(parents=True,exist_ok=False)
    return dest


def workspace_for_solver_case_run(run_directory):
    """[REF docs/source/components/gravity/output_ownership.py.md]
    Recover one immutable case's output workspace, never current GUI state.

    Case path: <workspace>/02_RESULTS/<scenario>/<profile>/<run-id>.
    This prevents late UI folder switching from registering a result into a
    foreign model's index. Historical irregular folders must use the explicit
    workspace captured at launch, not a guessed ancestor.
    """
    path=_unlinked(run_directory)
    base=path.parents[2]
    if (base.name!=SECTIONS["SOLVER"] or
            path.parents[1].name not in SCENARIOS):
        raise ValueError("Not a canonical 32/76/97 gravity solver case path: "+
                         str(path))
    return path.parents[3]


def workspace_for_dual_case_run(dual_run_folder):
    """[REF docs/source/components/gravity/output_ownership.py.md]
    Read true owner of an immutable 76/97 batch case, not current GUI path.
    """
    path=_unlinked(dual_run_folder)
    if (path.parent.name!="Gravity_Wall_Base_Comparison" or
            path.parents[1].name!=SECTIONS["COMPARISONS"]):
        raise ValueError("Not a canonical 76/97 dual gravity run path: "+str(path))
    return path.parents[2]


def index_path(root, name, *, create=False):
    """[REF docs/source/components/gravity/output_ownership.py.md]
    Index lives with indexes, not mixed with solver workbooks/plots."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+",str(name)):
        raise ValueError("Unsafe gravity index filename")
    return section(root,"INDEXES",create=create)/name


def existing_index(root, name):
    """[REF docs/source/components/gravity/output_ownership.py.md]
    Read canonical first; preserve historical flat-index compatibility."""
    canonical=index_path(root,name)
    return canonical if canonical.is_file() else _unlinked(root)/name


def dual_runs_parent(root, *, create=False):
    """[REF docs/source/components/gravity/output_ownership.py.md]
    Canonical owner for a gravity artifact family."""
    return section(root,"COMPARISONS",create=create)/"Gravity_Wall_Base_Comparison"


def diagnostic_parent(root, *, create=False):
    """[REF docs/source/components/gravity/output_ownership.py.md]
    Canonical owner for a gravity artifact family."""
    return section(root,"REVIEWS",create=create)/"Gravity_Reaction_Diagnostic"


def uploads_parent(root, *, create=False):
    """[REF docs/source/components/gravity/output_ownership.py.md]
    Canonical owner for a gravity artifact family."""
    return section(root,"UPLOADS",create=create)/"Gravity_Evidence_Upload"
