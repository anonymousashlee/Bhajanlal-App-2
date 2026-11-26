---
name: Dynamic Range Compression & Tone Mapping
description: Use when mapping 11-bit/12-bit/16-bit raw satellite radiometry into 8-bit displays without crushing dark tones.
---

# Dynamic Range Compression & Tone Mapping

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when mapping 11-bit/12-bit/16-bit raw satellite radiometry into 8-bit displays without crushing dark tones.

## Workflow

1. Normalize raw DN to a float reflectance or radiance range first.
2. Apply a global curve (gamma or Reinhard) tuned so asphalt mid-tones stay separated.
3. Use local tone mapping only when global compression loses tiny dark targets.
4. Record the transform so results remain radiometrically reproducible.

## Output

Display-ready 8-bit imagery with preserved dark detail.
