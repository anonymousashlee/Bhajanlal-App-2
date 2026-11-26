---
name: Rational Polynomial Coefficient (RPC) Orthorectification
description: Use when removing terrain tilt and camera perspective distortion so roads align true to scale.
---

# Rational Polynomial Coefficient (RPC) Orthorectification

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when removing terrain tilt and camera perspective distortion so roads align true to scale.

## Workflow

1. Load the RPCs supplied with the image and a coarse DEM.
2. Resample to a uniform ground grid using the RPC forward model.
3. Refine RPCs with ground control points if bias remains.
4. Check road widths match their true map dimensions.

## Output

Orthorectified image geometrically true to the ground grid.
