---
name: BM3D (Block-Matching and 3D Filtering)
description: Use when grouping similar road patches to strip Gaussian noise while preserving isolated tiny targets.
---

# BM3D (Block-Matching and 3D Filtering)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when grouping similar road patches to strip Gaussian noise while preserving isolated tiny targets.

## Workflow

1. Group similar 2D patches into 3D stacks via block matching.
2. Collaboratively filter in the transform domain and aggregate back.
3. Tune patch size and group size so single-pixel targets are not matched away.
4. Inspect tiny figures after filtering for erasure.

## Output

Denoised image with fine targets intact.
