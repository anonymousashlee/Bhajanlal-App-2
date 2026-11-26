#!/usr/bin/env python3
"""ADR security gate.

Checks changed (staged) files against the ADRs in docs/adr/ before commit.
Exits non-zero on a blocking violation.

Usage:
    python scripts/adr_security_gate.py            # staged files
    python scripts/adr_security_gate.py --all      # all tracked files
    python scripts/adr_security_gate.py path ...   # explicit files
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Paths excluded from scanning.
EXCLUDE = {".env.example"}
EXCLUDE_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}

# Secret patterns (ADR-0002).
SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "sk- style secret"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key header"),
    (re.compile(r"(?i)(password|secret|api_key|token)\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']"), "hardcoded secret assignment"),
]

# SQL injection patterns (ADR-0003).
# The SQL keyword must be inside a (possibly f-)quoted string literal so that
# identifiers/method names (e.g. def update(...)) don't trip the gate.
SQL_KEYWORDS = re.compile(r"(?i)(?:^|[^A-Za-z0-9_])(?:f?\"|f?'|\\\")\s*(SELECT|INSERT|UPDATE|DELETE|DROP)\b")
SQL_VIOLATION = re.compile(r"(?i)(f[\"'].*\b(SELECT|INSERT|UPDATE|DELETE)\b|\.format\(|\+\s*[\"']|\+\s*[a-zA-Z_])")

# Auth patterns (ADR-0001).
ROUTE_DECORATOR = re.compile(r"@(app|router|blueprint)\.(route|get|post|put|delete|patch)\b")
AUTH_GUARDS = re.compile(r"(require_auth|auth_required|Depends\(get_current_user\)|verify_token|current_user)")

# Input validation (ADR-0004) - warning only.
RAW_INPUT = re.compile(r"request\.(json|args|form|data|values)")
VALIDATION = re.compile(r"(validate|parse_obj|model_validate|schema\.load|\.validate\(|isinstance\()")


def is_excluded(path: Path) -> bool:
    if path.name in EXCLUDE:
        return True
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return True
    if path.suffix in {".md"} and "docs" in path.parts:
        return True
    if path.name == ".env.example":
        return True
    return False


def staged_files() -> list[Path]:
    out = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], cwd=ROOT, text=True
    )
    return [ROOT / p for p in out.split() if p.strip()]


def all_tracked() -> list[Path]:
    out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [ROOT / p for p in out.split() if p.strip()]


def read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []


def check_file(path: Path) -> tuple[list[str], list[str]]:
    """Return (blocking_violations, warnings)."""
    blocking: list[str] = []
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        return blocking, warnings
    if is_excluded(path):
        return blocking, warnings
    rel = path.relative_to(ROOT)
    lines = read_lines(path)

    # ADR-0002: secrets
    if path.suffix not in {".png", ".jpg", ".jpeg", ".gif", ".zip", ".pyc"}:
        text = "\n".join(lines)
        for pat, label in SECRET_PATTERNS:
            for m in pat.finditer(text):
                # skip placeholders
                snippet = m.group(0)
                if "example" in snippet.lower() or "placeholder" in snippet.lower() or "xxx" in snippet.lower():
                    continue
                blocking.append(f"{rel}: ADR-0002 secret pattern ({label}): {snippet[:60]}")

    # ADR-0003 + ADR-0001 + ADR-0004 (python app code only)
    app_code = "serve" in path.parts or "deploy" in path.parts
    if path.suffix == ".py" and app_code:
        for i, line in enumerate(lines, 1):
            if SQL_KEYWORDS.search(line) and SQL_VIOLATION.search(line):
                blocking.append(f"{rel}:{i}: ADR-0003 non-parameterized SQL: {line.strip()[:80]}")

        # ADR-0001: route decorators need auth guard nearby
        for i, line in enumerate(lines, 1):
            if ROUTE_DECORATOR.search(line):
                window = "\n".join(lines[i : i + 6])
                route_path_match = re.search(r"\([\"']([^\"']+)[\"']", line)
                route_path = route_path_match.group(1) if route_path_match else ""
                if route_path in {"/health", "/healthz"}:
                    continue
                if not AUTH_GUARDS.search(window):
                    blocking.append(f"{rel}:{i}: ADR-0001 route without auth guard nearby: {line.strip()[:80]}")

        # ADR-0004: raw input without validation (warning)
        for i, line in enumerate(lines, 1):
            if RAW_INPUT.search(line):
                window = "\n".join(lines[max(0, i - 2) : i + 4])
                if not VALIDATION.search(window):
                    warnings.append(f"{rel}:{i}: ADR-0004 raw input without nearby validation: {line.strip()[:80]}")

    return blocking, warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="scan all tracked files")
    ap.add_argument("files", nargs="*", help="explicit files")
    args = ap.parse_args()

    if args.files:
        files = [Path(f).resolve() if not Path(f).is_absolute() else Path(f) for f in args.files]
        files = [f if f.is_absolute() else ROOT / f for f in files]
    elif args.all:
        files = all_tracked()
    else:
        files = staged_files()

    if not files:
        print("ADR security gate: no files to scan.")
        return 0

    all_blocking: list[str] = []
    all_warnings: list[str] = []
    for f in files:
        b, w = check_file(f)
        all_blocking.extend(b)
        all_warnings.extend(w)

    if all_warnings:
        print("ADR security gate warnings:")
        for w in all_warnings:
            print("  - " + w)

    if all_blocking:
        print("ADR security gate BLOCKED commit:")
        for b in all_blocking:
            print("  - " + b)
        print("\nResolve the violations or update the relevant ADR before committing.")
        return 1

    print(f"ADR security gate: PASS ({len(files)} files scanned, 0 blocking violations).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
