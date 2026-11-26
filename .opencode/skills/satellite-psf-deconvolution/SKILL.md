---
name: Sensor PSF Estimation & Deconvolution
description: Use when modeling the optical diffraction and detector blur kernel of a satellite telescope to restore sharp edges.
---

# Sensor PSF Estimation & Deconvolution

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when modeling the optical diffraction and detector blur kernel of a satellite telescope to restore sharp edges.

## Workflow

1. Obtain or estimate the sensor PSF from MTF calibration or point sources.
2. Apply regularized deconvolution (Wiener or Richardson-Lucy) with that PSF.
3. Tune regularization so noise on asphalt is not amplified.
4. Validate edge sharpness against a known slanted-edge target such as a crosswalk.

## Output

Deconvolved tile with diffraction-limited sharpness.
