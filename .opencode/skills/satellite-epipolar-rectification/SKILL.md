---
name: Epipolar Geometry Alignment
description: Use when rectifying stereo pairs so parallax shifts directly reveal tiny objects standing above the road plane.
---

# Epipolar Geometry Alignment

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when rectifying stereo pairs so parallax shifts directly reveal tiny objects standing above the road plane.

## Workflow

1. Estimate the fundamental matrix from stereo correspondences.
2. Rectify both images so epipolar lines are horizontal.
3. Compute disparity and convert to height above the road plane.
4. Flag objects whose disparity indicates vertical relief.

## Output

Rectified stereo pair with clean vertical parallax.
