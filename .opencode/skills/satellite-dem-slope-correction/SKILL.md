---
name: DEM-Guided Terrain Slope Correction
description: Use when accounting for steep road inclines that warp pixel ground footprint dimensions.
---

# DEM-Guided Terrain Slope Correction

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when accounting for steep road inclines that warp pixel ground footprint dimensions.

## Workflow

1. Compute local slope from the DEM at each pixel.
2. Adjust the effective pixel footprint for the slope-induced scale change.
3. Resample to a constant ground-resolution grid.
4. Verify gradient roads no longer appear compressed or stretched.

## Output

Slope-corrected imagery with uniform ground sampling.
