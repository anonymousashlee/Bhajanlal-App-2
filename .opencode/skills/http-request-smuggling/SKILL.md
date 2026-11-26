---
name: http-request-smuggling
description: Use when detecting CL.TE and TE.CL desynchronization between proxies and backends.
---

# http-request-smuggling

Part of the **Bhajanlal** model-building skill library. Pillar: 106. Security, Pentesting & Compliance (100 skills)

Use when detecting CL.TE and TE.CL desynchronization between proxies and backends.

## Workflow

1. Probe CL.TE/TE.CL.
2. Detect desync.
3. Assess impact.
4. Fix proxy/backend parsing.

## Output

Request smuggling findings.
