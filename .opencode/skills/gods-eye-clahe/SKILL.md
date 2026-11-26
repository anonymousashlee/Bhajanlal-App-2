---
name: CLAHE
description: Use when local contrast in shadows must be boosted without blowing out headlights.
---

# CLAHE

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when local contrast in shadows must be boosted without blowing out headlights.

## Workflow

1. Tile the image and equalize each tile histogram.
2. Interpolate between tiles to avoid seams.
3. Apply on luminance channel only.
4. Lower clip limit if asphalt noise amplifies.

## Output

Locally contrast-enhanced frames.
