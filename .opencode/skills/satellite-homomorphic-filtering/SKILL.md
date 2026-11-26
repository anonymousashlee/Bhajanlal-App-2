---
name: Homomorphic Filtering
description: Use when simultaneously normalizing uneven road illumination and boosting high-frequency edge contrast.
---

# Homomorphic Filtering

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when simultaneously normalizing uneven road illumination and boosting high-frequency edge contrast.

## Workflow

1. Take the log of the image to separate illumination and reflectance multiplicatively.
2. Apply a high-pass filter in the frequency domain to attenuate low-frequency lighting.
3. Exponentiate back and clamp to the valid range.
4. Confirm shadows were flattened without ringing along curbs.

## Output

Evenly lit image with boosted edge contrast.
