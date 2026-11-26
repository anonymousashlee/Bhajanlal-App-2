---
name: Tiled Streaming & Memory-Efficient Inference (GDAL / Rasterio)
description: Use when processing multi-gigabyte GeoTIFF scenes without losing geospatial metadata or CRS projections.
---

# Tiled Streaming & Memory-Efficient Inference (GDAL / Rasterio)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when processing multi-gigabyte GeoTIFF scenes without losing geospatial metadata or CRS projections.

## Workflow

1. Open the raster with windowed reads instead of loading it whole.
2. Process in tiles sized to memory with overlap for seamless blending.
3. Write output with the source CRS, transform, and nodata preserved.
4. Validate the output opens correctly in a GIS viewer.

## Output

Processed huge rasters with geospatial metadata intact.
