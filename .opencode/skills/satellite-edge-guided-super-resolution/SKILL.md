---
name: Edge-Guided Super-Resolution
description: Use when extracting high-frequency gradient maps first so super-resolution does not blur road curbs and human silhouettes.
---

# Edge-Guided Super-Resolution

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when extracting high-frequency gradient maps first so super-resolution does not blur road curbs and human silhouettes.

## Workflow

1. Compute gradient maps (Sobel or Canny) from the input tile.
2. Use them as an extra guidance channel or as an edge loss in the SR network.
3. After upscaling, blend a detail layer back along the extracted edges.
4. Verify silhouettes remain sharp against the asphalt background.

## Output

Upscale with preserved edge structure on curbs and silhouettes.
