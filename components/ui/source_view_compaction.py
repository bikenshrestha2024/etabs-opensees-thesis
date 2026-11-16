"""Fast source *display* figures; no OpenSees model or element modification.

[REF docs/source/components/ui/source_view_compaction.py.md]
The original inspectors create a Plotly trace per ETABS source object/triangle.
Batching source geometries at the same level/category/property dramatically
reduces browser trace count while retaining an indexed per-object spotlight.
"""
from __future__ import annotations

from collections import OrderedDict

def _tolist(values):
    """[REF docs/source/components/ui/source_view_compaction.py.md] Normalize Plotly arrays."""
    return list(values) if values is not None else []


def compact_connectivity_figure(fig, metadata):
    """[REF docs/source/components/ui/source_view_compaction.py.md] Batch by level/category/property.

    Returns a new Plotly Figure, object metadata containing exact original
    coordinates, group metadata and spotlight trace index. Does not mutate
    source coordinates or structural connectivity.
    """
    from plotly import graph_objects as go
    grouped = OrderedDict()
    objects = []
    for item in metadata:
        trace = fig.data[int(item["trace"])]
        xs, ys, zs = (_tolist(getattr(trace, axis, None))
                      for axis in ("x", "y", "z"))
        if not (len(xs) == len(ys) == len(zs)):
            raise ValueError("Connectivity trace coordinate lengths do not match")
        if not xs:
            raise ValueError("Connectivity item has no geometry: " + str(item["object"]))
        entry = {key: value for key, value in item.items() if key != "trace"}
        entry.update(x=xs, y=ys, z=zs)
        index = len(objects)
        objects.append(entry)
        key = (entry["category"], int(entry["level"]),
               entry.get("section") or "UNASSIGNED")
        group = grouped.setdefault(key, dict(x=[], y=[], z=[], customdata=[],
                                             count=0, color=trace.line.color))
        group["x"].extend(xs + [None])
        group["y"].extend(ys + [None])
        group["z"].extend(zs + [None])
        group["customdata"].extend([[index] if value is not None else None
                                    for value in xs] + [None])
        group["count"] += 1

    reduced = go.Figure(layout=fig.layout)
    group_meta = []
    for (category, level, section), data in grouped.items():
        idx = len(reduced.data)
        reduced.add_trace(go.Scatter3d(
            x=data["x"], y=data["y"], z=data["z"],
            customdata=data["customdata"], mode="lines",
            name=f"{category} | Story {level} | {section}",
            line=dict(color=data["color"] or "#64748b", width=3),
            showlegend=False,
            hovertemplate="Element index: %{customdata[0]}<extra></extra>"))
        group_meta.append(dict(trace=idx, category=category, level=level,
                               section=section, count=data["count"]))
    spotlight = len(reduced.data)
    reduced.add_trace(go.Scatter3d(
        x=[], y=[], z=[], mode="lines+markers", name="Selected element",
        line=dict(color="#f43f5e", width=10),
        marker=dict(color="#f43f5e", size=5),
        showlegend=False, hoverinfo="skip", visible=False))
    return reduced, objects, group_meta, spotlight


def compact_load_figure(fig, metadata):
    """[REF docs/source/components/ui/source_view_compaction.py.md] Group load geometry.

    Each original load triangle and line segment is preserved geometrically.
    Only visual Plotly trace boundaries are changed, not engineering loads.
    Groups match the existing story/pattern/value filters exactly.
    """
    from plotly import graph_objects as go
    grouped = OrderedDict()
    original = list(fig.data)
    if not original:
        raise ValueError("No frame-skeleton trace available")
    out = go.Figure(layout=fig.layout)
    out.add_trace(original[0])
    for item in metadata:
        trace = original[int(item["trace"])]
        kind = "surface" if trace.type == "mesh3d" else "line"
        start = float(item["value"])
        end = float(item.get("value_end", start))
        key = (kind, str(item["pattern"]), int(item["level"]), start, end)
        group = grouped.setdefault(key, dict(x=[], y=[], z=[],
                                             i=[], j=[], k=[], count=0,
                                             template=trace))
        xyz = [_tolist(getattr(trace, axis, None)) for axis in ("x", "y", "z")]
        if not (len(xyz[0]) == len(xyz[1]) == len(xyz[2])):
            raise ValueError("Load figure coordinate arrays differ")
        if kind == "surface":
            base = len(group["x"])
            group["x"].extend(xyz[0])
            group["y"].extend(xyz[1])
            group["z"].extend(xyz[2])
            group["i"].extend(base + int(v) for v in trace.i)
            group["j"].extend(base + int(v) for v in trace.j)
            group["k"].extend(base + int(v) for v in trace.k)
        else:
            for axis, coords in zip(("x", "y", "z"), xyz):
                group[axis].extend(coords + [None])
        group["count"] += 1
    new_meta = []
    legend_patterns = set()
    for (kind, pattern, level, start, end), d in grouped.items():
        idx = len(out.data)
        name = f"{pattern} | Storey {level}"
        if kind == "surface":
            out.add_trace(go.Mesh3d(
                x=d["x"], y=d["y"], z=d["z"], i=d["i"], j=d["j"], k=d["k"],
                color=d["template"].color, opacity=d["template"].opacity,
                name=name, legendgroup=pattern, showlegend=pattern not in legend_patterns,
                hovertemplate=f"Pattern: {pattern}<br>Storey: {level}<extra></extra>"))
        else:
            out.add_trace(go.Scatter3d(
                x=d["x"], y=d["y"], z=d["z"], mode="lines",
                line=d["template"].line, name=name,
                legendgroup=pattern, showlegend=pattern not in legend_patterns,
                hovertemplate=f"Pattern: {pattern}<br>Storey: {level}<extra></extra>"))
        legend_patterns.add(pattern)
        new_meta.append(dict(trace=idx, pattern=pattern, level=level,
                             value=start, value_end=end, count=d["count"],
                             object="FRAME:BATCH" if kind == "line" else "AREA:BATCH"))
    return out, new_meta
