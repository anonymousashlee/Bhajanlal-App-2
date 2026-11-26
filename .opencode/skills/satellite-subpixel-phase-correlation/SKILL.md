---
name: Sub-Pixel Phase Correlation
description: Use when measuring and reversing fractional-pixel drift between Time Delay Integration sensor stages.
---

# Sub-Pixel Phase Correlation

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when measuring and reversing fractional-pixel drift between Time Delay Integration sensor stages.

## Workflow

1. Compute phase correlation between adjacent stage outputs.
2. Interpolate the peak for sub-pixel drift estimates.
3. Shift and align each stage contribution to remove the drift.
4. Verify residual drift is near zero after correction.

## Output

TDI stages aligned with fractional drift removed.
