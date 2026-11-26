---
name: Non-Uniform / Spatially Varying Deblurring
description: Use when correcting off-nadir perspective distortion and lens aberrations that blur differently across wide swath edges.
---

# Non-Uniform / Spatially Varying Deblurring

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when correcting off-nadir perspective distortion and lens aberrations that blur differently across wide swath edges.

## Workflow

1. Model the PSF as a spatially varying field by tiling the scene into PSF zones.
2. Apply per-tile deconvolution with overlap blending.
3. Correct residual geometric warp from the same field.
4. Check that sharpness is uniform from scene center to edge.

## Output

Uniformly sharp wide-swath image.
