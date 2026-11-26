---
name: Bicubic Interpolation
description: Use when a fast baseline geometric upsampling is needed before neural refinement.
---

# Bicubic Interpolation

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when a fast baseline geometric upsampling is needed before neural refinement.

## Workflow

1. Resize with bicubic kernel for smooth 2x-4x upsampling.
2. Use as the first stage in a cascade before neural refinement.
3. Avoid as final output for tiny human detection - too soft.
4. Measure runtime cost; it is nearly free on GPU.

## Output

Baseline smoothly upsampled frames.
