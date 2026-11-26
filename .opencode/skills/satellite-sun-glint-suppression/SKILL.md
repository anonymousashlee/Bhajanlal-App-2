---
name: Sun-Glint & Specular Reflection Suppression
description: Use when eliminating blinding reflections off car windshields and wet pavement that saturate nearby pixels.
---

# Sun-Glint & Specular Reflection Suppression

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when eliminating blinding reflections off car windshields and wet pavement that saturate nearby pixels.

## Workflow

1. Flag saturated or near-saturated specular pixels using NIR polarization or intensity thresholds.
2. Estimate the glint component and subtract it per band.
3. Inpaint flagged pixels from surrounding texture or from a second pass.
4. Verify figures near glint regions are no longer masked by bloom.

## Output

Glint-suppressed imagery with recovered detail around reflections.
