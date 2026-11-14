"""Export organization never mutates flat source files or existing evidence."""
import hashlib
import json
import pytest
from components.inputs.export_mirror import export_mirror

def test_mirror_preserves_source_and_categorizes(tmp_path):
    original=tmp_path/"OpenSees_Element_Connectivity.json"
    original.write_text('{"hello":1}')
    load=tmp_path/"OpenSees_Load_Conversion_Audit.csv"
    load.write_text("a,b\n1,2\n")
    e=tmp_path/"source.edb"
    e.write_bytes(b"never touched")
    before=hashlib.sha256(original.read_bytes()).hexdigest()
    manifest=export_mirror(tmp_path)
    data=json.loads(manifest.read_text())
    assert data["status"]=="MIRRORED_LEGACY_PATHS_PRESERVED"
    assert (tmp_path/"01_ETABS_EXPORT"/"02_MAPPING"/original.name).read_bytes()==original.read_bytes()
    assert (tmp_path/"01_ETABS_EXPORT"/"03_LOADS"/load.name).is_file()
    assert e.read_bytes()==b"never touched"
    assert hashlib.sha256(original.read_bytes()).hexdigest()==before
    assert len(data["files"])==2

def test_mirror_fails_before_clobbering_existing_different_file(tmp_path):
    (tmp_path/"OpenSees_Element_Connectivity.json").write_text("source")
    target=tmp_path/"01_ETABS_EXPORT"/"02_MAPPING"
    target.mkdir(parents=True)
    (target/"OpenSees_Element_Connectivity.json").write_text("different")
    with pytest.raises(ValueError, match="differs"):
        export_mirror(tmp_path)
    assert (target/"OpenSees_Element_Connectivity.json").read_text()=="different"
