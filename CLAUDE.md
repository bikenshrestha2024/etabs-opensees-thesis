# Claude Code — ETABS–OpenSees Thesis
Read `AGENTS.md` and `engineering/rules/CORE_RULES.md`. Use existing `.claude/skills/token-saving/SKILL.md` rather than creating redundant skills. Scan existing modules/tests before editing; do not rewrite existing research methods. Preserve scientific source and Windows/Spyder compatibility. One bounded task and minimal file slices per session. Do not modify source EDB or mislabel solver PASS as engineering acceptance. Save actual edit evidence to `engineering/agent_edits/` when a change is made; model label UNKNOWN if not available.

## Agent skills

### Issue tracker

For reading or publishing tickets, use [GitHub Issues](docs/agents/issue-tracker.md).

### Triage labels

When triaging an issue, use the [triage label mapping](docs/agents/triage-labels.md).

### Domain docs

Before naming thesis concepts or proposing design changes, consult the [domain documentation guide](docs/agents/domain.md).
