---
name: Raw Sensor Shot & Read Noise Modeling
description: Use when denoising linear raw imagery before demosaicing or gamma compression destroys faint signals.
---

# Raw Sensor Shot & Read Noise Modeling

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when denoising linear raw imagery before demosaicing or gamma compression destroys faint signals.

## Workflow

1. Model shot noise as Poisson (signal-dependent) and read noise as Gaussian.
2. Fit noise parameters from flat frames or per-pixel variance sweeps.
3. Denoise in linear space with a noise-aware loss or filter.
4. Only then apply demosaicing, gamma, and resampling.

## Output

Clean linear raw data with faint signals preserved.
