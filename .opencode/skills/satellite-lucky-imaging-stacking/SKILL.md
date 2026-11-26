---
name: Lucky Imaging Frame Selection
description: Use when selecting and stacking the sharpest micro-exposures from burst captures.
---

# Lucky Imaging Frame Selection

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when selecting and stacking the sharpest micro-exposures from burst captures.

## Workflow

1. Score each frame sharpness with variance of Laplacian or an MTF estimate.
2. Keep the top fraction of frames and align them.
3. Median-combine the aligned stack to reject noise and outliers.
4. Use the combined frame as input to SR or detection.

## Output

Low-noise, sharp stack composite.
