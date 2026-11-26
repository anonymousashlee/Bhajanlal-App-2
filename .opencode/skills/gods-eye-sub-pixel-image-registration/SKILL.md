---
name: Sub-Pixel Image Registration
description: Use when multi-temporal frames must be aligned to detect parked/departed vehicles.
---

# Sub-Pixel Image Registration

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when multi-temporal frames must be aligned to detect parked/departed vehicles.

## Workflow

1. Estimate sub-pixel shift via phase correlation.
2. Refine alignment to ~0.05 px.
3. Detect changes between aligned frames.
4. Validate on static roads.

## Output

Aligned multi-temporal frames.
