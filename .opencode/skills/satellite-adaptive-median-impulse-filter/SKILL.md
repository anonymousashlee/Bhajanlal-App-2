---
name: Impulse & Salt-and-Pepper Median Filtering (Adaptive)
description: Use when removing transmission bit-errors without eroding 1-pixel targets.
---

# Impulse & Salt-and-Pepper Median Filtering (Adaptive)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when removing transmission bit-errors without eroding 1-pixel targets.

## Workflow

1. Detect impulse pixels by comparing to the local median and variance.
2. Replace only flagged pixels, leaving all others untouched.
3. Use an adaptive window size so small real targets survive.
4. Verify no isolated real point targets were classified as noise.

## Output

Image with bit-error impulses removed, targets preserved.
