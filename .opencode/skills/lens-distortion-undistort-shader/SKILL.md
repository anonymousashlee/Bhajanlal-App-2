---
name: lens-distortion-undistort-shader
description: Use when applying barrel/pincushion radial correction to wide-angle fisheye street cameras.
---

# lens-distortion-undistort-shader

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when applying barrel/pincushion radial correction to wide-angle fisheye street cameras.

## Workflow

1. Implement radial undistortion shader.
2. Tune k1/k2 coefficients.
3. Apply to camera texture.
4. Validate straight lines.

## Output

Undistorted camera feeds.
