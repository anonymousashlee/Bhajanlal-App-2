---
name: VNIR + SWIR Spectral Fusion
description: Use when Short-Wave Infrared (1.2-2.5 um) must penetrate smoke/haze and distinguish synthetic fabrics from asphalt.
---

# VNIR + SWIR Spectral Fusion

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when Short-Wave Infrared (1.2-2.5 um) must penetrate smoke/haze and distinguish synthetic fabrics from asphalt.

## Workflow

1. Co-register VNIR and SWIR bands to a common grid.
2. Fuse with a pansharpening-style injection or a learned fusion network.
3. Use SWIR absorption features to separate fabric from mineral surfaces.
4. Check fusion did not distort diagnostic spectral features.

## Output

Fused VNIR-SWIR product with haze-penetrating material contrast.
