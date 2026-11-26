---
name: redis-tile-and-snapshot-cache
description: Use when caching frequently requested imagery tiles and API responses locally.
---

# redis-tile-and-snapshot-cache

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when caching frequently requested imagery tiles and API responses locally.

## Workflow

1. Set up Redis cache.
2. Cache tiles/snapshots.
3. Evict stale.
4. Validate.

## Output

Cached tiles/snapshots.
