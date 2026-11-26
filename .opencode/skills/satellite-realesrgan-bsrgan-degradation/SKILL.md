---
name: Real-ESRGAN & BSRGAN Degradation Modeling
description: Use when training or fine-tuning SR networks on realistic sensor blur, compression, and atmospheric noise instead of simple bicubic downsampling.
---

# Real-ESRGAN & BSRGAN Degradation Modeling

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when training or fine-tuning SR networks on realistic sensor blur, compression, and atmospheric noise instead of simple bicubic downsampling.

## Workflow

1. Build a degradation pipeline - blur (realistic PSF), noise (shot/read), JPEG or JPEG2000, downsample.
2. Match degradation parameters to the target satellite known noise and compression characteristics.
3. Train with perceptual plus GAN loss (Real-ESRGAN) or residual learning (BSRGAN).
4. Validate on real held-out tiles, never on synthetic bicubic pairs alone.

## Output

SR model robust to real satellite degradation rather than bicubic only.
