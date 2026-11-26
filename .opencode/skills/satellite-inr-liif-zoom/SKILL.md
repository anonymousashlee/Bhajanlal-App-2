---
name: Implicit Neural Representations (INR / LIIF)
description: Use when implicit neural representations query continuous coordinates to zoom smoothly into pedestrian-scale regions without pixelation.
---

# Implicit Neural Representations (INR / LIIF)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when implicit neural representations query continuous coordinates to zoom smoothly into pedestrian-scale regions without pixelation.

## Workflow

1. Train the INR on the target tile or load a pretrained LIIF model.
2. Query at arbitrary output resolution - for example 6-8x for a person-sized crop.
3. Limit zoom to where the model stays faithful; beyond about 4x flag the crop as uncertain.
4. Render a coordinate grid overlay to document the zoom factor used.

## Output

Continuously queryable image function for arbitrary-zoom crops.
