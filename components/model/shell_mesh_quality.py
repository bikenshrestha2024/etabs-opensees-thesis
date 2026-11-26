"""Shell mesh-quality audit and the opt-in wall cell-size limit validator.

[REF docs/source/components/model/shell_mesh_quality.py.md]

Geometry-only diagnostics for the conforming ShellMITC4 mesh written by
``components.model.assembly._mesh_areas``. Units: metres. The audit reads
node coordinates and four-node shell cells; it never changes the model,
loads, mass, stiffness or solver input. A small aspect ratio is not an
engineering acceptance criterion: ETABS equivalence of wall response still
requires a native OpenSees re-solve compared with ETABS reactions.

ETABS reference for the optional wall limit: ``Analysis - Wall Mesh
Settings`` (maximum wall mesh size, 1 m in the thesis source model, with
``Area Assigns - Wall Auto Mesh`` = Default for all wall objects).
"""
import bisect
import math

AUDIT_STATUS = 'DIAGNOSTIC_MESH_GEOMETRY_ONLY_NOT_ACCEPTANCE'
ASPECT_THRESHOLDS = (4, 10, 50)
_KEY_DIGITS = 6
_LINE_TOL = 1e-7


def validate_wall_max_cell_size(value):
    """Return ``None`` or a positive finite float for ``wall_max_cell_size_m``.

    [REF docs/source/components/model/shell_mesh_quality.py.md]
    ``None`` (key absent) keeps the historical wall mesh. Booleans, strings,
    NaN/inf and values <= 0 are rejected with ``ValueError``.
    """
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('wall_max_cell_size_m must be a positive number of metres '
                         '(for example 1.0) or absent; got '+repr(value))
    value = float(value)
    if not math.isfinite(value) or value <= 0.:
        raise ValueError('wall_max_cell_size_m must be a finite positive number '
                         'of metres; got '+repr(value))
    return value


def _edge_lengths(xyz):
    return [math.dist(xyz[k], xyz[(k+1) % 4]) for k in range(4)]


def _line_key(p, q):
    d = [q[k]-p[k] for k in range(3)]
    n = math.sqrt(sum(x*x for x in d))
    if n <= 1e-12:
        return None, 0., 0.
    d = [x/n for x in d]
    for x in d:
        if abs(x) > 1e-9:
            if x < 0:
                d = [-y for y in d]
            break
    tp = sum(p[k]*d[k] for k in range(3))
    tq = sum(q[k]*d[k] for k in range(3))
    foot = [p[k]-tp*d[k] for k in range(3)]
    key = tuple(round(x, _KEY_DIGITS) + 0. for x in d+foot)
    return key, tp, tq


def _hanging_nodes(nodes, shells):
    """Nodes lying strictly inside another cell edge (T-junctions).

    Edges are grouped by their supporting line (direction and foot point
    rounded to 1e-6 m); a node that is an edge endpoint on the same line and
    falls strictly between the ends of another edge is non-conforming.
    """
    lines = {}
    edges = []
    for cell in shells:
        tags = [int(n) for n in cell['nodes']]
        for k in range(4):
            a, b = tags[k], tags[(k+1) % 4]
            key, ta, tb = _line_key(nodes[a], nodes[b])
            if key is None:
                continue
            bucket = lines.setdefault(key, {})
            bucket[a] = ta
            bucket[b] = tb
            edges.append((key, min(ta, tb), max(ta, tb), a, b))
    ordered = {}
    for key, bucket in lines.items():
        pairs = sorted((t, n) for n, t in bucket.items())
        ordered[key] = ([t for t, _ in pairs], [n for _, n in pairs])
    hanging = set()
    for key, lo, hi, a, b in edges:
        ts, ns = ordered[key]
        i = bisect.bisect_right(ts, lo+_LINE_TOL)
        j = bisect.bisect_left(ts, hi-_LINE_TOL)
        for n in ns[i:j]:
            if n not in (a, b):
                hanging.add(n)
    return hanging


def audit_shell_mesh_quality(nodes, shells, *, wall_max_cell_size_m=None,
                             floor_subdivisions=None):
    """Per-category cell counts, edge lengths and aspect ratios.

    [REF docs/source/components/model/shell_mesh_quality.py.md]
    ``nodes`` maps tag -> [x, y, z] (m); ``shells`` are dicts with
    ``nodes`` (4 tags), ``category`` and optional ``area``. Aspect ratio is
    max/min cell edge length. For SHEAR WALL cells the vertical extent is the
    i->l edge and the horizontal width the i->j edge (assembly convention).
    Returns a JSON-serialisable dict; no side effects.
    """
    nodes = {int(k): [float(x) for x in v] for k, v in nodes.items()}
    categories = {}
    for cell in shells:
        xyz = [nodes[int(n)] for n in cell['nodes']]
        edges = _edge_lengths(xyz)
        lo, hi = min(edges), max(edges)
        aspect = hi/lo if lo > 0 else math.inf
        row = categories.setdefault(str(cell.get('category')), dict(
            cell_count=0, min_edge_m=math.inf, max_edge_m=0., max_aspect_ratio=0.,
            total_area_m2=0., **{f'cells_aspect_gt_{t}': 0 for t in ASPECT_THRESHOLDS},
            _widths=[], _heights=[]))
        row['cell_count'] += 1
        row['min_edge_m'] = min(row['min_edge_m'], lo)
        row['max_edge_m'] = max(row['max_edge_m'], hi)
        row['max_aspect_ratio'] = max(row['max_aspect_ratio'], aspect)
        row['total_area_m2'] += float(cell.get('area', 0.) or 0.)
        for t in ASPECT_THRESHOLDS:
            if aspect > t:
                row[f'cells_aspect_gt_{t}'] += 1
        if str(cell.get('category')) == 'SHEAR WALL':
            row['_widths'].append(edges[0])
            row['_heights'].append(edges[3])
    for name, row in categories.items():
        widths = row.pop('_widths')
        heights = row.pop('_heights')
        if widths:
            row['wall_width_min_m'] = min(widths)
            row['wall_width_max_m'] = max(widths)
            row['wall_vertical_extent_min_m'] = min(heights)
            row['wall_vertical_extent_max_m'] = max(heights)
            distinct = sorted({round(h, 4) for h in heights})
            row['wall_vertical_extent_distinct_m'] = distinct[:25]
            row['wall_vertical_extent_distinct_count'] = len(distinct)
        for key in ('min_edge_m', 'max_edge_m', 'max_aspect_ratio', 'total_area_m2'):
            if math.isfinite(row[key]):
                row[key] = round(row[key], 9)
    hanging = _hanging_nodes(nodes, shells)
    wall = categories.get('SHEAR WALL', {})
    limit_ok = None
    if wall_max_cell_size_m is not None and wall:
        limit_ok = wall['max_edge_m'] <= wall_max_cell_size_m*(1+1e-6)
    return dict(
        status=AUDIT_STATUS,
        note='Geometry diagnostic only. Aspect ratios and cell sizes do not '
             'certify ETABS equivalence or engineering acceptance; a native '
             'OpenSees gravity/modal re-solve compared with ETABS is required.',
        floor_subdivisions=floor_subdivisions,
        wall_max_cell_size_m=wall_max_cell_size_m,
        wall_mesh_rule=('HISTORICAL_COPLANAR_LINES' if wall_max_cell_size_m is None
                        else 'COPLANAR_LINES_PLUS_UNIFORM_SUBDIVISION_TO_LIMIT'),
        wall_max_cell_size_satisfied=limit_ok,
        aspect_ratio_definition='max cell edge / min cell edge',
        aspect_ratio_thresholds=list(ASPECT_THRESHOLDS),
        categories=dict(sorted(categories.items())),
        hanging_node_count=len(hanging),
        hanging_node_sample=sorted(hanging)[:20],
        hanging_node_definition='node lying strictly inside another shell '
                                'cell edge on the same line (T-junction)')
