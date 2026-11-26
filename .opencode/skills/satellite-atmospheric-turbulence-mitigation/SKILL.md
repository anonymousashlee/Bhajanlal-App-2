---
name: Atmospheric Turbulence Mitigation
description: Use when removing heat-haze shimmer rising off sun-baked asphalt roads.
---

# Atmospheric Turbulence Mitigation

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when removing heat-haze shimmer rising off sun-baked asphalt roads.

## Workflow

1. Estimate turbulence strength from frame sequences or single-image priors.
2. Apply a turbulence restoration network or multi-frame lucky selection.
3. For single images, use a physics-guided dehaze plus deblur cascade.
4. Confirm distant road features stop shimmering.

## Output

Image with atmospheric shimmer suppressed.
