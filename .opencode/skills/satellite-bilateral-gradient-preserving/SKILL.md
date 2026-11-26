---
name: Gradient-Preserving Bilateral Filtering
description: Use when smoothing flat asphalt noise while respecting sharp luminance jumps.
---

# Gradient-Preserving Bilateral Filtering

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when smoothing flat asphalt noise while respecting sharp luminance jumps.

## Workflow

1. Filter with range weights so pixels across strong edges are not averaged.
2. Keep the spatial sigma small enough to retain silhouette boundaries.
3. Apply on flat road regions to suppress sensor grain.
4. Check pedestrian edges stay crisp after smoothing.

## Output

Smoothed noise with gradients and edges preserved.
