---
name: Normalized Wasserstein Distance (NWD) Loss
description: Use when replacing IoU loss, which fails on 2x2 pixel targets, with distribution-based similarity metrics.
---

# Normalized Wasserstein Distance (NWD) Loss

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when replacing IoU loss, which fails on 2x2 pixel targets, with distribution-based similarity metrics.

## Workflow

1. Represent each box as a 2D Gaussian distribution.
2. Compute NWD between prediction and ground-truth distributions.
3. Use NWD as the classification-matching or regression loss for tiny boxes.
4. Compare recall on sub-10-pixel targets against IoU-trained baseline.

## Output

Detector trained with a loss that stays stable at tiny scales.
