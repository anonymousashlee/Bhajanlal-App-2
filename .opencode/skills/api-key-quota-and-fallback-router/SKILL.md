---
name: api-key-quota-and-fallback-router
description: Use when gracefully falling back from Google 3D Tiles to Cesium Ion or Esri without sudden quality drops.
---

# api-key-quota-and-fallback-router

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when gracefully falling back from Google 3D Tiles to Cesium Ion or Esri without sudden quality drops.

## Workflow

1. Route by quota. Track per-provider request counts against daily/monthly quotas (with a safety margin, e.g. 0.9) and pick the highest-quality provider that still has budget.
2. Fallback gracefully. When the current provider exhausts its quota, switch to the next-best available provider (Google 3D Tiles -> Cesium Ion -> Esri), preferring a one-tier step to avoid jarring jumps.
3. Avoid quality drops. Only allow a switch if the quality delta is <= 1 tier (or forced by exhaustion); otherwise defer and keep the current provider to prevent flicker.
4. Validate. Sanity-check the routing decision (known provider, non-negative quota remaining) and recover to the lowest-quality always-available provider if invalid.

## Output

Quota-aware fallback routing.

## Applied example

See `examples/quota-fallback-router.js` (core router) and `examples/quota-fallback-applied.js` (full pipeline with report).
