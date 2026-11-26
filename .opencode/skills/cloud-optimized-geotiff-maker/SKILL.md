---
name: Cloud-Optimized GeoTIFF Maker
description: Use when converting raw rasters into tiled, overview-enabled COGs using GDAL.
---

# Cloud-Optimized GeoTIFF Maker

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when converting raw rasters into tiled, overview-enabled COGs using GDAL.

## Workflow

1. Inspect input raster.
2. Build overviews with gdaladdo.
3. Convert to COG with tiling.
4. Validate with rio-cogeo.
5. Upload to object storage.

## Output

COG-ready raster files.
