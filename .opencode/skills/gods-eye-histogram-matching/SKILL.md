---
name: Histogram Matching
description: Use when exposure must be normalized across stitched tiles/cameras.
---

# Histogram Matching

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when exposure must be normalized across stitched tiles/cameras.

## Workflow

1. Compute reference histogram.
2. Match source histogram to reference.
3. Apply per-channel or luminance-only.
4. Validate color consistency.

## Output

Exposure-normalized frames.
