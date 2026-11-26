---
name: DeblurGAN-v2
description: Use when real-time blind motion deblurring must freeze moving vehicles.
---

# DeblurGAN-v2

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when real-time blind motion deblurring must freeze moving vehicles.

## Workflow

1. Use FPN-based generator for multi-scale deblurring.
2. Train with adversarial + perceptual loss.
3. Handle blind blur without PSF estimation.
4. Validate on fast-moving cars and walkers.

## Output

Motion-deblurred frames.
