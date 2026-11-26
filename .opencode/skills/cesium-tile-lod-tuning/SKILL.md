---
name: cesium-tile-lod-tuning
description: Use when adjusting maximumScreenSpaceError to force higher-detail 3D tile loading at close range.
---

# cesium-tile-lod-tuning

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when adjusting maximumScreenSpaceError to force higher-detail 3D tile loading at close range.

## Workflow

1. Open the Cesium viewer options and locate maximumScreenSpaceError.
2. Lower the value (e.g. 8-16) to force higher-detail tiles at close range.
3. Raise it on low-end GPUs to protect frame rate.
4. Benchmark tile load time vs visual quality.

## Output

Sharper close-range 3D tiles with balanced performance.
