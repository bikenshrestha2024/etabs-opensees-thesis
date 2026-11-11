"""No-network regression tests for Git LFS workbook input recovery."""
import hashlib
import json
from pathlib import Path
import sys
import types

import pytest
from components.inputs.lfs_workbook_recovery import (
    is_lfs_pointer, recover_lfs_pointer, ensure_gui_workbooks)


def _sha(content):
    return hashlib.sha256(content).hexdigest()


def _setup(tmp_path):
    runtime=tmp_path/"repo"
    (runtime/"excel"/"source").mkdir(parents=True)
    workbook=runtime/"excel"/"source"/"big.xlsx"
    workbook.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 12\n")
    original=tmp_path/"original.xlsx"
    data=b"PK\\x03\\x04ORIGINAL_TEST_XLSX_BYTES"
    original.write_bytes(data)
    edb=tmp_path/"selected.EDB"
    edb.write_bytes(b"mock-EDB")
    registry={"schema":"project-sources-v1","source_edb_sha256":_sha(edb.read_bytes()),
              "sources":{"etabs_full_table":{"path":"source/big.xlsx","sha256":_sha(data)}}}
    (runtime/"excel"/"SOURCE_REGISTRY.json").write_text(json.dumps(registry))
    return runtime,edb,original,workbook


def test_archive_without_git_uses_dialog_and_private_override(tmp_path,monkeypatch):
    runtime,edb,original,pointer=_setup(tmp_path)
    alerts=[]
    tk=types.ModuleType("tkinter")
    tk.filedialog=types.SimpleNamespace(askopenfilename=lambda **k: str(original))
    tk.messagebox=types.SimpleNamespace(showwarning=lambda *a,**k: alerts.append(a))
    monkeypatch.setitem(sys.modules,"tkinter",tk)
    out=tmp_path/"export"
    logs=[]
    ensure_gui_workbooks(runtime,out,edb,parent=None,log=logs.append)
    assert is_lfs_pointer(pointer)  # No overwriting tracked pointer or source
    private=json.loads((out/"project_sources.private.json").read_text())
    assert Path(private["sources"]["etabs_full_table"]["path"])==original
    assert private["sources"]["etabs_full_table"]["sha256"]==_sha(original.read_bytes())
    assert len(alerts)==1
    assert any("ARCHIVE_WITHOUT_GIT_METADATA" in x for x in logs)


def test_wrong_selected_excel_is_rejected_without_registration(tmp_path,monkeypatch):
    runtime,edb,original,pointer=_setup(tmp_path)
    original.write_bytes(b"another workbook")
    tk=types.ModuleType("tkinter")
    tk.filedialog=types.SimpleNamespace(askopenfilename=lambda **k: str(original))
    tk.messagebox=types.SimpleNamespace(showwarning=lambda *a,**k:None)
    monkeypatch.setitem(sys.modules,"tkinter",tk)
    out=tmp_path/"export"
    with pytest.raises(ValueError,match="SHA256"):
        ensure_gui_workbooks(runtime,out,edb,parent=None)
    assert not (out/"project_sources.private.json").exists()
    assert is_lfs_pointer(pointer)


def test_cancelled_dialog_does_not_fake_success(tmp_path,monkeypatch):
    runtime,edb,original,pointer=_setup(tmp_path)
    tk=types.ModuleType("tkinter")
    tk.filedialog=types.SimpleNamespace(askopenfilename=lambda **k:"")
    tk.messagebox=types.SimpleNamespace(showwarning=lambda *a,**k:None)
    monkeypatch.setitem(sys.modules,"tkinter",tk)
    with pytest.raises(FileNotFoundError,match="not selected"):
        ensure_gui_workbooks(runtime,tmp_path/"export",edb,parent=None)


def test_valid_normal_workbook_never_invokes_git(tmp_path,monkeypatch):
    runtime,edb,original,pointer=_setup(tmp_path)
    registry=runtime/"excel"/"SOURCE_REGISTRY.json"
    d=json.loads(registry.read_text())
    pointer.write_bytes(original.read_bytes())
    registry.write_text(json.dumps(d))
    tk=types.ModuleType("tkinter")
    tk.filedialog=types.SimpleNamespace(
        askopenfilename=lambda **k: (_ for _ in ()).throw(AssertionError("unexpected dialog")))
    tk.messagebox=types.SimpleNamespace(
        showwarning=lambda *a,**k: (_ for _ in ()).throw(AssertionError("unexpected warning")))
    monkeypatch.setitem(sys.modules,"tkinter",tk)
    ensure_gui_workbooks(runtime,tmp_path/"export",edb,parent=None)


def test_no_git_does_not_try_network_for_pointer(tmp_path):
    runtime,edb,original,pointer=_setup(tmp_path)
    ok,reason=recover_lfs_pointer(pointer,expected_sha256=_sha(original.read_bytes()))
    assert not ok and reason=="ARCHIVE_WITHOUT_GIT_METADATA"


def test_downstream_registry_pointer_prompts_and_remembers_original(tmp_path,monkeypatch):
    """Manifest may only exist after conversion starts: picker still works."""
    from components.inputs.project_workbooks import registered_project_source
    runtime,edb,original,pointer=_setup(tmp_path)
    export=tmp_path/"export"
    export.mkdir()
    (export/"OpenSees_Element_Connectivity.json").write_text(
        json.dumps({"source_edb": str(edb)}))
    # The resolver's repository registry lives under its own module root.
    # Override the file-based lookup by invoking in a copied isolated
    # version of the resolver's code with a controlled module path.
    import components.inputs.project_workbooks as pw
    class FakeFile:
        def __init__(self,path): self._path=path
        def resolve(self): return self._path
    monkeypatch.setattr(pw,"__file__",str(runtime/"components"/"inputs"/"project_workbooks.py"))
    tk=types.ModuleType("tkinter")
    tk._default_root=object()
    picks=[]
    tk.filedialog=types.SimpleNamespace(askopenfilename=lambda **kw: (
        picks.append(kw),str(original))[1])
    tk.messagebox=types.SimpleNamespace(showwarning=lambda *a,**k:None)
    monkeypatch.setitem(sys.modules,"tkinter",tk)
    got=registered_project_source(export,"etabs_full_table")
    assert got==str(original.resolve())
    assert len(picks)==1
    private=json.loads((export/"project_sources.private.json").read_text())
    assert private["sources"]["etabs_full_table"]["sha256"]==_sha(original.read_bytes())
    # The second attempt must pick the stored full-size original, no dialog.
    got2=registered_project_source(export,"etabs_full_table")
    assert got2==got and len(picks)==1


def test_downstream_registry_rejects_wrong_workbook(tmp_path,monkeypatch):
    from components.inputs.project_workbooks import registered_project_source
    import components.inputs.project_workbooks as pw
    runtime,edb,original,pointer=_setup(tmp_path)
    export=tmp_path/"export"
    export.mkdir()
    (export/"OpenSees_Element_Connectivity.json").write_text(
        json.dumps({"source_edb":str(edb)}))
    monkeypatch.setattr(pw,"__file__",str(runtime/"components"/"inputs"/"project_workbooks.py"))
    original.write_bytes(b"NOT_THE_REGISTERED_XLSX")
    tk=types.ModuleType("tkinter")
    tk._default_root=object()
    tk.filedialog=types.SimpleNamespace(askopenfilename=lambda **kw:str(original))
    tk.messagebox=types.SimpleNamespace(showwarning=lambda *a,**k:None)
    monkeypatch.setitem(sys.modules,"tkinter",tk)
    with pytest.raises(ValueError,match="SHA256"):
        registered_project_source(export,"etabs_full_table")
    assert not (export/"project_sources.private.json").exists()
