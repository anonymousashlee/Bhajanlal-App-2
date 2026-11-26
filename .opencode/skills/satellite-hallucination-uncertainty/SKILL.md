---
name: Hallucination Detection & Uncertainty Quantification
description: Use when flagging pixels generated purely by AI priors versus grounded in physical sensor photons.
---

# Hallucination Detection & Uncertainty Quantification

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when flagging pixels generated purely by AI priors versus grounded in physical sensor photons.

## Workflow

1. Keep a provenance mask through every generative step (SR, diffusion, inpainting).
2. Estimate per-pixel uncertainty with ensembles or diffusion variance.
3. Flag any detection resting mostly on generated pixels.
4. Require photon-grounded evidence before accepting a forensic claim.

## Output

Provenance and uncertainty maps separating real from generated detail.
