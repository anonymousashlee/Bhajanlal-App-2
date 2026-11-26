---
name: Road Centerline & Mask Extraction
description: Use when isolating road surfaces to constrain search areas and eliminate background clutter.
---

# Road Centerline & Mask Extraction

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when isolating road surfaces to constrain search areas and eliminate background clutter.

## Workflow

1. Segment road surface with a semantic model or spectral rule set.
2. Extract centerlines and lane boundaries from the mask.
3. Grow or shrink the mask to include curbs and sidewalks.
4. Use the mask to bound detection and change-analysis regions.

## Output

Road mask and centerlines constraining downstream analysis.
