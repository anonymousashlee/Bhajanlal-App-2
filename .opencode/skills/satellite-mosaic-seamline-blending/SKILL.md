---
name: Image Mosaicking & Seamline Blending
description: Use when merging adjacent satellite strips seamlessly without cutting across moving road targets.
---

# Image Mosaicking & Seamline Blending

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when merging adjacent satellite strips seamlessly without cutting across moving road targets.

## Workflow

1. Co-register strips to sub-pixel accuracy before mosaicking.
2. Choose seamlines that avoid roads and dynamic objects where possible.
3. Blend across seams with radiometric normalization and feathering.
4. Check seams never split a vehicle or pedestrian across two tones.

## Output

Seamless radiometrically consistent mosaic.
