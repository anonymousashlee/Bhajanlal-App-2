---
name: Diffusion-Based Remote Sensing SR
description: Use when latent diffusion models must synthesize realistic high-frequency texture in satellite imagery without hallucinating fake objects.
---

# Diffusion-Based Remote Sensing SR

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when latent diffusion models must synthesize realistic high-frequency texture in satellite imagery without hallucinating fake objects.

## Workflow

1. Condition the diffusion SR on the low-res tile with a mild (2x) noise schedule.
2. Keep guidance strength low so priors add texture, not invented objects.
3. Compare output structure against the input - any new road marking or figure is a red flag.
4. Use the deterministic DDIM sampler so results are reproducible across runs.

## Output

Texturally rich upscale with structure locked to the input pixels.
