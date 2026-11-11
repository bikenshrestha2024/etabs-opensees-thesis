# Security policy — public ETABS-to-OpenSees thesis repository

This repository contains engineering research code and documentation. **Do not open a public issue containing credentials, proprietary ETABS EDB files, sensitive building plans, local file inventories or unredacted logs.**

## Reporting possible exposed secrets
Contact the repository owner privately through GitHub profile contact methods or GitHub's private vulnerability reporting feature if enabled. Never paste a live token or password in a GitHub issue, pull request, CI log or ChatGPT conversation.

If a live credential has been exposed:
1. Immediately revoke or rotate it through its provider; deleting a file or commit alone does not invalidate credentials.
2. Review the associated provider account for unauthorized use and reduce scopes/permissions.
3. Remove plaintext credentials from active code; use environment variables or GitHub Actions secrets for legitimately required access.
4. Coordinate public Git-history cleanup with repository collaborators; clones and caches may retain old data.
5. Verify remediations using secret scanning and a private historical scan, without publishing a secret-bearing report.

## Supported security checks
- Current tracked files: `python tools/security_audit.py --repo .`
- CI: `.github/workflows/history-ui-security.yml` (read-only token permissions, no persisted checkout credentials).
- Full Git history: use `gitleaks git --redact` locally and keep its report private.
- Enable GitHub repository secret scanning and push protection when supported; review Dependabot alerts, branch protection, action permissions and third-party action pinning.

**Scope limits:** The checked-in scanner is intentionally lightweight and cannot certify history, dependency safety, binary content or privately configured GitHub secrets. The engineering output ZIP exporter is local-only but may include sensitive project paths within logs or JSON; inspect prior to disclosure.

See `docs/review/20261111_HISTORY_GUI_SECURITY_AND_PHYSICS.md` for engineering and data-provenance restrictions.
