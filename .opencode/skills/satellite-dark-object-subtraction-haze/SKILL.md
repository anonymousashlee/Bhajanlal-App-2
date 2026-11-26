---
name: Atmospheric Scattering & Haze Removal (Dark Object Subtraction)
description: Use when stripping Rayleigh and Mie scattering veils that wash out low-contrast road targets.
---

# Atmospheric Scattering & Haze Removal (Dark Object Subtraction)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when stripping Rayleigh and Mie scattering veils that wash out low-contrast road targets.

## Workflow

1. Find the darkest object in the scene (water, deep shadow) and assume it should be near zero.
2. Subtract that per-band offset from the whole image to remove the scattering veil.
3. Re-scale to the original dynamic range so radiometry stays comparable across passes.
4. Check that contrast on asphalt and silhouettes improved without crushing shadows.

## Output

Haze-stripped imagery with restored low-contrast detail.
