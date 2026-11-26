---
name: 3D Gaussian Splatting / NeRF for Satellite Multi-View
description: Use when reconstructing photorealistic, arbitrary-angle 3D road scenes from multiple orbital captures.
---

# 3D Gaussian Splatting / NeRF for Satellite Multi-View

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when reconstructing photorealistic, arbitrary-angle 3D road scenes from multiple orbital captures.

## Workflow

1. Collect multi-view captures with known or estimated camera poses.
2. Train a 3D Gaussian or NeRF reconstruction of the scene.
3. Render novel viewpoints to disambiguate occluded road areas.
4. Flag hallucinated regions that lack multi-view support.

## Output

Arbitrary-angle renders of the road scene from multi-view data.
