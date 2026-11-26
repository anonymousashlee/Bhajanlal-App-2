---
name: Off-Nadir Angle Compensation
description: Use when correcting foreshortening distortion when a satellite captures a road at a 20-35 degree slant angle.
---

# Off-Nadir Angle Compensation

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when correcting foreshortening distortion when a satellite captures a road at a 20-35 degree slant angle.

## Workflow

1. Read the off-nadir angle and look direction from the metadata.
2. Project the image to nadir using the RPC model and DEM.
3. Resample with a PSF-aware kernel to avoid extra blur.
4. Confirm road widths and lengths are restored to true scale.

## Output

Nadir-equivalent view with foreshortening removed.
