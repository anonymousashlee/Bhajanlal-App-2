---
name: DehazeFormer & Physics-Guided Dehazing
description: Use when clearing thin cirrus clouds and urban smog over road networks.
---

# DehazeFormer & Physics-Guided Dehazing

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when clearing thin cirrus clouds and urban smog over road networks.

## Workflow

1. Estimate the transmission map with a physics haze model or DehazeFormer network.
2. Recover the scene radiance with the atmospheric scattering model.
3. Refine transmission edges so building and tree boundaries do not halo.
4. Leave opaque cloud pixels masked rather than hallucinating content beneath them.

## Output

Dehazed scene with roads and figures visible through thin haze.
