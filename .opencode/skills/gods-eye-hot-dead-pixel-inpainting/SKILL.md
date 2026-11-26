---
name: Hot/Dead Pixel Inpainting
description: Use when stuck CMOS sensor pixels must be detected and interpolated.
---

# Hot/Dead Pixel Inpainting

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when stuck CMOS sensor pixels must be detected and interpolated.

## Workflow

1. Detect outlier pixels vs local median.
2. Interpolate from neighbors.
3. Maintain a bad-pixel map for reuse.
4. Apply before neural processing.

## Output

Sensor-defect-corrected frames.
