---
name: Multi-View Stereo (MVS) 3D Reconstruction
description: Use when rebuilding sub-meter elevation profiles from stereo satellite pairs to detect vertical relief.
---

# Multi-View Stereo (MVS) 3D Reconstruction

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when rebuilding sub-meter elevation profiles from stereo satellite pairs to detect vertical relief.

## Workflow

1. Rectify the stereo pair and match features across views.
2. Compute a dense depth or point cloud with an MVS method.
3. Filter depth by photometric consistency and DEM sanity checks.
4. Use the elevation output to identify objects standing above the road plane.

## Output

Sub-meter 3D reconstruction of the road scene.
