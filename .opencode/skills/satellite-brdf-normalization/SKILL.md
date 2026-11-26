---
name: BRDF (Bidirectional Reflectance Distribution Function) Normalization
description: Use when correcting brightness changes caused by off-nadir viewing angles.
---

# BRDF (Bidirectional Reflectance Distribution Function) Normalization

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when correcting brightness changes caused by off-nadir viewing angles.

## Workflow

1. Record per-pixel view and solar geometry for the acquisition.
2. Apply a kernel-driven BRDF model to normalize to a fixed reference geometry.
3. Mask pixels where the geometry is too extreme for stable normalization.
4. Confirm multi-date tiles now share comparable brightness.

## Output

Angularly normalized imagery comparable across view angles.
