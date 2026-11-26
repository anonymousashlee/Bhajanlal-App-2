---
name: Pansharpening (Brovey, Gram-Schmidt, IHS)
description: Use when merging high-resolution panchromatic bands with lower-resolution multispectral color bands to sharpen satellite road imagery.
---

# Pansharpening (Brovey, Gram-Schmidt, IHS)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when merging high-resolution panchromatic bands with lower-resolution multispectral color bands to sharpen satellite road imagery.

## Workflow

1. Resample the multispectral bands to the panchromatic grid and match histograms.
2. Pick the injection method - IHS for visual sharpness, Gram-Schmidt for radiometric fidelity, Brovey for quick previews.
3. Fuse, then restore original color statistics to prevent hue shifts.
4. Check narrow road features and crosswalks for spectral distortion at 100% zoom.

## Output

Color-preserving imagery at panchromatic resolution with sharp road detail.
