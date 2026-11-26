---
name: websocket-backpressure-handler
description: Use when dropping stale telemetry packets instead of lagging the render loop.
---

# websocket-backpressure-handler

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when dropping stale telemetry packets instead of lagging the render loop.

## Workflow

1. Handle WS backpressure.
2. Drop stale packets.
3. Keep render loop smooth.
4. Validate.

## Output

Backpressure-handled WS.
