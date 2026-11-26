# Architectural Decision Records (ADRs)

ADRs capture significant architectural decisions for the Bhajanlal app. The
`adr-security-gate` (see `.opencode/skills/adr-security-gate/SKILL.md`) checks
code edits against these records before commit and blocks violations.

## Index

- [ADR-0001](0001-auth-required-on-api-routes.md) - Auth required on all API routes
- [ADR-0002](0002-no-hardcoded-secrets.md) - No hardcoded secrets
- [ADR-0003](0003-parameterized-sql-queries.md) - Parameterized SQL queries only
- [ADR-0004](0004-validate-external-input.md) - Validate all external input at boundaries

## Format

Each ADR uses: Title, Status, Context, Decision, Consequences, Security Gate Rule.
A rule is a machine-checkable predicate referenced by `scripts/adr_security_gate.py`.
