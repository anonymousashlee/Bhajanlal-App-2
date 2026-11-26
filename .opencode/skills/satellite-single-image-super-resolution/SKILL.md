---
name: Single-Image Super-Resolution (SISR)
description: Use when upscaling low-resolution satellite tiles with deep convolutional or transformer networks to recover sub-pixel road and pedestrian detail.
---

# Single-Image Super-Resolution (SISR)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when upscaling low-resolution satellite tiles with deep convolutional or transformer networks to recover sub-pixel road and pedestrian detail.

## Workflow

1. Confirm the source GSD and pick an integer scale (2x/4x) whose training degradation matches the sensor.
2. Run tiled inference with overlap so large scenes stay inside GPU memory.
3. Prefer transformer SISR (SwinIR/HAT class) when road geometry and tiny figures must stay crisp.
4. Inspect upscaled crops at 100% for hallucinated texture before accepting the result.

## Output

Sharper satellite tiles at 2x-4x scale with recovered sub-pixel detail.
