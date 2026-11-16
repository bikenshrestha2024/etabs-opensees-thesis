"""On-demand, batched 3D visualization of the *assembled* OpenSees mesh.

[REF docs/source/components/ui/assembled_mesh_view.py.md]
Unlike ETABS source-object previews, this reads the actual assembled
ShellMITC4 quadrilaterals and frame segments from the saved V118 model.
It does not remesh, change a numerical model, or invoke ETABS/OpenSees.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

MODEL = "OpenSees_Complete_Model_Data_V118.json"
CONFIG = "OpenSees_Complete_Model_Config_V118.json"
RELATIVE_VIEW = Path("02_MODEL") / "03_3D_VIEWS" / "OpenSees_Assembled_Mesh_3D.html"


def _xyz(nodes, tag):
    point = nodes.get(str(tag))
    if not isinstance(point, (list, tuple)) or len(point) != 3:
        raise ValueError("Missing assembled node coordinate: " + str(tag))
    xyz = tuple(float(x) for x in point)
    if not all(math.isfinite(x) for x in xyz):
        raise ValueError("Nonfinite assembled node coordinate: " + str(tag))
    return xyz


def build_mesh_lines(payload):
    """[REF docs/source/components/ui/assembled_mesh_view.py.md] Build batched traces."""
    nodes = payload.get("nodes")
    shells = payload.get("shells")
    frames = payload.get("frames")
    if not isinstance(nodes, dict) or not isinstance(shells, list) or not isinstance(frames, list):
        raise ValueError("Actual assembled nodes, shells and frames are required")
    categories = {"FLOOR": [], "SHEAR WALL": [], "OTHER SHELL": [], "FRAME": []}
    seen = {name: set() for name in categories}
    for element in shells:
        corners = element.get("nodes")
        if not isinstance(corners, list) or len(corners) != 4:
            raise ValueError("Assembled shell requires exactly four nodes")
        category = str(element.get("category", "")).upper()
        kind = category if category in ("FLOOR", "SHEAR WALL") else "OTHER SHELL"
        for i in range(4):
            a, b = str(corners[i]), str(corners[(i + 1) % 4])
            # Shared cell edges are rendered once per category.
            key = tuple(sorted((a, b), key=lambda x: (len(x), x)))
            if key not in seen[kind]:
                seen[kind].add(key)
                categories[kind].append((_xyz(nodes, a), _xyz(nodes, b)))
    for element in frames:
        ends = element.get("nodes")
        if not isinstance(ends, list) or len(ends) != 2:
            raise ValueError("Assembled frame requires exactly two end nodes")
        a, b = str(ends[0]), str(ends[1])
        key = tuple(sorted((a, b), key=lambda x: (len(x), x)))
        if key not in seen["FRAME"]:
            seen["FRAME"].add(key)
            categories["FRAME"].append((_xyz(nodes, a), _xyz(nodes, b)))
    return categories


def render(export_root, *, output=None):
    """[REF docs/source/components/ui/assembled_mesh_view.py.md] Render read-only local HTML."""
    root = Path(export_root).expanduser().resolve()
    source = root / MODEL
    config = root / CONFIG
    if not source.is_file() or not config.is_file():
        raise FileNotFoundError("Assembled model and configuration are required; finish or rebuild the export first")
    if source.is_symlink() or config.is_symlink():
        raise ValueError("Linked source model/config not permitted for mesh viewer")
    payload = json.loads(source.read_text(encoding="utf-8-sig"))
    cfg = json.loads(config.read_text(encoding="utf-8-sig"))
    import hashlib
    sha = hashlib.sha256(config.read_bytes()).hexdigest()
    if payload.get("config_sha256") != sha:
        raise ValueError("Stale assembled mesh: saved config differs from model hash. Rebuild from saved export.")
    n = cfg.get("floor_subdivisions", 4)
    if type(n) is not int or n < 2 or n > 16:
        raise ValueError("floor_subdivisions must be the recorded integer 2..16")
    lines = build_mesh_lines(payload)
    from plotly import graph_objects as go
    fig = go.Figure()
    colors = {"FLOOR": "#2563eb", "SHEAR WALL": "#d97706",
              "OTHER SHELL": "#64748b", "FRAME": "#111827"}
    widths = {"FLOOR": 1.5, "SHEAR WALL": 2, "OTHER SHELL": 1.5, "FRAME": 3}
    for category, segments in lines.items():
        if not segments:
            continue
        x, y, z = [], [], []
        for a, b in segments:
            x.extend((a[0], b[0], None))
            y.extend((a[1], b[1], None))
            z.extend((a[2], b[2], None))
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode="lines", name=category,
            line=dict(color=colors[category], width=widths[category]),
            hoverinfo="skip"))
    fig.update_layout(
        title=f"Actual assembled OpenSees mesh | {n}×{n} source-panel subdivisions "
              f"| {len(payload['shells']):,} shell cells, {len(payload['frames']):,} frame segments",
        scene=dict(aspectmode="data",
                   xaxis_title="X (m)", yaxis_title="Y (m)", zaxis_title="Z (m)"),
        legend=dict(orientation="h"), margin=dict(l=0, r=0, b=0, t=95),
        annotations=[dict(text="VIEW ONLY — actual solver mesh; not ETABS validation",
                          x=0, y=1.04, xref="paper", yref="paper", showarrow=False)])
    target = (Path(output).expanduser().resolve() if output
              else root / RELATIVE_VIEW)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink() or target.parent.is_symlink():
        raise ValueError("Symlink output not permitted")
    # A single directory-local Plotly bundle is reused by other views in this folder.
    fig.write_html(str(target), include_plotlyjs="directory",
                   full_html=True, auto_open=False)
    return target


def main(argv=None):
    """[REF docs/source/components/ui/assembled_mesh_view.py.md] Local CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export_root")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    print(render(args.export_root, output=args.output))


if __name__ == "__main__":
    main()
