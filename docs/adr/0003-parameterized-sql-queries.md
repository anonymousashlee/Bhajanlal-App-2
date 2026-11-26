# ADR-0003: Parameterized SQL queries only

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

String-interpolated SQL enables injection. The codebase uses SQLite/Postgres
drivers that support parameter binding.

## Decision

All SQL must use parameter binding (`?`, `%s`, `:name`) with values passed
separately. f-strings, `.format()`, or `+` concatenation inside SQL strings
are forbidden.

## Consequences

- Safer queries; slightly more verbose call sites.

## Security Gate Rule

`ADR-0003`: In `*.py`, lines containing SQL keywords (`SELECT`, `INSERT`,
`UPDATE`, `DELETE`) combined with an f-string or `.format(` or `+` string
concatenation on the same line are violations.
