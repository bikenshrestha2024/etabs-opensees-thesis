"""Evidence-gated mapping of ETABS-reviewed RC reinforcement to fiber templates.

A section design report or reinforcement schedule must first be exported/reviewed
outside OpenSees. This module cannot claim reinforcement automatically from ETABS.
The current template models use equivalent bars_per_side; detailed irregular bar
coordinates and hoop confinement require a more capable fiber section interface.
Source: PEER 2015/12 (wall material calibration methodology).
"""
from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path

REQUIRED=("section_key","width_mm","depth_mm","cover_mm","bar_diameter_mm",
          "bars_per_side","tie_diameter_mm","tie_spacing_mm","source_file_sha256",
          "reviewed_by","review_status")
APPROVED="APPROVED_FROM_ETABS_DRAWINGS"


def read_approved_frame_register(path, expected_sections):
    """Return strict mappings for existing template geometry; never infer missing bars.

    All sizes are in mm. The source hash must correspond to the actual reviewed
    ETABS schedule/drawing, not to a made-up or self-reported model identifier.
    """
    path=Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        if not reader.fieldnames or any(k not in reader.fieldnames for k in REQUIRED):
            raise ValueError("Reinforcement CSV missing mandatory columns")
        rows=list(reader)
    if not rows:
        raise ValueError("Reinforcement register has no rows")
    seen={}
    for row in rows:
        key=row["section_key"].strip()
        if key in seen:
            raise ValueError(f"Duplicate reinforcement section key: {key}")
        if key not in expected_sections:
            raise ValueError(f"Unknown section key {key}; review section mapping")
        if row["review_status"].strip()!=APPROVED or not row["reviewed_by"].strip():
            raise ValueError(f"{key}: schedule is not independently approved")
        digest=row["source_file_sha256"].strip().lower()
        if len(digest)!=64 or any(x not in "0123456789abcdef" for x in digest):
            raise ValueError(f"{key}: missing/invalid source SHA256")
        dimensions={}
        for name in ("width_mm","depth_mm","cover_mm","bar_diameter_mm","tie_diameter_mm","tie_spacing_mm"):
            value=float(row[name])
            if not math.isfinite(value) or value<=0:
                raise ValueError(f"{key}: {name} must be finite and positive")
            dimensions[name]=value
        bars=float(row["bars_per_side"])
        if not bars.is_integer() or bars<2 or bars>100:
            raise ValueError(f"{key}: bars_per_side must be an integer >=2")
        dimensions["bars_per_side"]=int(bars)
        old=expected_sections[key]
        for name in ("width_mm","depth_mm"):
            if not math.isclose(dimensions[name],float(old[name]),abs_tol=1e-6,rel_tol=0):
                raise ValueError(f"{key}: {name} differs from current fiber section geometry")
        if dimensions["cover_mm"]+dimensions["tie_diameter_mm"]+dimensions["bar_diameter_mm"] >= 0.5*min(dimensions["width_mm"],dimensions["depth_mm"]):
            raise ValueError(f"{key}: no viable confined core")
        seen[key]=dict(parameters=dimensions,source_file_sha256=digest,
                       reviewer=row["reviewed_by"].strip(),review_status=APPROVED)
    if set(seen)!=set(expected_sections):
        raise ValueError("Missing approved reinforcement for sections: "+
                         ", ".join(sorted(set(expected_sections)-set(seen))))
    return seen


def apply_approved_frame_register(section_configs, register):
    """Only update geometric/rebar keys, not unmeasured concrete confinement."""
    new={key:dict(value) for key,value in section_configs.items()}
    for name,record in register.items():
        if name not in new:
            raise ValueError(f"No fiber section matches register key {name}")
        for field,value in record["parameters"].items():
            if field == "tie_spacing_mm":
                continue  # Metadata only: do not infer confined concrete strength.
            new[name][field]=value
    return new
