---
name: Latent Diffusion Upscaling (Tile-based)
description: Use when plausible micro-textures must be hallucinated on ultra-low-res aerial tiles.
---

# Latent Diffusion Upscaling (Tile-based)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when plausible micro-textures must be hallucinated on ultra-low-res aerial tiles.

## Workflow

1. Condition latent diffusion on the low-res tile with mild noise.
2. Keep guidance low so priors add texture, not invented objects.
3. Tile with overlap to cover large scenes.
4. Compare structure against input - new objects are a red flag.

## Output

Texturally rich upscaled tiles with structure locked to input.
