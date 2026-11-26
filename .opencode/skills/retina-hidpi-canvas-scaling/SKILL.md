---
name: retina-hidpi-canvas-scaling
description: Use when configuring viewer.resolutionScale for crisp rendering on 4K and Retina displays.
---

# retina-hidpi-canvas-scaling

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when configuring viewer.resolutionScale for crisp rendering on 4K and Retina displays.

## Workflow

1. Detect devicePixelRatio.
2. Set viewer.resolutionScale accordingly.
3. Cap scale on low-end GPUs.
4. Verify crispness on Retina/4K.

## Output

Crisp HiDPI canvas rendering.
