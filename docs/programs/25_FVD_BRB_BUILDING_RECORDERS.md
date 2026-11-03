# Stage 04 — accepted-step FVD/BRB recorders

The exploratory runner now identifies active device override assignments in OpenSees_Element_Overrides_V125.json. Only those actual frame/solver tags receive samples after accepted steps, with full device tags and source frame IDs.

Device_Accepted_Step_History.csv stores relative displacement, relative velocity, and raw basicForce (FVD) or axialForce (BRB). Device_Demand_Summary.csv and JSON store peak absolute demands and the SIGNED force-velocity integral. All force units kN, lengths m, time s. If no devices are active, none are fabricated.

An isolated OpenSees device benchmark is still essential: confirm that installed element recorders return scalar basicForce and axialForce, direction conventions, force sign, stroke, Maxwell spring energy, BRB actual plastic deformation/fatigue. None of this is qualification of a manufacturer FVD/BRB.

References: Korkmaz and Kircil (2026), DOI 10.3390/buildings16040711; Cao et al. (2024), DOI 10.1007/s11803-024-2282-4.
