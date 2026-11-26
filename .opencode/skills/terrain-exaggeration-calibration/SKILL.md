---
name: terrain-exaggeration-calibration
description: Use when tuning terrain elevation meshes so camera projections sit flush on the ground.
---

# terrain-exaggeration-calibration

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when tuning terrain elevation meshes so camera projections sit flush on the ground.

## Workflow

1. Set terrain exaggeration factor in Cesium.
2. Align camera projections and viewsheds to exaggerated terrain.
3. Verify markers don't clip underground.
4. Tune per scene for readability.

## Output

Terrain-aligned camera projections.
