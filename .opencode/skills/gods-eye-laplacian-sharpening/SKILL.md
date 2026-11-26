---
name: Laplacian Sharpening
description: Use when rapid intensity transitions must be highlighted.
---

# Laplacian Sharpening

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when rapid intensity transitions must be highlighted.

## Workflow

1. Apply Laplacian kernel to find second derivatives.
2. Subtract/ add scaled Laplacian to original.
3. Tune gain to avoid noise amplification.
4. Validate on vehicle contours.

## Output

Laplacian-sharpened frames.
