---
name: Sub-Pixel Centroid Localization
description: Use when computing intensity-weighted centers of mass to track pedestrian positions with sub-pixel precision.
---

# Sub-Pixel Centroid Localization

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when computing intensity-weighted centers of mass to track pedestrian positions with sub-pixel precision.

## Workflow

1. Isolate the target blob from the local background.
2. Compute the intensity-weighted centroid within a small window.
3. Correct for background bias with a local mean subtraction.
4. Report coordinates with a stated sub-pixel uncertainty.

## Output

Sub-pixel target coordinates with uncertainty.
