---
name: hls-adaptive-bitrate-lock
description: Use when forcing hls.js players to lock onto the highest available resolution variant instead of auto-downgrading.
---

# hls-adaptive-bitrate-lock

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when forcing hls.js players to lock onto the highest available resolution variant instead of auto-downgrading.

## Workflow

1. Configure hls.js to start at highest level.
2. Disable auto quality switching.
3. Handle bandwidth errors gracefully.
4. Validate crisp playback.

## Output

Locked high-res HLS playback.
