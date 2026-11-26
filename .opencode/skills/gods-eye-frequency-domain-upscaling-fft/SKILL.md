---
name: Frequency-Domain Upscaling (FFT Zero-Padding)
description: Use when periodic structures like crosswalks and roofs must be preserved during zoom.
---

# Frequency-Domain Upscaling (FFT Zero-Padding)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when periodic structures like crosswalks and roofs must be preserved during zoom.

## Workflow

1. Transform to frequency domain and zero-pad high frequencies.
2. Inverse transform to obtain the upsampled image.
3. Apply a window to reduce ringing artifacts.
4. Use for periodic/structured scenes, not natural textures.

## Output

Frequency-preserving upsampled frames.
