---
name: Swin-Conv-UNet (SCUNet) Blind Denoising
description: Use when handling mixed sensor noise levels across varying illumination zones.
---

# Swin-Conv-UNet (SCUNet) Blind Denoising

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when handling mixed sensor noise levels across varying illumination zones.

## Workflow

1. Feed the image to a blind-denoising network without specifying the noise level.
2. Tile large scenes with overlap and blend tile borders.
3. Let the model adapt to per-region noise differences (sunlit vs shadow).
4. Check that texture on asphalt was not over-smoothed.

## Output

Uniformly denoised scene despite mixed noise levels.
