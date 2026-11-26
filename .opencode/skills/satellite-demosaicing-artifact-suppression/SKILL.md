---
name: Demosaicing Artifact Suppression
description: Use when preventing zippering and false-color moire patterns on high-frequency road markings.
---

# Demosaicing Artifact Suppression

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when preventing zippering and false-color moire patterns on high-frequency road markings.

## Workflow

1. Detect moire and zipper artifacts with high-frequency color residual analysis.
2. Re-demosaic with an adaptive or learning-based demosaicer.
3. Apply a targeted color-aliasing removal pass if artifacts remain.
4. Check lane lines and crosswalks for false color fringes.

## Output

Artifact-free color image without zippering or moire.
