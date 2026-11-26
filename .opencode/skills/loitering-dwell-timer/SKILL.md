---
name: Loitering Dwell Timer
description: Use when tracking object persistence inside a zone and alerting when dwell thresholds are exceeded.
---

# Loitering Dwell Timer

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when tracking object persistence inside a zone and alerting when dwell thresholds are exceeded.

## Workflow

1. Track objects inside the zone over time.
2. Accumulate dwell time per ID.
3. Apply movement tolerance to avoid false resets.
4. Trigger alerts at threshold.
5. Reset on exit and log events.

## Output

Loitering detection with dwell timers.
