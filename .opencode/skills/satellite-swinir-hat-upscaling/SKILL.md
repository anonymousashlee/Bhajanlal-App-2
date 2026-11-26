---
name: SwinIR & HAT Transformer Upscaling
description: Use when applying Hybrid Attention or Swin transformer upscalers that capture long-range road geometry while sharpening tiny targets.
---

# SwinIR & HAT Transformer Upscaling

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when applying Hybrid Attention or Swin transformer upscalers that capture long-range road geometry while sharpening tiny targets.

## Workflow

1. Choose the classical or lightweight SwinIR variant to match available VRAM.
2. Feed patches large enough (64x64+) so attention sees whole road segments.
3. Run overlapping-window inference to avoid seam artifacts between patches.
4. Confirm lane lines and silhouettes stay continuous across patch borders.

## Output

Transformer-upscaled tiles with coherent long-range structure.
