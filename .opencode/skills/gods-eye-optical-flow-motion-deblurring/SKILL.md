---
name: Optical Flow Motion Deblurring
description: Use when vehicle velocity vectors must be estimated to invert directional motion blur.
---

# Optical Flow Motion Deblurring

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when vehicle velocity vectors must be estimated to invert directional motion blur.

## Workflow

1. Estimate dense optical flow of moving objects.
2. Invert blur along flow vectors.
3. Handle multiple moving objects separately.
4. Validate on directional streaks.

## Output

Flow-inverted motion-deblurred frames.
