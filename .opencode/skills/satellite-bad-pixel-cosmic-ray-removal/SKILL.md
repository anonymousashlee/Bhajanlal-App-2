---
name: Bad-Pixel & Cosmic-Ray Spike Removal
description: Use when interpolating dead detector pixels or radiation hits that mimic tiny white dots on roads.
---

# Bad-Pixel & Cosmic-Ray Spike Removal

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when interpolating dead detector pixels or radiation hits that mimic tiny white dots on roads.

## Workflow

1. Detect outliers with a median filter residual and a saturation check.
2. Distinguish cosmic rays (sharp single pixels) from real small targets by PSF width.
3. Replace flagged pixels with a local median or inpainting interpolation.
4. Re-run detection to confirm no real target was removed.

## Output

Clean image without false point targets.
