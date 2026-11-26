---
name: elevation-clamping-fix
description: Use when preventing camera markers and viewshed polygons from clipping underground.
---

# elevation-clamping-fix

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when preventing camera markers and viewshed polygons from clipping underground.

## Workflow

1. Clamp entities to terrain height.
2. Use sampleTerrain for accurate elevation.
3. Offset slightly above ground.
4. Validate no underground clipping.

## Output

Ground-clamped markers and viewsheds.
