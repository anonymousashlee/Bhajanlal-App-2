---
name: rate-limit-exponential-backoff
description: Use when preventing third-party imagery providers from throttling your IP during rapid zooming.
---

# rate-limit-exponential-backoff

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when preventing third-party imagery providers from throttling your IP during rapid zooming.

## Workflow

1. Implement backoff.
2. Handle 429s.
3. Retry smartly.
4. Validate.

## Output

Throttle-safe zooming.
