# ADR-0004: Validate all external input at boundaries

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

External input (HTTP bodies, query params, CLI args, webhooks) flows into
business logic. Unvalidated input causes injection and logic flaws.

## Decision

Every external entry point must validate and sanitize input with a strict schema
(Pydantic/Zod/equivalent) before use. Raw `request.json` / `request.args`
values must not reach DB or shell calls unvalidated.

## Consequences

- Clear trust boundary; more boilerplate at handlers.

## Security Gate Rule

`ADR-0004`: Informational. Reported as a warning when a handler reads
`request.json`/`request.args`/`request.form` without a nearby validation call
(`validate`, `parse_obj`, `model_validate`, `schema.load`). Does not block.
