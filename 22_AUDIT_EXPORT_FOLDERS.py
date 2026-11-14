"""Audit ETABS-export folders, optionally mirror flat source artifacts safely.

Examples (Windows / Spyder-compatible Python):
    python 22_AUDIT_EXPORT_FOLDERS.py "D:\\Thesis Opensees\\ETABS 11-14-2026\\3"
    python 22_AUDIT_EXPORT_FOLDERS.py "D:\\Thesis Opensees\\ETABS 11-14-2026\\3" --mirror

--mirror copies eligible flat export files into 01_ETABS_EXPORT with hashes
but NEVER moves or removes originals. Existing different copies fail closed.
All reports remain LOCAL to the selected case; do not commit confidential data.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from components.inputs.folder_audit import write_folder_audit
from components.inputs.export_mirror import export_mirror


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit categorized ETABS/OpenSees case folders safely.")
    parser.add_argument("export_dir", type=Path)
    parser.add_argument("--mirror", action="store_true",
                        help="Create categorized, checksum-verified COPY of flat ETABS exports first.")
    parser.add_argument("--skip-hash", action="store_true",
                        help="Skip potentially expensive original-vs-mirror hash comparison.")
    args = parser.parse_args(argv)
    if args.mirror:
        copied = export_mirror(args.export_dir)
        print("SOURCE_MIRROR_MANIFEST=" + str(copied))
    json_file, md_file = write_folder_audit(args.export_dir,
                                            verify_copies=not args.skip_hash)
    print("FOLDER_AUDIT_JSON=" + str(json_file))
    print("FOLDER_AUDIT_MARKDOWN=" + str(md_file))
    print("STATUS=LOCAL_FOLDER_AUDIT_ONLY_NOT_ENGINEERING_ACCEPTANCE")
    return json_file, md_file


if __name__ == "__main__":
    main()
