---
name: STAC API Query Builder
description: Use when querying SpatioTemporal Asset Catalogs (Sentinel, Landsat, Planet) by bounding box and cloud cover.
---

# STAC API Query Builder

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when querying SpatioTemporal Asset Catalogs (Sentinel, Landsat, Planet) by bounding box and cloud cover.

## Workflow

1. Define AOI and time range.
2. Build STAC search request with filters.
3. Paginate and collect items.
4. Filter by cloud cover and bands.
5. Export asset links.

## Output

STAC query results and asset links.
