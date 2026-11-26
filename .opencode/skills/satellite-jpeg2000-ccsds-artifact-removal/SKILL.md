---
name: JPEG2000 & CCSDS Downlink Artifact Removal
description: Use when eliminating ringing and blocking artifacts caused by onboard satellite data compression.
---

# JPEG2000 & CCSDS Downlink Artifact Removal

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when eliminating ringing and blocking artifacts caused by onboard satellite data compression.

## Workflow

1. Identify compression parameters (quality, wavelet levels) from headers if available.
2. Apply artifact suppression with a compression-artifact-trained network.
3. Deblock block boundaries and dering around high-contrast road markings.
4. Compare against an uncompressed reference strip when one exists.

## Output

Image restored from downlink compression artifacts.
