> **READ FIRST — REQUIRED BEFORE ALL EDITS:** Start with root [AGENTS.md](AGENTS.md), [the physical-model contract](engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md), and [the complete mandatory agent skill](.agents/skills/etabs-opensees-read-first/SKILL.md). Use [Claude preflight alias](.claude/skills/etabs-opensees-read-first/SKILL.md). The real foundation has **32 supports + 44 shear-wall mesh points** (not 76 physical supports). Full gravity is **100% DL + 100% LL**; seismic weight is **NBC 105:2025 Table 5-1**, a different case. Emit preflight acknowledgement before editing. Do not claim native acceptance from total reaction balance.

# Claude Code — ETABS–OpenSees Thesis
Read `AGENTS.md` and `engineering/rules/CORE_RULES.md`. Use existing `.claude/skills/token-saving/SKILL.md` rather than creating redundant skills. Scan existing modules/tests before editing; do not rewrite existing research methods. Preserve scientific source and Windows/Spyder compatibility. One bounded task and minimal file slices per session. Do not modify source EDB or mislabel solver PASS as engineering acceptance. Save actual edit evidence to `engineering/agent_edits/` when a change is made; model label UNKNOWN if not available.

## Agent skills

### Issue tracker

For reading or publishing tickets, use [GitHub Issues](docs/agents/issue-tracker.md).

### Triage labels

When triaging an issue, use the [triage label mapping](docs/agents/triage-labels.md).

### Domain docs

Before naming thesis concepts or proposing design changes, consult the [domain documentation guide](docs/agents/domain.md).
