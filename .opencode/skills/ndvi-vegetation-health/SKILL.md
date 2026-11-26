---
name: NDVI Vegetation Health
description: Use when computing Normalized Difference Vegetation Index rasters and classifying crop vigor.
---

# NDVI Vegetation Health

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when computing Normalized Difference Vegetation Index rasters and classifying crop vigor.

## Workflow

1. Compute (NIR-Red)/(NIR+Red).
2. Handle nodata and scaling.
3. Classify vigor thresholds.
4. Visualize and export.
5. Validate against ground truth.

## Output

NDVI vegetation health raster.
