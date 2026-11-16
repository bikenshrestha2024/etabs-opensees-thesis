# GitHub Issues

Use [GitHub Issues](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues) for this repository’s work. Pass `--repo bikenshrestha2024/etabs-opensees-thesis` to `gh issue` commands because a local checkout may have a mirror as its `origin`.

- Read a ticket with `gh issue view NUMBER --repo bikenshrestha2024/etabs-opensees-thesis --json number,title,body,labels,comments`.
- Find open tickets with `gh issue list --repo bikenshrestha2024/etabs-opensees-thesis --state open`. Use `--label` when filtering by triage state.
- Publish approved tickets with `gh issue create` and use `--body-file` for multiline descriptions.
- Apply triage labels with `gh issue edit` and record triage decisions with `gh issue comment`. Read [Triage labels](triage-labels.md) for the mapping.
- Use GitHub sub-issues for parent-child relationships and native dependencies for blockers. If either operation is unavailable, record `Part of #NUMBER` or `Blocked by #NUMBER` in the issue body, as applicable.

**PRs as a request surface: no.**
