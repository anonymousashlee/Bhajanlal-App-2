---
name: Wavelet Thresholding (VisuShrink/BayesShrink)
description: Use when high-frequency sensor noise must be stripped across wavelet sub-bands.
---

# Wavelet Thresholding (VisuShrink/BayesShrink)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when high-frequency sensor noise must be stripped across wavelet sub-bands.

## Workflow

1. Decompose into wavelet sub-bands.
2. Apply soft/hard thresholding per sub-band.
3. Use BayesShrink for adaptive thresholds.
4. Reconstruct and inspect for over-smoothing.

## Output

Wavelet-denoised frames.
