# One count per physical self-weight source

`components/model/single_count_self_weight.py` is invoked during `components/model/assembly.py` source-model build. An explicit gravity nodal load is generated from each finite-element member's source volume (area × frame length or shell thickness × shell area), source material unit weight and exactly one ETABS source self-weight pattern allocation.

A self-weight multiplier is *not another self-weight*. It represents how ETABS assigns a fraction of one physical self-weight to a load pattern; it is retained to avoid dropping or duplicating loads when building Dead/Live, configured seismic preload or other profiles. OpenSees does not automatically apply member body-force weight in the standard frame/shell assembly used here; it must be explicitly loaded once.

The validator raises on duplicate pattern IDs or when the sum of source self-weight multipliers exceeds unity. A configured gravity strength-combination factor above unity (for example, 1.2D) is a legitimate factored load and **does not** constitute double-counted geometry. An anomalously high seismic self-weight mass coefficient is separately flagged for review. Multipliers must be nonnegative and finite. Intentional unusual source cases with multiple physical self-weight allocations require separate engineering review, not silent acceptance.

The resulting `Gravity_Single_Count_Self_Weight_Audit.json` contains source pattern allocations, full DL+LL physical self-weight coefficient, configured gravity coefficient, seismic mass coefficient, and explicit `geometric_joint_solid_ownership=NOT_ESTABLISHED_BY_THIS_AUDIT`.

Physical intersection accounting must not use a blanket subtract-every-beam/column/slab/wall joint solid volume rule. A joint counted in different members can be subtracted twice. The reviewed source beam clear-length convention can be enabled only after independent original ETABS Material List, Self Weight Option and end-offset evidence. It is mutually exclusive with `VERIFIED_SINGLE_OWNER`.

ETABS documented `Frame End Length Offsets` (https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm) explains overlap and rigid-zone kinematics; the **frame self-weight option is a distinct setting**. The source model's 8,652.444 kN excess beam weight equals 721.25 m of reported offsets × 0.6 × 0.8 m × 24.992618 kN/m³, but that arithmetic is never used to tune the model automatically.

New ETABS metadata extraction also uses `PropFrame.GetSectProps` to transfer native SHS gross area and elastic I22/I33/J. CSI API: https://docs.csiamerica.com/help-files/etabs-api-2016/html/7e0e26e6-6e25-6b5a-c523-003da72307e8.htm. A missing native SHS record remains an unvalidated sharp-corner fallback and is reported in export warnings. The source data must be freshly exported from the original EDB to use this feature.

Gravity source conservation and source-to-ETABS equivalence are independent gates. Avoid introducing reaction-dependent load adjustments or choosing new restraint nodes based only on zero/nonzero ETABS reactions.

Author: ChatGPT GPT-6, November 2026.
