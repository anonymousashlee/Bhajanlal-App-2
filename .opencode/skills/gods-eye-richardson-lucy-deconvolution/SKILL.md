---
name: Richardson-Lucy Deconvolution
description: Use when iterative Bayesian restoration must fix optical lens defocus.
---

# Richardson-Lucy Deconvolution

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when iterative Bayesian restoration must fix optical lens defocus.

## Workflow

1. Iterate RL updates with PSF.
2. Apply positivity constraints.
3. Stop early to avoid noise amplification.
4. Use for defocus and mild motion blur.

## Output

RL-restored frames.
