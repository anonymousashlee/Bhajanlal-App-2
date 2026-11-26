---
name: Density-Map Counting (CSRNet / DM-Count)
description: Use when estimating pedestrian presence and crowd density on busy roads even when individual limbs cannot be resolved.
---

# Density-Map Counting (CSRNet / DM-Count)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when estimating pedestrian presence and crowd density on busy roads even when individual limbs cannot be resolved.

## Workflow

1. Generate density maps by convolving point annotations with Gaussian kernels.
2. Train a regression network to predict the density map from the crop.
3. Integrate the map to get counts and threshold for presence detection.
4. Validate count error against manual tallies on held-out scenes.

## Output

Crowd density maps and counts for unresolved targets.
