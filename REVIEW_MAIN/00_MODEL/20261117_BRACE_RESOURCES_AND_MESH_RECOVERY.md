# Brace resources and incomplete mesh-run follow-up

Search date: 2026-11-17. Literature discovery is not a calibrated project model.
The screenshot shows model data, export report and mapping workbook already
written; the last GUI stage alone cannot locate a hang. PR #112 was still draft
and unmerged when checked. No access to the user's Windows interpreter or
current run status JSON was available from the Linux workspace.

## Primary sources checked

- Uriz, Filippou and Mahin (2008), Model for Cyclic Inelastic Buckling of Steel Braces,
  DOI https://doi.org/10.1061/(ASCE)0733-9445(2008)134:4(619): distributed fiber
  plasticity and corotational geometry for axial-flexural buckling.
- Uriz and Mahin, PEER 2008/08, especially 4.4 parameter study:
  https://peer.berkeley.edu/sites/default/files/web_peer808_uriz_patxi_uriz_stephen_a._mahin.pdf
  Identifies element subdivision, integration and initial camber as modeling decisions.
- Official Fatigue material:
  https://opensees.berkeley.edu/wiki/index.php/Fatigue_Material
  Its default fatigue calibration derives from European steel tests, not this SHS.
- 2025 SHS local-buckling damage model, DOI https://doi.org/10.1016/j.tws.2025.113451.
  Candidate additional formulation; no implementation or project transfer established.
- 2026 endplate-gusset frame experiments:
  https://www.sciencedirect.com/science/article/pii/S2352012426011136
  Different connection specimens; not proof of this building's pin idealization.

## Required implementation evidence

A defensible ordinary-brace adapter needs actual SHS geometry/corner properties,
steel cyclic material inputs, unbraced lengths, imperfection direction/amplitude,
connection rotation/torsion treatment and validated local-buckling/fracture limits.
A forceBeamColumn fiber section with Corotational transformation is a candidate
for global buckling, not automatic local-buckling or fracture reproduction.
Preserve end releases using explicit compatible end DOFs; do not replace the
member with an axial truss and claim buckling is solved. Benchmark monotonic
compression, reversal, end moments, force balance, mesh sensitivity and cyclic
energy against source specimens before full-building adoption. No guessed
project calibration or approval boolean added in this fix.

## Runtime recovery

Use the existing source/config SHA-checked saved-mesh workbook recovery exposed
as `python -m components.gravity.mesh_cases EXPORT_ROOT --mesh 4` from the
updated checkout. It avoids reassembling a saved, matching FLOOR mesh. Old GUI
processes must be closed before starting recovery. New builds retain runtime
identity, stage log and original failure traceback. Native Windows completion,
full 4/8/16 solves and project brace validation remain unexecuted here.
