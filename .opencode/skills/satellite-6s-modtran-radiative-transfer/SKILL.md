---
name: 6S & MODTRAN Radiative Transfer Correction
description: Use when converting raw Digital Numbers (DN) into true surface reflectance with radiative transfer models.
---

# 6S & MODTRAN Radiative Transfer Correction

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when converting raw Digital Numbers (DN) into true surface reflectance with radiative transfer models.

## Workflow

1. Gather acquisition metadata - solar angles, sensor, altitude, aerosol type.
2. Run 6S or MODTRAN to get the atmosphere transfer coefficients for the pass.
3. Apply the TOA reflectance equation and the atmospheric correction coefficients.
4. Validate against ground control reflectance panels or known land-cover spectra.

## Output

Atmospherically corrected surface reflectance product.
