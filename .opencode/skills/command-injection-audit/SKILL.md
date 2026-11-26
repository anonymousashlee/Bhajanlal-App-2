---
name: command-injection-audit
description: Use when tracing unsanitized user inputs passed to OS shell execution functions.
---

# command-injection-audit

Part of the **Bhajanlal** model-building skill library. Pillar: 106. Security, Pentesting & Compliance (100 skills)

Use when tracing unsanitized user inputs passed to OS shell execution functions.

## Workflow

1. Find shell exec calls.
2. Trace user input to sinks.
3. Test injection payloads.
4. Replace with safe APIs.

## Output

Command injection findings.
