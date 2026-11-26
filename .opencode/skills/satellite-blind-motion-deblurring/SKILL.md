---
name: Blind Motion Deblurring
description: Use when removing directional smear caused by spacecraft orbital velocity at 7.5 km/s and Time Delay Integration jitter.
---

# Blind Motion Deblurring

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when removing directional smear caused by spacecraft orbital velocity at 7.5 km/s and Time Delay Integration jitter.

## Workflow

1. Estimate the blur kernel direction and length from strong edges via gradient statistics.
2. Apply a blind deconvolution or a motion-blur-trained restoration network.
3. Re-estimate the kernel once after the first pass if edges still smear.
4. Check lane lines and vehicle outlines for residual streaking.

## Output

Image with orbital motion smear removed.
