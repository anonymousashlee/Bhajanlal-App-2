---
name: Blind Super-Resolution (BSRGAN)
description: Use when unknown compression artifacts and sensor blur kernels must be handled.
---

# Blind Super-Resolution (BSRGAN)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when unknown compression artifacts and sensor blur kernels must be handled.

## Workflow

1. Model realistic degradations: blur, noise, compression, downsample.
2. Train residual learning to invert the degradation.
3. Validate on real held-out tiles, not synthetic bicubic pairs.
4. Use as default for unknown public camera streams.

## Output

Robust super-resolution for unknown degradations.
