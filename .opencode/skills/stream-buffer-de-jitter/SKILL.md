---
name: stream-buffer-de-jitter
description: Use when smoothing out choppy public camera frame rates with frame interpolation.
---

# stream-buffer-de-jitter

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when smoothing out choppy public camera frame rates with frame interpolation.

## Workflow

1. Buffer frames with jitter tolerance.
2. Interpolate missing frames.
3. Drop late frames.
4. Validate smoothness.

## Output

De-jittered camera streams.
