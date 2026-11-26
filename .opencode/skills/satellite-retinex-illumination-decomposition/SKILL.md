---
name: Retinex Illumination-Reflectance Decomposition
description: Use when separating uneven lighting conditions from true object surface albedo.
---

# Retinex Illumination-Reflectance Decomposition

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when separating uneven lighting conditions from true object surface albedo.

## Workflow

1. Estimate the illumination field with a large-scale Gaussian or Retinex network.
2. Divide (or log-subtract) illumination to recover reflectance.
3. Re-composite with a softened illumination so the result does not look flat.
4. Check that clothing and skin tones stay distinguishable from asphalt.

## Output

Reflectance image free of uneven illumination gradients.
