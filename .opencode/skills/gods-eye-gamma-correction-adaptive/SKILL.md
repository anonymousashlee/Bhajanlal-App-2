---
name: Gamma Correction (Adaptive)
description: Use when non-linear luminance mapping must be tuned per frame histogram.
---

# Gamma Correction (Adaptive)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when non-linear luminance mapping must be tuned per frame histogram.

## Workflow

1. Compute per-frame histogram.
2. Adjust gamma to lift shadows.
3. Clamp to avoid over-brightening.
4. Apply on luminance channel.

## Output

Gamma-corrected frames.
