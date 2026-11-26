---
name: Motion-Triggered Prebuffer
description: Use when maintaining a 5-second RAM ring buffer to save pre-event footage upon motion triggers.
---

# Motion-Triggered Prebuffer

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when maintaining a 5-second RAM ring buffer to save pre-event footage upon motion triggers.

## Workflow

1. Maintain in-memory ring buffer of frames.
2. On trigger, flush pre + post event footage.
3. Write clips to disk with metadata.
4. Tune buffer duration and size.
5. Handle concurrent triggers.

## Output

Pre-event capture on motion triggers.
