---
name: tile-request-throttling-manager
description: Use when batching and prioritizing tile requests to prevent rate-limit downgrades.
---

# tile-request-throttling-manager

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when batching and prioritizing tile requests to prevent rate-limit downgrades.

## Workflow

1. Batch tile requests with a queue.
2. Prioritize by frustum and LOD.
3. Apply rate limits per provider.
4. Monitor 429s.

## Output

Throttled, prioritized tile requests.
