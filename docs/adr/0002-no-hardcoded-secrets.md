# ADR-0002: No hardcoded secrets

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

API keys, tokens, passwords, and private keys committed to source are a common
exfiltration vector and are hard to rotate.

## Decision

Secrets MUST be loaded from environment variables or a secret manager. No
literal secret values may appear in committed source, config, or docs. Only
`.env.example` may contain placeholder values.

## Consequences

- Code references `os.environ` / `os.getenv` / settings objects.
- `.env` and key files remain gitignored.

## Security Gate Rule

`ADR-0002`: Scanned text files must not contain patterns matching common secret
formats (AWS access keys `AKIA...`, OpenAI/Anthropic-style `sk-...`, private key
headers `-----BEGIN ... PRIVATE KEY-----`, or `password|secret|token = "..."` with
a non-placeholder value). Allow-listed paths: `.env.example`, `docs/`, `*.md`.
