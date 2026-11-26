---
name: Non-Local Means (NLM) Denoising
description: Use when averaging repetitive pavement textures without smearing non-repeating pedestrian pixels.
---

# Non-Local Means (NLM) Denoising

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when averaging repetitive pavement textures without smearing non-repeating pedestrian pixels.

## Workflow

1. Search a large window for patches similar to each reference patch.
2. Weight similar patches by exponential similarity of their neighborhoods.
3. Use a search window large enough to find true matches in uniform asphalt.
4. Verify non-repeating silhouettes are not blurred by wrong matches.

## Output

Noise reduced with texture and unique targets preserved.
