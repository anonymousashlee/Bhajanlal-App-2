---
name: cesium-frustum-culling-optimizer
description: Use when prioritizing GPU memory for foreground tiles in the active camera frustum.
---

# cesium-frustum-culling-optimizer

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when prioritizing GPU memory for foreground tiles in the active camera frustum.

## Workflow

1. Enable frustum culling in Cesium.
2. Tune tile loading priorities by frustum.
3. Free GPU memory for off-screen tiles.
4. Profile frame time.

## Output

Optimized frustum-based tile loading.
