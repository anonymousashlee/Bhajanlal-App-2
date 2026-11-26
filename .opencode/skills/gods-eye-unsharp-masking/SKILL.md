---
name: Unsharp Masking
description: Use when local edge acutance must be enhanced.
---

# Unsharp Masking

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when local edge acutance must be enhanced.

## Workflow

1. Subtract a Gaussian-blurred copy from original.
2. Scale and add back the high-frequency residual.
3. Tune radius and amount to avoid halos.
4. Use as a cheap sharpening fallback.

## Output

Edge-acutance-enhanced frames.
