---
name: CLAHE (Contrast Limited Adaptive Histogram Equalization)
description: Use when enhancing local micro-contrast on uniform gray roads so tiny figures stand out.
---

# CLAHE (Contrast Limited Adaptive Histogram Equalization)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when enhancing local micro-contrast on uniform gray roads so tiny figures stand out.

## Workflow

1. Tile the image and equalize each tile histogram with a clip limit.
2. Interpolate between tiles to avoid block seams.
3. Apply on the luminance channel only to prevent color shifts.
4. Lower the clip limit if noise on flat asphalt is amplified.

## Output

Locally contrast-enhanced image where small targets pop.
