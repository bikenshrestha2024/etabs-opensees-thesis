"""Labelled wall-index (Aw) source for the modal and ESM windows.

[REF R10 NBC105-2025 §5.1.2 (Aw = sum Awi[0.2 + (Lwi/H)^2], Lwi/H <= 0.9)]
[REF docs/review/20261106_THESIS_EXCEL_METHOD_DECISION_REGISTER.md (original Excel Aw/opening method is authoritative)]

The modal audit and ESM forms showed blank Aw whenever no source-verified
SCALING SUMMARY workbook for the *same* EDB existed, even after the user had
run the ETABS-linked original Excel method or the OpenSees geometry sync.
This module returns, in order of authority:

1. ORIGINAL_EXCEL_METHOD_ETABS_LINKED: the newest ``*_ETABS_LINKED_ESM.provenance.json``
   in the state's analysis folder whose source EDB is the export's source EDB
   (same path or same SHA256), whose condition matches the limit state, and
   whose direct ETABS thickness check did not fail.
2. OpenSees geometry candidate from ``opensees_nbc_sync._source_snapshot``
   (read-only), with its own evidence status, e.g.
   PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC. Never NBC acceptance.
Nothing is written or modified; values carry a label the GUI must display.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

LINKED_PATTERN = '*_ETABS_LINKED_ESM.provenance.json'
CONDITION_STATE = {'ultimate': 'ULS', 'service': 'SLS'}
GEOMETRY_STATUSES = ('OPEN_SEES_GEOMETRY_CANDIDATE_REVIEW_REQUIRED',
                     'PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC',
                     'SOURCE_MATCHED_GROUPED_WALL_AREA_REVIEW_REQUIRED')


def _positive(value):
    try:
        x = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return x if math.isfinite(x) and x > 0 else None


def _norm(path):
    return str(path or '').replace('\\', '/').casefold().strip()


def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def edb_identity(current_edb, audit):
    """SAME_EDB_PATH / BYTE_IDENTICAL_EDB / DIFFERENT_EDB / UNKNOWN_CURRENT_EDB.

    [REF components/inputs/project_workbooks.py _same_edb_file_content]
    A matching file name after dropping '- Copy' is NOT accepted.
    """
    if not current_edb:
        return 'UNKNOWN_CURRENT_EDB'
    if _norm(current_edb) == _norm(audit.get('source_edb')):
        if Path(str(current_edb)).is_file() and audit.get('source_edb_sha256'):
            if _sha256(current_edb)!=audit['source_edb_sha256']:
                return 'DIFFERENT_EDB'
        return 'SAME_EDB_PATH'
    path = Path(str(current_edb))
    if audit.get('source_edb_sha256') and path.is_file():
        try:
            if _sha256(path) == audit['source_edb_sha256']:
                return 'BYTE_IDENTICAL_EDB'
        except OSError:
            pass
    return 'DIFFERENT_EDB'


def linked_reference_from_audit(audit, audit_path, *, state, current_edb):
    """Convert an ETABS-linked provenance JSON into the ESM ``excel_direct_reference`` shape.

    [REF components/equivalent_static/etabs_linked_excel.py run_etabs_excel]
    Raises ValueError for a limit-state mismatch, invalid Aw/T or a failed
    direct-thickness check.
    """
    state = str(state).strip().upper()
    coeff = audit.get('coefficients') or {}
    values, cells, conditions = {}, {}, set()
    for axis in ('X', 'Y'):
        c = coeff.get(axis) or {}
        aw, t1 = _positive(c.get('Aw_m2')), _positive(c.get('T1_s'))
        if aw is None or t1 is None:
            raise ValueError(f'ETABS-linked audit has no valid Aw/T for {axis}: {audit_path}')
        values['aw' + axis.lower()] = aw
        values['workbook_adopted_t' + axis.lower()] = t1
        cells['aw' + axis.lower()] = 'NBC Calculator (ETABS-linked original method)'
        conditions.add(CONDITION_STATE.get(str(c.get('condition', '')).strip().casefold()))
    if conditions != {state}:
        raise ValueError(f'ETABS-linked workbook condition {sorted(map(str, conditions))} '
                         f'does not match {state}: {audit_path}')
    thickness = audit.get('direct_thickness_check') or {}
    if thickness.get('status') == 'MISMATCH':
        raise ValueError('ETABS-linked Excel wall thickness differs from the direct ETABS '
                         'PropArea.GetWall thickness; do not use this Aw: '
                         + '; '.join(map(str, thickness.get('mismatches', [])[:5])))
    identity = edb_identity(current_edb, audit)
    return dict(
        values=values, cells=cells,
        source_workbook=str(audit.get('output_excel', '')),
        source_sheet='NBC Calculator', workbook_source_edb=str(audit.get('source_edb', '')),
        current_export_source_edb=current_edb or None,
        source_identity={'SAME_EDB_PATH': 'SAME_EDB_PATH_REFERENCE',
                         'BYTE_IDENTICAL_EDB': 'BYTE_IDENTICAL_EDB_REFERENCE'}.get(
                             identity, 'DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY'),
        limit_state=state, code_accepted=False,
        method='ORIGINAL_EXCEL_METHOD_ETABS_LINKED',
        provenance_json=str(audit_path),
        direct_thickness_status=thickness.get('status', 'NOT_RECORDED'),
        notice=('Original Excel method populated from ETABS (read-only). Aw and the '
                'workbook adopted T are research references, not NBC acceptance; '
                'review wall piers/openings under §5.1.2.'),
        workbook_sha256=str(audit.get('output_excel_sha256', '')))


def latest_linked_reference(export_dir, state, *, search_dirs=()):
    """Newest acceptable ETABS-linked reference for this export/state, or (None, reason).

    [REF NBC105-2025 §5.1.2; Excel method decision register] Only SAME or
    BYTE_IDENTICAL EDB identity is returned for automatic filling.
    """
    from components.inputs.project_workbooks import _source_edb_path, analysis_output_folder, registered_project_source
    dirs = [analysis_output_folder(export_dir, state), *map(Path, search_dirs)]
    found = []
    registered=registered_project_source(export_dir,'etabs_linked_audit')
    if registered:found.append(Path(registered))
    for d in dirs:
        if Path(d).is_dir():
            found += list(Path(d).glob(LINKED_PATTERN)) + list(Path(d).glob('*/' + LINKED_PATTERN))
    if not found:
        return None, 'No ETABS-linked original Excel run found for ' + str(state)
    current = _source_edb_path(export_dir)
    reasons = []
    for path in sorted(set(found), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            audit = json.loads(path.read_text(encoding='utf-8-sig'))
            ref = linked_reference_from_audit(audit, path, state=state, current_edb=current)
        except (OSError, ValueError) as exc:
            reasons.append(f'{path.name}: {exc}')
            continue
        if ref['source_identity'] == 'DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY':
            reasons.append(f'{path.name}: source EDB {ref["workbook_source_edb"]} is not the '
                           f'export source EDB {current or "(not recorded)"}')
            continue
        return ref, 'OK'
    return None, ' | '.join(reasons[:3])


def resolve_aw(export_dir, state):
    """Best labelled Aw for each axis: {'X':..,'Y':..,'method':..,'labels':{..},'reference':..}.

    [REF NBC105-2025 §5.1.2; components/inputs/opensees_nbc_sync.py]
    Returns values None for axes without an acceptable source.
    """
    state = 'ULS' if str(state).strip().upper() == 'BOTH' else str(state).strip().upper()
    out = dict(X=None, Y=None, method=None, labels={}, reference=None, notes=[], state=state)

    # This thesis's 2x12m structural-wall decision takes precedence over the
    # OLD 4x6m Excel value only when current first-storey exported shell/node
    # geometry passes all source-linked dimensional checks. No EDB or XLSX
    # bytes are altered, and native ETABS equivalence is not asserted.
    try:
        from components.inputs.opensees_nbc_sync import _source_snapshot
        snapshot = _source_snapshot(export_dir, state)
    except Exception as exc:
        snapshot = None
        out['notes'].append('12m wall grouping verification unavailable: ' + str(exc))
    if snapshot is not None:
        reviewed = snapshot.get('grouped_wall_aw_review') or {}
        if reviewed.get('status') == 'EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY':
            previous, why = latest_linked_reference(export_dir, state)
            out.update(X=_positive(reviewed['aw_candidate_m2'].get('X')),
                       Y=_positive(reviewed['aw_candidate_m2'].get('Y')),
                       method='EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY',
                       reference=previous, code_accepted=False,
                       assembled_model_sha256=snapshot.get('assembled_model_sha256'),
                       source_edb_sha256=reviewed.get('source_edb_sha256'),
                       evidence=snapshot['aw_evidence'])
            out['labels'] = {
                'X': 'REVIEWED PROJECT GROUPING: 2 connected 12m X walls; export node geometry matched',
                'Y': 'REVIEWED PROJECT GROUPING: 3 solid 6m Y walls; export node geometry matched'}
            if previous:
                prior = previous.get('values') or {}
                out['historical_workbook_aw_m2'] = {
                    'X': prior.get('awx'), 'Y': prior.get('awy')}
                out['notes'].append(
                    'Prior original Excel Aw retained as historical comparison. '
                    'If calculated using 4x6m panels it is superseded for THIS '
                    'project geometry; original workbook NOT modified.')
            out['notes'].append(
                'UBC 1997 and SEAOC support net minimum area with full '
                'connected-wall length. Native ETABS validation and code '
                'acceptance remain separate.')
            return out
    ref, reason = latest_linked_reference(export_dir, state)
    if ref:
        out.update(X=ref['values']['awx'], Y=ref['values']['awy'],
                   method=ref['method'], reference=ref)
        for axis in ('X', 'Y'):
            out['labels'][axis] = ('ORIGINAL EXCEL METHOD (ETABS-linked, ' + ref['source_identity']
                                   + '; thickness ' + ref['direct_thickness_status'] + ')')
        return out
    out['notes'].append(reason)
    try:
        from components.inputs.opensees_nbc_sync import _source_snapshot
        snap = _source_snapshot(export_dir, state)
    except Exception as exc:  # report, never guess
        out['notes'].append('OpenSees geometry candidate unavailable: ' + str(exc))
        return out
    for axis in ('X', 'Y'):
        status = snap['aw_evidence'][axis]['status']
        value = _positive(snap['aw_candidate_m2'].get(axis))
        if value is not None and status in GEOMETRY_STATUSES:
            out[axis] = value
            out['labels'][axis] = status.replace('_', ' ') + ' (OpenSees geometry; not NBC accepted)'
        else:
            out['labels'][axis] = 'not filled: ' + status
    out['method'] = ('SOURCE_MATCHED_GROUPED_WALL_AREA_REVIEW_REQUIRED'
                     if any(out['labels'].get(axis, '').startswith(
                         'SOURCE MATCHED GROUPED WALL AREA') for axis in ('X','Y'))
                     else 'OPEN_SEES_GEOMETRY_CANDIDATE')
    out['evidence'] = snap['aw_evidence']
    out['assembled_model_sha256'] = snap['assembled_model_sha256']
    return out
