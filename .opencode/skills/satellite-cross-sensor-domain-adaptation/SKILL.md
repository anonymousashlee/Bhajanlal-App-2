---
name: Cross-Sensor Domain Adaptation
description: Use when transferring sharpness priors from aerial drone imagery at 5 cm to orbital satellite imagery at 30 cm.
---

# Cross-Sensor Domain Adaptation

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when transferring sharpness priors from aerial drone imagery at 5 cm to orbital satellite imagery at 30 cm.

## Workflow

1. Collect paired or unpaired drone/satellite scenes of the same area types.
2. Adapt with domain-adversarial training or style transfer that preserves geometry.
3. Validate that the adapted model does not invent drone-only detail.
4. Keep radiometry consistent so downstream detection still works.

## Output

SR model whose priors transfer from drone to satellite imagery.
