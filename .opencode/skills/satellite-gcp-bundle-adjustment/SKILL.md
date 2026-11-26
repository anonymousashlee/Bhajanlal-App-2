---
name: Geo-Referencing & Ground Control Point (GCP) Bundle Adjustment
description: Use when locking image coordinates to sub-decimeter geographic accuracy.
---

# Geo-Referencing & Ground Control Point (GCP) Bundle Adjustment

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when locking image coordinates to sub-decimeter geographic accuracy.

## Workflow

1. Collect well-spread GCPs with known coordinates.
2. Run bundle adjustment to solve camera and ground parameters jointly.
3. Check residuals - reject outliers and re-solve.
4. Report RMSE in the horizontal and vertical directions.

## Output

Geo-referenced image with sub-decimeter positional accuracy.
