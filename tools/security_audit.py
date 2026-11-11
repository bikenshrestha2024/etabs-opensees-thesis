#!/usr/bin/env python3
"""Conservative public-repository secret audit; never prints candidate values.

Run: python tools/security_audit.py --repo .
Scans tracked files only. Git history and GitHub-side secret scanning require
separate checks. False negatives are possible; this is not a security guarantee.
"""
from __future__ import annotations
import argparse
import re
import subprocess
from pathlib import Path

PREFIXES = (
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}")),
    ("github_fine_grained_token", re.compile(r"github_pat_[A-Za-z0-9_]{40,}")),
    ("openai_token", re.compile(r"sk-" + r"(?:proj-|svcacct-)?[A-Za-z0-9_-]{28,}")),
    ("google_api_key", re.compile(r"AIza[A-Za-z0-9_-]{30,}")),
    ("aws_access_key_id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("credential_assignment", re.compile(
        r"""(?im)^\s*(?:export\s+)?(?:[A-Za-z_]\w*\.)?
        (?:api[_-]?key|access[_-]?token|auth[_-]?token|secret[_-]?key|
        client[_-]?secret|password|passwd)\s*[:=]\s*
        [\"']([^\s\"']{16,})[\"']""", re.VERBOSE)),
)
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".rar",
                 ".7z", ".xlsx", ".xls", ".xlsm", ".db", ".sqlite", ".edb",
                 ".exe", ".dll", ".so", ".pyd", ".bin", ".npy", ".npz", ".h5"}
MAX_BYTES = 2 * 1024 * 1024


def tracked_files(root):
    output = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z"], stderr=subprocess.DEVNULL)
    for item in output.split(b"\0"):
        if item:
            yield root / item.decode("utf-8", "surrogateescape")


def audit(root):
    findings, skipped = [], []
    for path in tracked_files(root):
        if path.is_symlink() or not path.is_file():
            continue
        name = path.relative_to(root).as_posix()
        if path.suffix.lower() in SKIP_SUFFIXES or path.stat().st_size > MAX_BYTES:
            skipped.append(name)
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            skipped.append(name)
            continue
        for category, pattern in PREFIXES:
            for match in pattern.finditer(content):
                # The scanner's own regex definitions must not generate alerts.
                if name == "tools/security_audit.py":
                    continue
                findings.append((name, content.count("\n", 0, match.start()) + 1, category))
    return findings, skipped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    try:
        findings, skipped = audit(root)
    except (OSError, subprocess.CalledProcessError) as exc:
        parser.exit(2, "Audit could not scan tracked files: " + str(exc) + "\n")
    print(f"Tracked-file scan: {len(findings)} candidate findings, {len(skipped)} skipped binary/oversized files.")
    for path, line, kind in findings:
        print(f"CANDIDATE: {path}:{line} category={kind} [VALUE REDACTED]")
    print("Scope: current tracked tree ONLY. Review Git history and GitHub alert settings separately.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
