---
name: Frequency-Aware Loss Optimization (Focal Frequency Loss)
description: Use when forcing a restoration network to prioritize high-frequency spatial details over flat asphalt backgrounds during training.
---

# Frequency-Aware Loss Optimization (Focal Frequency Loss)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when forcing a restoration network to prioritize high-frequency spatial details over flat asphalt backgrounds during training.

## Workflow

1. Add a focal frequency loss term that weights hard-to-reconstruct frequencies.
2. Balance its weight against pixel loss so sensor noise is not amplified.
3. Monitor the frequency-domain residual during training for convergence.
4. Validate that road markings gain sharpness without checkerboard artifacts.

## Output

Model that optimizes perceptually important high frequencies.
