---
name: Camera Health Watchdog
description: Use when writing heartbeat scripts to detect frozen frames, black screens, or offline IP cameras.
---

# Camera Health Watchdog

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when writing heartbeat scripts to detect frozen frames, black screens, or offline IP cameras.

## Workflow

1. Periodically grab a frame from each camera.
2. Compute frame hash / motion / brightness metrics.
3. Detect freeze, black screen, or offline state.
4. Emit alerts and attempt reconnect.
5. Log incidents with timestamps.

## Output

Automated camera uptime and quality watchdog.
