---
name: smart-crop-zoom-interpolator
description: Use when using Lanczos resampling instead of blurry bilinear scaling when digitally zooming into CCTV feeds.
---

# smart-crop-zoom-interpolator

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when using Lanczos resampling instead of blurry bilinear scaling when digitally zooming into CCTV feeds.

## Workflow

1. Replace bilinear with Lanczos.
2. Apply on zoom.
3. Validate sharpness.
4. Profile performance.

## Output

Sharp digital zoom.
