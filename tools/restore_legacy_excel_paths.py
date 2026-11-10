"""Plan or restore byte-identical workbook copies for historical launchers."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil


def restore_legacy_workbooks(root, *, apply=False):
    """Restore catalogued old paths without overwriting existing workbooks.

    Only paths within the checkout are allowed; SHA256 is verified first.
    Default is a read-only plan. New code uses excel/ directly.
    [REF docs/review/EXCEL_AND_LAUNCHER_PUBLICATION_DECISIONS.md]
    """
    root=Path(root).resolve()
    catalog=json.loads((root/'excel/WORKBOOK_CATALOG.json').read_text(encoding='utf-8'))
    result=[]
    for entry in catalog['workbooks']:
        if not entry.get('legacy_path'):continue
        source=(root/entry['path']).resolve();target=(root/entry['legacy_path']).resolve()
        if not source.is_relative_to(root) or not target.is_relative_to(root):
            raise ValueError('Workbook path leaves checkout')
        if not source.is_file():raise FileNotFoundError(source)
        with source.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
        if sha!=entry['sha256']:raise ValueError('Source workbook hash mismatch: '+entry['path'])
        status='PLANNED'
        if target.exists():
            with target.open('rb') as stream:old=hashlib.file_digest(stream,'sha256').hexdigest()
            if old!=sha:raise ValueError('Refusing to overwrite different workbook: '+entry['legacy_path'])
            status='ALREADY_IDENTICAL'
        elif apply:
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);status='RESTORED'
        result.append({'legacy_path':entry['legacy_path'],'status':status})
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore',action='store_true',help='Create missing compatibility copies; never overwrite')
    args=parser.parse_args()
    rows=restore_legacy_workbooks(Path(__file__).resolve().parents[1],apply=args.restore)
    print(json.dumps(rows,indent=2))
