---
name: Wavelet-Domain Super-Resolution
description: Use when reconstructing high-frequency sub-bands separately in the discrete wavelet domain to recover detail in satellite tiles.
---

# Wavelet-Domain Super-Resolution

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when reconstructing high-frequency sub-bands separately in the discrete wavelet domain to recover detail in satellite tiles.

## Workflow

1. Decompose the low-res tile into wavelet sub-bands with a 2-level DWT.
2. Predict or interpolate the high-frequency sub-bands with a small network.
3. Reconstruct with inverse DWT and check for ringing along lane lines.
4. Blend with a spatial-domain SR result if artifacts appear.

## Output

Detail-restored tile via wavelet sub-band reconstruction.
