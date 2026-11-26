---
name: Multi-Frame Super-Resolution (MFSR)
description: Use when fusing multiple slightly shifted satellite passes of the same road to recover sub-pixel detail beyond a single frame GSD.
---

# Multi-Frame Super-Resolution (MFSR)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when fusing multiple slightly shifted satellite passes of the same road to recover sub-pixel detail beyond a single frame GSD.

## Workflow

1. Register the frame stack to sub-pixel accuracy first (see satellite-subpixel-shift-registration).
2. Estimate each frame relative shift and weight frames by sharpness and cloud cover.
3. Fuse into a high-resolution grid with robust averaging that rejects outlier frames.
4. Mask or ghost-check moving objects so cars and pedestrians are not doubled.

## Output

One super-resolved frame built from a burst of shifted low-res captures.
