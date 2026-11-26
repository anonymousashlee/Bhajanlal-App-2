---
name: NDWI Surface Water Mapper
description: Use when extracting water bodies, reservoirs, and flood extents using green and NIR bands.
---

# NDWI Surface Water Mapper

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when extracting water bodies, reservoirs, and flood extents using green and NIR bands.

## Workflow

1. Compute (Green-NIR)/(Green+NIR).
2. Threshold water pixels.
3. Clean with morphology.
4. Vectorize water bodies.
5. Export water mask.

## Output

Surface water extent map.
