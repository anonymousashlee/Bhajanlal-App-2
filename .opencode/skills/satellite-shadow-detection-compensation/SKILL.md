---
name: Shadow Detection & Radiometric Compensation
description: Use when brightening pedestrians inside building or tree shadows without blowing out sunlit asphalt.
---

# Shadow Detection & Radiometric Compensation

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when brightening pedestrians inside building or tree shadows without blowing out sunlit asphalt.

## Workflow

1. Build a shadow mask from chromaticity, brightness, and NIR ratios.
2. Estimate the illumination ratio between shadowed and sunlit regions per band.
3. Brighten shadowed pixels by that ratio while preserving their texture.
4. Clamp highlights so sunlit road areas keep their original radiometry.

## Output

Shadow-balanced image where figures stay visible in shade.
