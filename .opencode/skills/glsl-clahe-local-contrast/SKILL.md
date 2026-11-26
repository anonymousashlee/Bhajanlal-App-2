---
name: glsl-clahe-local-contrast
description: Use when applying adaptive histogram equalization to reveal details in dark shadows or blown-out highlights.
---

# glsl-clahe-local-contrast

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when applying adaptive histogram equalization to reveal details in dark shadows or blown-out highlights.

## Workflow

1. Implement CLAHE in shader.
2. Tune clip limit.
3. Apply to luminance.
4. Validate detail.

## Output

CLAHE-enhanced details.
