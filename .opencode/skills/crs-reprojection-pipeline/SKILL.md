---
name: CRS Reprojection Pipeline
description: Use when safely transforming geometries and rasters between WGS84 (EPSG:4326) and local UTM zones.
---

# CRS Reprojection Pipeline

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when safely transforming geometries and rasters between WGS84 (EPSG:4326) and local UTM zones.

## Workflow

1. Detect source CRS.
2. Choose target CRS.
3. Reproject with GDAL/Shapely.
4. Validate accuracy.
5. Handle edge cases.

## Output

Reprojected geospatial data.
