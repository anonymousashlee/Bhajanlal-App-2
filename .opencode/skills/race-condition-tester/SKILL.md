---
name: race-condition-tester
description: Use when sending parallel async requests to exploit TOCTOU flaws in payments/coupons.
---

# race-condition-tester

Part of the **Bhajanlal** model-building skill library. Pillar: 106. Security, Pentesting & Compliance (100 skills)

Use when sending parallel async requests to exploit TOCTOU flaws in payments/coupons.

## Workflow

1. Send parallel requests.
2. Detect TOCTOU.
3. Assess impact.
4. Add locking/idempotency.

## Output

Race condition findings.
