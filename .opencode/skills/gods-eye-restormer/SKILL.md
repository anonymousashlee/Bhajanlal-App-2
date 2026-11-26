---
name: Restormer
description: Use when a transformer must remove rain and noise on high-resolution imagery.
---

# Restormer

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when a transformer must remove rain and noise on high-resolution imagery.

## Workflow

1. Use multi-Dconv head transposed attention for efficiency.
2. Feed high-res frames via tiling if needed.
3. Train on rain, noise, and blur jointly.
4. Validate edge preservation on vehicles.

## Output

Transformer-denoised high-res frames.
