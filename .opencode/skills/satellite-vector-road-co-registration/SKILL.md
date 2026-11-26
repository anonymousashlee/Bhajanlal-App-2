---
name: Sub-Pixel Co-Registration with Vector Road Maps
description: Use when aligning OpenStreetMap/HD road vectors to pinpoint exact lanes and crosswalks.
---

# Sub-Pixel Co-Registration with Vector Road Maps

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when aligning OpenStreetMap/HD road vectors to pinpoint exact lanes and crosswalks.

## Workflow

1. Extract road centerlines from the image and from the vector map.
2. Align them with sub-pixel registration using mutual information.
3. Apply a smooth warp field, not a global shift alone.
4. Report residual alignment error per segment.

## Output

Image registered to road vectors at sub-pixel accuracy.
