---
name: SAHI (Slicing Aided Hyper Inference)
description: Use when splitting massive gigapixel satellite scenes into overlapping high-res patches so tiny targets are not downscaled away.
---

# SAHI (Slicing Aided Hyper Inference)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when splitting massive gigapixel satellite scenes into overlapping high-res patches so tiny targets are not downscaled away.

## Workflow

1. Slice the scene into overlapping patches sized for the detector input.
2. Run inference on each patch at full resolution.
3. Merge predictions across slices with non-maximum suppression.
4. Confirm a person-sized target is not lost between slice borders.

## Output

Detections over the full scene without resolution loss.
