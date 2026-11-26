---
name: Temporal Change Detection (Background Subtraction)
description: Use when comparing a current pass against a clear historical reference of the exact same road to isolate newly appeared pedestrians.
---

# Temporal Change Detection (Background Subtraction)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when comparing a current pass against a clear historical reference of the exact same road to isolate newly appeared pedestrians.

## Workflow

1. Co-register the current and reference images to sub-pixel accuracy.
2. Normalize radiometry so illumination differences do not read as change.
3. Compute a change mask with a threshold tuned on known-static regions.
4. Classify compact change blobs above the road plane as candidate targets.

## Output

Change mask isolating newly appeared objects on the road.
