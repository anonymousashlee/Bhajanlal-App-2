---
name: ZFS Surveillance Pool Tuner
description: Use when optimizing ZFS recordsize and sync settings for continuous multi-stream video writes.
---

# ZFS Surveillance Pool Tuner

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when optimizing ZFS recordsize and sync settings for continuous multi-stream video writes.

## Workflow

1. Set recordsize to match video segment size.
2. Tune sync/async and ARC cache.
3. Enable compression and atime off.
4. Monitor write latency and IOPS.
5. Document pool configuration.

## Output

ZFS pool tuned for video writes.
