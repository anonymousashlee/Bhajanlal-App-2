---
name: Shadow-Length Height Estimation
description: Use when calculating the exact height of a tiny road object from sun azimuth, elevation angle, and cast shadow length.
---

# Shadow-Length Height Estimation

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when calculating the exact height of a tiny road object from sun azimuth, elevation angle, and cast shadow length.

## Workflow

1. Get sun elevation and azimuth for the acquisition timestamp.
2. Measure the cast shadow length from the object base to its tip.
3. Compute height = shadow length x tan(sun elevation), correcting for slope.
4. Sanity-check against known object heights (poles, cars, people).

## Output

Estimated object heights from sun geometry and shadows.
