---
name: Dark Channel Prior Deblurring
description: Use when exploiting dark shadow pixels cast by pedestrians to estimate exact blur kernels.
---

# Dark Channel Prior Deblurring

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when exploiting dark shadow pixels cast by pedestrians to estimate exact blur kernels.

## Workflow

1. Detect dark-channel pixels (shadows, dark clothing) as blur references.
2. Estimate the kernel from those high-contrast dark regions.
3. Apply non-blind deconvolution with the estimated kernel.
4. Cross-check the kernel against the sensor known PSF bounds.

## Output

Kernel estimated from scene shadows, applied for deblur.
