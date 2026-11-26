---
name: Scene Cloud Masking
description: Use when applying QA60 or s2cloudless masks to remove clouds and cloud shadows from optical scenes.
---

# Scene Cloud Masking

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when applying QA60 or s2cloudless masks to remove clouds and cloud shadows from optical scenes.

## Workflow

1. Load QA band or run s2cloudless.
2. Build cloud/shadow mask.
3. Apply mask to scene.
4. Interpolate or leave nodata.
5. Validate mask quality.

## Output

Cloud-masked satellite scene.
