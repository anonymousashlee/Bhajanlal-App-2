---
name: Circular Buffer Retention
description: Use when writing cron/systemd scripts to prune oldest recordings when disk usage hits 85%.
---

# Circular Buffer Retention

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when writing cron/systemd scripts to prune oldest recordings when disk usage hits 85%.

## Workflow

1. Monitor disk usage per camera pool.
2. Define retention policies by priority.
3. Prune oldest files when threshold exceeded.
4. Protect active/alert clips.
5. Log deletions and report freed space.

## Output

Automated retention pruning scripts.
