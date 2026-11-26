---
name: Digital Surface Model (DSM) True-Ortho Projection
description: Use when eliminating building lean so tall structures do not occlude adjacent sidewalks and roads.
---

# Digital Surface Model (DSM) True-Ortho Projection

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when eliminating building lean so tall structures do not occlude adjacent sidewalks and roads.

## Workflow

1. Build or load a DSM covering the scene.
2. Reproject each pixel using its DSM height to remove occlusions.
3. Fill occluded areas from other passes or inpainting.
4. Confirm sidewalks next to buildings are visible and not hidden.

## Output

True-ortho image with building lean removed.
