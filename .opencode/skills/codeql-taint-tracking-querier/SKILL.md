---
name: Codeql Taint Tracking Querier
description: Write CodeQL queries tracing untrusted user input from sources to SQL/command sinks.
---

# Codeql Taint Tracking Querier

Part of the **Bhajanlal** OpenCode skill library.

Pillar: 120. Source Code Audit, Wireless & Reporting (10 skills)

Use only on systems you own or have explicit written authorization to test.

## Workflow

1. Confirm written authorization and the exact in-scope targets before running any tool.
2. Prepare the tooling described here (Write CodeQL queries tracing untrusted user input from sources to SQL/command sinks) and set scoped, rate-limited parameters.
3. Execute against authorized targets only, capturing raw output and timestamps.
4. Correlate results with other findings and manually validate every candidate issue.
5. Record evidence, assign severity, and map each finding to a concrete remediation.

## Output

A structured finding set with evidence, confidence, severity, and remediation guidance, plus a short executive summary suitable for a rules-of-engagement report.
