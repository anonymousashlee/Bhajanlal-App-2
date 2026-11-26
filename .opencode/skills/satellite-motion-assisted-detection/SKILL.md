---
name: Motion-Assisted Detection (Optical Flow / Frame Differencing)
description: Use when detecting 1-2 pixel moving entities across sequential video satellite frames by velocity vectors.
---

# Motion-Assisted Detection (Optical Flow / Frame Differencing)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when detecting 1-2 pixel moving entities across sequential video satellite frames by velocity vectors.

## Workflow

1. Estimate optical flow or frame differences on co-registered frames.
2. Cluster motion pixels into candidate moving objects.
3. Filter by velocity range consistent with road traffic and pedestrians.
4. Confirm detections track consistently across at least 3 frames.

## Output

Motion-based candidate list of tiny moving targets.
