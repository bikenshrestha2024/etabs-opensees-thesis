"""Verify directional Rayleigh periods from ETABS assignment and analysis exports."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from openpyxl import load_workbook

from reconcile import G, empirical_reference, matches_empirical_reference, rayleigh

STORIES = [f"Story{i}" for i in range(1, 26)]


def table(book, name, required_units=None):
    rows = book[name].iter_rows(min_row=2, values_only=True)
    names = next(rows)
    units = dict(zip(names, next(rows), strict=True))
    for field, unit in (required_units or {}).items():
        if units.get(field) != unit:
            raise ValueError(f"{name} {field}: expected {unit}, found {units.get(field)}")
    return [dict(zip(names, row, strict=True)) for row in rows]


def index(rows, field, name):
    indexed = {row[field]: row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError(f"{name}: duplicate {field}")
    return indexed


def fingerprint(path):
    with path.open("rb") as source:
        return {"name": path.name, "bytes": path.stat().st_size,
                "sha256": hashlib.file_digest(source, "sha256").hexdigest()}


def initial_stiffness(path):
    source = path.read_text(encoding="latin-1")

    def setting(pattern):
        matches = re.findall(pattern, source, flags=re.M)
        if len(matches) != 1:
            raise ValueError(f"Expected one ETABS setting matching {pattern}")
        return matches[0]

    preset = setting(r'^\s*PDELTA\s+METHOD\s+"([^"]+)"')
    cases = {
        case: setting(rf'^\s*LOADCASE "{case}"\s+TYPE\s+"[^"]+"\s+INITCOND\s+"([^"]+)"')
        for case in ("EQX", "EQY", "Modal Ritz")
    }
    ritz = {
        axis: setting(rf'^\s*LOADCASE "RS{axis} P Delta"\s+TYPE\s+"Response Spectrum"\s+MODALCASE\s+"([^"]+)"')
        for axis in ("X", "Y")
    }
    return {
        "snapshot": fingerprint(path), "global_pdelta_preset": preset,
        "initial_stiffness_by_case": cases, "rs_modal_case": ritz,
        "both_rs_use_unpreloaded_ritz_preset": (
            preset.upper() == "NONE" and cases["Modal Ritz"].upper() == "PRESET"
            and set(ritz.values()) == {"Modal Ritz"}
        ),
    }


def verify(assignment, analysis, provenance=True, *, pdelta=False):
    with_book = load_workbook(assignment, read_only=True, data_only=True)
    result_book = load_workbook(analysis, read_only=True, data_only=True)
    try:
        auto = index(table(with_book, "Auto Seismic - User Coefficient"), "Name", "auto seismic")
        names = {axis: f"EQ{axis}+ P-Delta" if pdelta else f"EQ{axis}" for axis in "XY"}
        static = index([row for row in table(with_book, "Load Cases - Linear Static")
                        if row["Name"] in names.values()], "Name", "centered load cases")
        nonlinear = table(with_book, "Load Cases - Nonlinear Static") if pdelta else []
        mass = index(table(with_book, "Mass Summary by Story", {"UX": "kg", "UY": "kg"}),
                     "Story", "story mass")
        cm = table(result_book, "Diaphragm CM Displacements",
                   {"UX": "mm", "UY": "mm", "RZ": "rad", "X": "m", "Y": "m", "Z": "m",
                    "Diaphragm Mass X": "kg", "Diaphragm Mass Y": "kg"})
        cuts = table(result_book, "Story Forces", {"VX": "kN", "VY": "kN", "T": "kN-m"})
        modes = table(result_book, "Modal Participating Mass Ratios", {"Period": "sec"})
    finally:
        with_book.close()
        result_book.close()
    output = {"directions": {}}
    if provenance:
        output["files"] = [fingerprint(assignment), fingerprint(analysis)]
    for axis in "XY":
        pattern = "EQ" + axis
        case = names[axis]
        branch = auto[pattern + "(1/3)"]
        enabled = [k for k in branch if k.endswith("?") and branch[k] == "Yes"]
        if enabled != [axis + " Dir?"] or static[case]["Load Name"] != pattern or static[case]["Load SF"] != 1:
            raise ValueError(f"{case}: centered branch or unit case load not confirmed")
        initial_case = static[case]["Nonlinear Case"]
        if pdelta and not any(r["Name"] == initial_case and r["Geometric Nonlinearity"] == "P-Delta"
                              for r in nonlinear):
            raise ValueError(f"{case}: a nonlinear P-Delta initial case is required")

        def selected(row):
            return (row["Output Case"], row["Case Type"], row["Step Type"], row["Step Number"]) == (
                case, "LinStatic", "Step By Step", 1
            )

        centers = index([r for r in cm if selected(r)], "Story", f"{case} CM")
        bottom = index([r for r in cuts if selected(r) and r["Location"] == "Bottom"],
                       "Story", f"{case} bottom cut")
        if set(centers) != set(bottom) or set(centers) != set(STORIES):
            raise ValueError(f"{case}: incomplete floor matching")
        shear = [-bottom[story]["V" + axis] for story in STORIES]
        forces = [v - above for v, above in zip(shear, shear[1:] + [0], strict=True)]
        rows = []
        for story, force in zip(STORIES, forces, strict=True):
            center = centers[story]
            kg = mass[story]["U" + axis]
            if center["Diaphragm"] != "D1" or abs(kg - center["Diaphragm Mass " + axis]) > 0.01:
                raise ValueError(f"{case} {story}: diaphragm or mass mismatch")
            cut_row = bottom[story]
            torsion = cut_row["T"] - center["X"] * cut_row["VY"] + center["Y"] * cut_row["VX"]
            rows.append({"story": story, "level_m": center["Z"], "weight_kN": kg * G / 1000,
                         "force_kN": force, "displacement_m": center["U" + axis] / 1000,
                         "rotation_rad": center["RZ"],
                         "torsion_kNm": torsion})
        shape = [r["weight_kN"] * r["level_m"] ** branch["K"] for r in rows]
        total = math.fsum(shape)
        shape_error = max(abs(f - v / total * shear[0]) for f, v in zip(forces, shape, strict=True))
        if (abs(shear[0] - branch["Base Shear"]) > 0.002
                or abs(math.fsum(row["weight_kN"] for row in rows) - branch["Weight Used"]) > 0.02
                or shape_error > 0.003):
            raise ValueError(f"{case}: native shear, weight or floor-force distribution mismatch")
        ritz = sorted((mode for mode in modes if mode["Case"] == "Modal Ritz"),
                      key=lambda mode: int(mode["Mode"]))
        if any(r["SumU" + axis] < l["SumU" + axis] for l, r in zip(ritz, ritz[1:])):
            raise ValueError(f"{axis}: cumulative modal mass must increase in numeric mode order")
        primary = max(ritz, key=lambda mode: mode["U" + axis])
        tn = next(mode for mode in ritz if mode["SumU" + axis] >= 0.9)
        # Use the consistent force and displacement scaling expected for one linear state.
        max_ecc = max(abs(r["torsion_kNm"] / v) for r, v in zip(rows, shear, strict=True))
        if pdelta and max_ecc > 0.001:
            raise ValueError(f"{case}: residual torsion exceeds 1 mm equivalent eccentricity")
        tolerance = max(abs(r["torsion_kNm"]) for r in rows) if pdelta else 0.002
        doubled = [dict(r, force_kN=2*r["force_kN"], displacement_m=2*r["displacement_m"])
                   for r in rows]
        seeded = pdelta and matches_empirical_reference(axis, branch["C"], branch["K"], shear[0])
        eligible = not pdelta or seeded
        period = rayleigh(rows, torsion_tolerance_kNm=tolerance) if eligible else {"period_s": None}
        double_period = rayleigh(doubled, torsion_tolerance_kNm=tolerance)["period_s"] if eligible else None
        output["directions"][axis] = dict(period, native_cd=branch["C"], native_k=branch["K"],
            base_shear_kN=shear[0], roof_translation_mm=1000*rows[-1]["displacement_m"],
            max_force_distribution_error_kN=shape_error, preceding_nonlinear_case=static[case]["Nonlinear Case"],
            stiffness_label=static[case]["Stiffness Type"], ritz_s=primary["Period"],
            ritz_mode=int(primary["Mode"]), tn90_s=tn["Period"], tn90_mode=int(tn["Mode"]),
            proportional_double_period_s=double_period,
            pdelta_rayleigh_verified=seeded, empirical_reference_verified=seeded,
            expected_empirical_reference=empirical_reference(axis), case=case, max_cut_equivalent_eccentricity_m=max_ecc,
            max_floor_rotation_rad=max(abs(r["rotation_rad"]) for r in rows), rows=rows)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assignment", type=Path)
    parser.add_argument("analysis", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--staged", type=Path, help="Compare against the V10.8 reconciliation JSON.")
    parser.add_argument("--e2k", type=Path, help="Audit the stiffness basis of a companion E2K snapshot.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--pdelta", dest="pdelta", action="store_true",
                        help="Use centered Step 1 of EQX+/EQY+ P-Delta (default).")
    source.add_argument("--historical-unpreloaded", dest="pdelta", action="store_false",
                        help="Reproduce the old unstaged EQX/EQY diagnostic.")
    parser.set_defaults(pdelta=True)
    args = parser.parse_args()
    result = verify(args.assignment, args.analysis, pdelta=args.pdelta)
    if args.e2k:
        result["companion_initial_stiffness"] = initial_stiffness(args.e2k)
    if args.staged:
        targets = json.loads(args.staged.read_text(encoding="utf-8"))["directions"]
        match = {}
        for axis, readback in result["directions"].items():
            expected = targets[axis]
            match[axis] = {
                "coefficient_matches": expected["cd_uls"] is not None and abs(readback["native_cd"] - expected["cd_uls"]) < 5.1e-7,
                "exponent_matches": expected["k"] is not None and abs(readback["native_k"] - expected["k"]) < 5.1e-7,
                "base_shear_matches": expected["updated_esm_minimum_kN"] is not None and abs(readback["base_shear_kN"] - expected["updated_esm_minimum_kN"]) < 0.01,
            }
        result["matches_staged_eq_settings"] = all(all(axis.values()) for axis in match.values())
        result["staged_settings_readback"] = match
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
