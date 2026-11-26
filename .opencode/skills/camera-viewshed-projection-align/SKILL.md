---
name: camera-viewshed-projection-align
description: Use when calibrating FOV, pitch, yaw, and roll so video textures map cleanly onto 3D geometry.
---

# camera-viewshed-projection-align

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when calibrating FOV, pitch, yaw, and roll so video textures map cleanly onto 3D geometry.

## Workflow

1. Calibrate camera intrinsics (FOV).
2. Set pitch/yaw/roll on the viewshed.
3. Align texture projection.
4. Validate no distortion.

## Output

Aligned camera viewshed projections.
