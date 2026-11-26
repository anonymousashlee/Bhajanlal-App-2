---
name: LiDAR-Guided Depth Super-Resolution
description: Use when airborne LiDAR point clouds serve as geometric priors to sharpen orbital imagery.
---

# LiDAR-Guided Depth Super-Resolution

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when airborne LiDAR point clouds serve as geometric priors to sharpen orbital imagery.

## Workflow

1. Interpolate sparse LiDAR points into a dense depth map.
2. Condition the SR or restoration network on that depth map.
3. Let depth edges guide upscaling so structures stay crisp.
4. Verify depth-conditioned output against held-out LiDAR points.

## Output

Depth-guided sharp imagery with correct geometry.
