---
name: Noise2Void / Self-Supervised Denoising
description: Use when training denoisers directly on noisy orbital imagery without clean ground truth.
---

# Noise2Void / Self-Supervised Denoising

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when training denoisers directly on noisy orbital imagery without clean ground truth.

## Workflow

1. Hide the center pixel of each patch so the network cannot copy noise.
2. Train to predict the hidden pixel from its blind-spot context.
3. Validate with SURE or noisy-to-noisy consistency, not PSNR against clean data.
4. Confirm real structures were not smoothed out of existence.

## Output

Self-supervised denoiser trained on noisy-only data.
