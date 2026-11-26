---
name: Wiener Filtering
description: Use when suppressing optical blur in the Fourier domain while bounding noise amplification with a Wiener filter.
---

# Wiener Filtering

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when suppressing optical blur in the Fourier domain while bounding noise amplification with a Wiener filter.

## Workflow

1. Estimate the OTF from the PSF and the noise-to-signal power ratio.
2. Apply the Wiener filter in the frequency domain.
3. Clip the filter gain to avoid noise blow-up in dark areas.
4. Verify no periodic artifacts from FFT tiling.

## Output

Blur-suppressed image with controlled noise.
