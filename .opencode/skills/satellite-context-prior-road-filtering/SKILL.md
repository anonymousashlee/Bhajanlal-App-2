---
name: Context Prior Filtering (Road/Sidewalk Constraints)
description: Use when weighting detection confidence higher along crosswalks, bus stops, and sidewalks.
---

# Context Prior Filtering (Road/Sidewalk Constraints)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when weighting detection confidence higher along crosswalks, bus stops, and sidewalks.

## Workflow

1. Load road, sidewalk, and crosswalk masks from vector data.
2. Boost or gate detector scores inside high-probability zones.
3. Suppress detections in impossible zones (building roofs, water).
4. Report which prior changed each accepted detection.

## Output

Context-gated detections concentrated on walkable areas.
