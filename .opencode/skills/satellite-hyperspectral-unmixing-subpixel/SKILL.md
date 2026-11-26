---
name: Hyperspectral Unmixing (Sub-Pixel Target Detection)
description: Use when decomposing a single mixed pixel's spectrum to detect fractional presence of human clothing/skin materials.
---

# Hyperspectral Unmixing (Sub-Pixel Target Detection)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when decomposing a single mixed pixel's spectrum to detect fractional presence of human clothing/skin materials.

## Workflow

1. Extract endmembers for asphalt, skin, common fabrics, and background.
2. Solve linear or non-linear unmixing to get fractional abundances.
3. Flag pixels where a target endmember exceeds an abundance threshold.
4. Validate fractions against known-material reference spectra.

## Output

Sub-pixel material abundance maps flagging human presence.
