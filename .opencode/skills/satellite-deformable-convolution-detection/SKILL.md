---
name: Deformable Convolutional Networks (DCN)
description: Use when adapting receptive fields to elongated human silhouettes and irregular cast shadows.
---

# Deformable Convolutional Networks (DCN)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when adapting receptive fields to elongated human silhouettes and irregular cast shadows.

## Workflow

1. Replace fixed-kernel convolutions with offset-learned deformable ones.
2. Train on varied silhouette poses and shadow shapes.
3. Inspect learned offsets to confirm they follow target geometry.
4. Fall back to standard convs if offsets become unstable on small data.

## Output

Detector whose receptive fields conform to target shapes.
