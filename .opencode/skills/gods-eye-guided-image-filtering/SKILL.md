---
name: Guided Image Filtering
description: Use when fast linear-time edge-preserving smoothing is needed.
---

# Guided Image Filtering

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when fast linear-time edge-preserving smoothing is needed.

## Workflow

1. Compute local linear model guided by an edge map.
2. Use the original image as guide for edge preservation.
3. Tune radius and epsilon for road surfaces.
4. Run in O(N) for real-time streams.

## Output

Fast edge-preserving smoothed frames.
