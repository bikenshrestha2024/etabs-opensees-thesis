"""Non-destructive categorized mirror of current ETABS export."""
import argparse
from pathlib import Path
from components.inputs.export_mirror import export_mirror
from components.inputs.output_layout import write_stage_index

def main(argv=None):
    """Export root CLI. [REF docs/source/components/inputs/export_mirror.py.md]"""
    p=argparse.ArgumentParser(description="Copy generated ETABS artifacts into 01_ETABS_EXPORT, preserve legacy files")
    p.add_argument("export_dir",type=Path)
    args=p.parse_args(argv)
    path=export_mirror(args.export_dir)
    index = write_stage_index(args.export_dir)
    print("ORGANIZED_MANIFEST="+str(path))
    print("STAGE_INDEX="+str(index))
    print("STATUS=MIRRORED_LEGACY_PATHS_PRESERVED")
    return path

if __name__=="__main__":
    main()
