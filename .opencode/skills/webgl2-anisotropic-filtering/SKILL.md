---
name: webgl2-anisotropic-filtering
description: Use when enabling maximum anisotropic texture filtering on ground imagery tiles.
---

# webgl2-anisotropic-filtering

Part of the **Bhajanlal** model-building skill library. Pillar: 105. God's Eye View - OpenCode Cesium/GLSL/Node Skills (100 skills)

Use when enabling maximum anisotropic texture filtering on ground imagery tiles.

## Workflow

1. Query max anisotropy from WebGL2.
2. Apply to imagery samplers.
3. Fallback gracefully if unsupported.
4. Validate oblique-angle sharpness.

## Output

Anisotropic-filtered ground tiles.
