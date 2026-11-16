"""Regression for source geometry trace batching and untouched model inputs."""
import unittest
from plotly import graph_objects as go
from components.ui.source_view_compaction import (
    compact_connectivity_figure, compact_load_figure)


class TestSourceViewCompaction(unittest.TestCase):
    def test_connectivity_preserves_exact_objects_and_reduces_traces(self):
        fig=go.Figure()
        source=[]
        for i in range(12):
            fig.add_trace(go.Scatter3d(
                x=[float(i),float(i+1)],y=[0.,0.],z=[3.8,3.8],
                mode="lines",line=dict(color="#2563eb",width=5),
                customdata=[[str(i)]]*2))
            source.append(dict(trace=i,object=str(i),element_tag=100+i,
                               category="BEAM",level=1,section="B600",
                               nodes=f"{i},{i+1}"))
        old_trace_count=len(fig.data)
        reduced,meta,groups,spot=compact_connectivity_figure(fig,source)
        self.assertEqual(old_trace_count,12)
        self.assertEqual(len(reduced.data),2)
        self.assertEqual(spot,1)
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0]["count"],12)
        self.assertEqual(len(meta),12)
        self.assertEqual(meta[7]["object"],"7")
        self.assertEqual(meta[7]["element_tag"],107)
        self.assertEqual(meta[7]["x"],[7.,8.])
        self.assertEqual(fig.data[7].x,(7.,8.))
        self.assertEqual(len(reduced.data[0].customdata),36)
        self.assertEqual(reduced.data[0].customdata[21],[7])

    def test_same_type_but_different_story_or_property_not_mixed(self):
        fig=go.Figure()
        meta=[]
        for i,(story,section) in enumerate([(1,"A"),(1,"B"),(2,"A")]):
            fig.add_trace(go.Scatter3d(
                x=[0,1],y=[i,i],z=[story,story],
                line=dict(color="#dc2626")))
            meta.append(dict(trace=i,object=str(i),category="COLUMN",
                             level=story,section=section))
        batched,_,groups,_=compact_connectivity_figure(fig,meta)
        self.assertEqual(len(groups),3)
        self.assertEqual(len(batched.data),4)

    def test_load_grouping_keeps_triangle_faces_and_exact_hover(self):
        fig=go.Figure()
        fig.add_trace(go.Scatter3d(x=[0,1],y=[0,0],z=[0,0],mode="lines"))
        metadata=[]
        for n in range(4):
            fig.add_trace(go.Mesh3d(
                x=[n,n+1,n],y=[0,0,1],z=[3,3,3],
                i=[0],j=[1],k=[2],color="#2563eb",opacity=.48,
                customdata=[[str(n),"Live",1]]*3,
                hovertemplate="Object %{customdata[0]}<extra></extra>"))
            metadata.append(dict(trace=n+1,pattern="Live",level=1,
                                 value=2.0,object=str(n)))
        batched,items=compact_load_figure(fig,metadata)
        self.assertEqual(len(batched.data),2)
        self.assertEqual(items[0]["count"],4)
        self.assertEqual(len(batched.data[1].x),12)
        self.assertEqual(list(batched.data[1].i),(0,3,6,9))
        self.assertEqual(batched.data[1].customdata[6][0],"2")
        self.assertIn("customdata[0]",batched.data[1].hovertemplate)
        self.assertEqual(len(fig.data),5)

    def test_frame_loads_batch_without_losing_arrows(self):
        fig=go.Figure()
        fig.add_trace(go.Scatter3d(x=[0,1],y=[0,0],z=[0,0]))
        meta=[]
        for i in range(6):
            fig.add_trace(go.Scatter3d(
                x=[i,i,None],y=[0,0,None],z=[2,1,None],
                mode="lines",line=dict(color="#ea580c",width=5),
                customdata=[[str(i),"Wall",1]]*3,
                hovertemplate="Frame %{customdata[0]}<extra></extra>"))
            meta.append(dict(trace=i+1,pattern="Wall",level=1,value=7.,
                             value_end=7.,object=f"FRAME:{i}"))
        out,m=compact_load_figure(fig,meta)
        self.assertEqual(len(out.data),2)
        self.assertEqual(m[0]["count"],6)
        self.assertEqual(len(out.data[1].x),24)
        self.assertEqual(out.data[1].customdata[0][0],"0")
        self.assertIsNone(out.data[1].customdata[3])
        self.assertEqual(out.data[1].customdata[4][0],"1")


if __name__ == "__main__":
    unittest.main()
