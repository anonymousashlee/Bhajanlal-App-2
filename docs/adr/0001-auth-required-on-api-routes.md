# ADR-0001: Auth required on all API routes

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

The backend (`serve/backend.py`) exposes HTTP endpoints consumed by the UI and
eval harness. Unauthenticated endpoints allow anonymous access to internal data
and privileged actions.

## Decision

Every route registered in `serve/backend.py` (and any new service module) MUST
enforce authentication via the existing auth middleware/guard before handling
the request. Public health endpoints (`/health`) are the only exception and must
be explicitly allow-listed.

## Consequences

- New endpoints ship with an auth check or are rejected by the gate.
- Health checks remain public for orchestration.

## Security Gate Rule

`ADR-0001`: In `serve/**/*.py`, any `@app.route` / `@router.` decorator must be
followed (within 5 lines) by an auth guard call (`require_auth`, `auth_required`,
`Depends(get_current_user)`, `verify_token`) OR the route path must be in the
public allow-list `{"/health", "/healthz"}`.
