---
name: Multi-Scale Test-Time Augmentation (TTA)
description: Use when running inference across rotated and zoomed crops to boost recall on borderline-visible figures.
---

# Multi-Scale Test-Time Augmentation (TTA)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when running inference across rotated and zoomed crops to boost recall on borderline-visible figures.

## Workflow

1. Generate rotated and scaled variants of each crop.
2. Run the detector on every variant.
3. Merge results with weighted box fusion.
4. Keep the variant set small enough that latency stays acceptable.

## Output

Higher-recall detections from multi-view aggregation.
