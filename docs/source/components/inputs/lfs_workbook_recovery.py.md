# Git LFS workbook source recovery

Source: [lfs_workbook_recovery.py](../../../../components/inputs/lfs_workbook_recovery.py)

Handles repository-stored Excel workbook sources that can be represented by Git LFS pointer files. Before using recovered sources in the engineering workflow, verify the actual workbook bytes, source identity and hash. Do not replace an unavailable workbook with another model's spreadsheet or claim that an LFS pointer is a complete Excel archive.

This document describes intended evidence safeguards; review exact implementation, exceptions and caller requirements in the linked source.
