---
name: Poisson-Gaussian Variance Stabilization (Anscombe Transform)
description: Use when converting signal-dependent photon noise into uniform additive noise for standard denoisers.
---

# Poisson-Gaussian Variance Stabilization (Anscombe Transform)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when converting signal-dependent photon noise into uniform additive noise for standard denoisers.

## Workflow

1. Apply the generalized Anscombe transform to the raw counts.
2. Run the denoiser in the stabilized domain where noise is approximately Gaussian.
3. Apply the exact unbiased inverse transform to return to counts.
4. Confirm brightness is unbiased after the round trip.

## Output

Denoised data with photon noise handled correctly.
