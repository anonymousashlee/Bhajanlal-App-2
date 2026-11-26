---
name: subdomain-enum
description: Use when orchestrating passive and active subdomain discovery (Amass, Subfinder).
---

# subdomain-enum

Part of the **Bhajanlal** model-building skill library. Pillar: 106. Security, Pentesting & Compliance (100 skills)

Use when orchestrating passive and active subdomain discovery (Amass, Subfinder).

## Workflow

1. Run passive sources (CT logs, DNS).
2. Run active brute-force/permutation.
3. Dedup and validate live hosts.
4. Feed into attack surface graph.

## Output

Comprehensive subdomain inventory.
