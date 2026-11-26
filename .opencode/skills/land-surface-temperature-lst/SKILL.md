---
name: Land Surface Temperature (LST)
description: Use when deriving thermal heat-island maps from Landsat Thermal Infrared (TIRS) bands.
---

# Land Surface Temperature (LST)

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when deriving thermal heat-island maps from Landsat Thermal Infrared (TIRS) bands.

## Workflow

1. Convert TIRS to radiance.
2. Compute brightness temperature.
3. Apply emissivity correction.
4. Derive LST.
5. Map heat islands.

## Output

Land surface temperature raster.
