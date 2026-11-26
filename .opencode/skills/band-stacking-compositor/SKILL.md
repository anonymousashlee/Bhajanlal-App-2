---
name: Band Stacking Compositor
description: Use when merging individual spectral band files (Red, Green, Blue, NIR) into multi-band rasters.
---

# Band Stacking Compositor

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when merging individual spectral band files (Red, Green, Blue, NIR) into multi-band rasters.

## Workflow

1. List band files and order.
2. Stack with rasterio/GDAL.
3. Set band names and metadata.
4. Validate dimensions/CRS.
5. Write multi-band GeoTIFF.

## Output

Multi-band composite raster.
