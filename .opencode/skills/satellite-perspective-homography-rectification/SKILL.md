---
name: Perspective & Homography Rectification
description: Use when warping oblique aerial/satellite views into top-down nadir geometry.
---

# Perspective & Homography Rectification

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when warping oblique aerial/satellite views into top-down nadir geometry.

## Workflow

1. Identify four or more correspondences on the ground plane.
2. Solve the homography and warp with a high-quality resampler.
3. Mask areas outside the valid warped footprint.
4. Verify straight roads remain straight after the warp.

## Output

Rectified top-down view of oblique imagery.
