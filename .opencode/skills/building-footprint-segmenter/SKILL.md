---
name: Building Footprint Segmenter
description: Use when running semantic segmentation (U-Net/SAM) on sub-meter imagery to extract building polygons.
---

# Building Footprint Segmenter

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when running semantic segmentation (U-Net/SAM) on sub-meter imagery to extract building polygons.

## Workflow

1. Run segmentation model.
2. Post-process masks.
3. Vectorize footprints.
4. Clean topology.
5. Export GeoJSON.

## Output

Building footprint polygons.
