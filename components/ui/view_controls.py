"""Shared 3D orientation, camera controls and unscaled physical node readouts."""
import math
VIEWS={'Isometric':(27.5,45.),'Top (+Z)':(90.,-90.),'Bottom (-Z)':(-90.,-90.),'Front (-Y)':(0.,-90.),'Back (+Y)':(0.,90.),'Right (+X)':(0.,0.),'Left (-X)':(0.,180.)}


def apply_view(axis,name='Isometric'):
    elev,azim=VIEWS[name];axis.view_init(elev=elev,azim=azim)
    if hasattr(axis,'set_proj_type'):axis.set_proj_type('ortho')


def camera_controls(parent,axis,canvas):
    import tkinter as tk
    from tkinter import ttk
    row=ttk.Frame(parent);row.pack(fill='x');choice=tk.StringVar(value='Isometric')
    ttk.Label(row,text='3D view').pack(side='left');box=ttk.Combobox(row,textvariable=choice,values=list(VIEWS),state='readonly',width=22);box.pack(side='left')
    def change(*unused):apply_view(axis,choice.get());canvas.draw_idle()
    box.bind('<<ComboboxSelected>>',change);ttk.Button(row,text='Reset isometric',command=lambda:(choice.set('Isometric'),change())).pack(side='left');apply_view(axis);return choice


def node_readout(tag,values,coordinates=None,scope='Unscaled physical response'):
    names=['Ux','Uy','Uz','Rx','Ry','Rz'];parts=[]
    for i,name in enumerate(names):
        v=values[i] if i<len(values) else None
        parts.append(name+'='+('N/A (not recorded)' if v is None else f'{float(v):.7g} '+('m' if i<3 else 'rad')))
    xyz=' | deformed XYZ=('+', '.join(f'{float(v):.7g}' for v in coordinates[:3])+') m' if coordinates is not None else ''
    return 'Node '+str(tag)+' | '+' | '.join(parts)+xyz+'\n'+scope


def resolve_node_tag(kind,ident,point_map):
    """Return string OpenSees tag; never leak integer ETABS mappings into string-key dictionaries.
    [REF docs/source/components/ui/view_controls.py.md]
    """
    key=str(ident).strip()
    if kind=="ETABS point":
        node=point_map.get(key)
        return str(node) if node is not None else ""
    return key


def center_camera_on_node(axis,point,*,home=None,span_fraction=0.10,min_span_m=1.0):
    """Focus all three world axes around node; preserve 3D view orientation.

    A selected base node should remain visible even when 25 storeys
    extend far above it. The selected-node focus is a camera operation
    only; it never moves or merges any structural node.
    [REF docs/source/components/ui/view_controls.py.md]
    """
    coords=[float(x) for x in point[:3]]
    if any(not math.isfinite(x) for x in coords):
        raise ValueError("Node coordinates are not finite")
    if not 0<span_fraction<=1:
        raise ValueError("span_fraction must be in (0,1]")
    if home is None:
        home=(axis.get_xlim(),axis.get_ylim(),axis.get_zlim())
    original=[abs(float(pair[1])-float(pair[0])) for pair in home]
    # Comparable world-space extent in X,Y,Z avoids losing a selected node
    # under the entire high-rise model and preserves its apparent depth.
    span=max(float(min_span_m),max(original)*span_fraction)
    for coordinate,setter in zip(coords,(axis.set_xlim,axis.set_ylim,axis.set_zlim)):
        setter(coordinate-span/2,coordinate+span/2)
    if hasattr(axis,"set_box_aspect"):
        axis.set_box_aspect((1,1,1))
    return span


def node_selection_artists(axis,point,*,span_m=1.0,label=None):
    """Highly visible marker, crosshair and label on top of wireframe.

    Returns artists so selection can be cleared before a redraw.
    [REF docs/source/components/ui/view_controls.py.md]
    """
    import numpy as np
    point=np.asarray(point,dtype=float)
    if point.shape!=(3,) or not np.isfinite(point).all():
        raise ValueError("Node marker requires a finite xyz triple")
    span=max(.25,float(span_m))
    radius=max(.035,span*.045)
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    cross=Line3DCollection(
        [[point-np.eye(3)[i]*radius,point+np.eye(3)[i]*radius]
         for i in range(3)],colors="#ff008c",linewidths=5)
    axis.add_collection3d(cross,autolim=False)
    dot=axis.scatter([point[0]],[point[1]],[point[2]],
                     c="#ffde00",edgecolors="#b60072",
                     s=160,linewidths=2.3,depthshade=False)
    # A fixed screen-space label remains legible even when the selected
    # physical node is behind a shell surface or dense wall mesh.
    label_text="NODE "+str(label) if label is not None else "SELECTED NODE"
    overlay=axis.text2D(.02,.97,label_text,transform=axis.transAxes,
                       fontsize=12,fontweight="bold",color="#890051",
                       va="top",bbox=dict(boxstyle="round,pad=.35",
                       facecolor="#fff1a8",edgecolor="#b60072",linewidth=1.5))
    return [cross,dot,overlay]


def remove_selection_artists(artists):
    """Remove previous selected-node marker before drawing the next.

    [REF docs/source/components/ui/view_controls.py.md]
    """
    for artist in artists:
        try:artist.remove()
        except (ValueError,AttributeError):pass
