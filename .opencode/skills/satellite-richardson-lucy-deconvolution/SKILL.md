---
name: Richardson-Lucy Iterative Deconvolution
description: Use when restoring sharp edges on high-contrast targets using Poisson noise statistics via iterative Richardson-Lucy deconvolution.
---

# Richardson-Lucy Iterative Deconvolution

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when restoring sharp edges on high-contrast targets using Poisson noise statistics via iterative Richardson-Lucy deconvolution.

## Workflow

1. Start from the PSF estimate and run 10-30 RL iterations.
2. Stop when noise begins to blossom in flat road regions.
3. Add a mild total-variation penalty or use early stopping as regularization.
4. Compare before/after on pedestrian silhouettes for over-sharpening halos.

## Output

Poisson-aware deconvolution with crisp high-contrast edges.
