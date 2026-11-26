---
name: glsl-de-haze-atmospheric-filter
description: Use when implementing dark-channel prior dehazing for foggy street cameras and aerial imagery.
---

# glsl-de-haze-atmospheric-filter

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when implementing dark-channel prior dehazing for foggy street cameras and aerial imagery.

## Workflow

1. Implement DCP dehazing.
2. Estimate transmission.
3. Recover radiance.
4. Validate clarity.

## Output

Dehazed camera/aerial imagery.
