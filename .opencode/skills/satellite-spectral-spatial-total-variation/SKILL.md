---
name: Spectral-Spatial Total Variation Denoising
description: Use when exploiting correlations across RGB and NIR bands to isolate true physical objects from noise.
---

# Spectral-Spatial Total Variation Denoising

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when exploiting correlations across RGB and NIR bands to isolate true physical objects from noise.

## Workflow

1. Jointly denoise all bands with a shared spatial gradient map.
2. Add a spectral consistency term so band ratios stay physically valid.
3. Sweep the TV weight against small-target retention.
4. Confirm NIR vegetation and skin signatures remain intact.

## Output

Jointly denoised bands with spectral relationships preserved.
