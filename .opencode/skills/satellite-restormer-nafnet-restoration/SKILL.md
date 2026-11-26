---
name: Restormer & NAFNet Restoration
description: Use when nonlinear activation-free networks remove complex atmospheric and motion blur simultaneously from satellite imagery.
---

# Restormer & NAFNet Restoration

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when nonlinear activation-free networks remove complex atmospheric and motion blur simultaneously from satellite imagery.

## Workflow

1. Select the pretrained checkpoint sized for the expected degradation mix.
2. Feed the raw tile and use tiled inference with padding for large scenes.
3. If retraining, mix blur, haze, and noise degradations in one dataset.
4. Validate with both PSNR and visual checks on tiny targets.

## Output

One-pass restoration covering blur, haze, and noise.
