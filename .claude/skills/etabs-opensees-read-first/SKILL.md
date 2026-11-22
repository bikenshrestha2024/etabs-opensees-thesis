---
name: etabs-opensees-read-first
description: Mandatory physical-model and NBC load-purpose preflight for every Claude Code task in this thesis repository, to be read before any editing, import/migration, GUI, solver or documentation change.
---

# READ FIRST — physical ETABS/OpenSees project contract

Before touching code or documentation, read in this order:
1. `AGENTS.md`;
2. `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`;
3. `.agents/skills/etabs-opensees-read-first/SKILL.md` (**canonical comprehensive prompt, shared across agents**);
4. `engineering/rules/CORE_RULES.md` and task-relevant source and code-purpose guidance.

The user's foundation has **32 physical support joints** and **44 additional shear-wall mesh points** (76 mapped IDs, NOT 76 independent foundation supports). Never turn the 44 mesh nodes into physical supports or remove their shell connectivity by assumption. The primary full gravity benchmark is **100% dead plus 100% live (`GRAVITY_1.0D_1.0L`)**. The seismic weight is independently defined by **NBC 105:2025 §5.2 Table 5-1** (classified dead=1, storage LL=0.6, other LL=0.3, roof LL=0 as applicable); never use seismic factors as full gravity factors. The gross-shell **3041.266 kN** max joint discrepancy and the different ETABS-elastic **768.045 kN** result must not be conflated. Neither proves native acceptance.

Use the canonical skill's **complete task prompt** and preflight checklist. Preserve source hashes, true model topology, original EDB read-only, Windows/Spyder workflow and native evidence gates. `CLAUDE.md` and existing `.claude/skills/token-saving/SKILL.md` continue to apply; token-saving can never bypass this mandatory read-first gate.
