---
name: SAR-Optical Cross-Modal Translation
description: Use when fusing Synthetic Aperture Radar backscatter with optical tiles during partial cloud cover.
---

# SAR-Optical Cross-Modal Translation

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when fusing Synthetic Aperture Radar backscatter with optical tiles during partial cloud cover.

## Workflow

1. Geometrically align SAR and optical acquisitions.
2. Translate SAR to optical appearance or fuse features with a cross-modal network.
3. Mask remaining cloud and use SAR-only confidence where optical is unusable.
4. Check specular road surfaces and target scattering behave as expected.

## Output

All-weather fused product covering cloudy acquisitions.
