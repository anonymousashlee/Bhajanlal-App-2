---
name: Total Variation (TV) Regularized Deconvolution
description: Use when sharpening object boundaries while keeping smooth road surfaces flat via total-variation regularized deconvolution.
---

# Total Variation (TV) Regularized Deconvolution

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when sharpening object boundaries while keeping smooth road surfaces flat via total-variation regularized deconvolution.

## Workflow

1. Solve the deconvolution with a TV penalty (Chambolle or primal-dual solver).
2. Sweep the TV weight - too high staircases asphalt, too low leaves noise.
3. Preserve radiometry so the TV term does not shift reflectance values.
4. Inspect pedestrian silhouettes for blocky edges.

## Output

Sharp boundaries with flat, noise-free road surfaces.
