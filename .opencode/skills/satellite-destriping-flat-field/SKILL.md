---
name: Destriping & Flat-Field Calibration
description: Use when eliminating vertical push-broom sensor banding across CCD/CMOS detector arrays.
---

# Destriping & Flat-Field Calibration

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when eliminating vertical push-broom sensor banding across CCD/CMOS detector arrays.

## Workflow

1. Estimate per-detector gain and offset from flat-field or scene statistics.
2. Apply the correction column-wise to flatten detector response.
3. For residual stripes, use a low-rank or Fourier notch destriping pass.
4. Verify no horizontal features were attenuated along the road.

## Output

Stripe-free image with uniform detector response.
