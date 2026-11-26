---
name: Sub-Pixel Convolution (ESPCN)
description: Use when pixel-shuffling must deliver low-latency 2x-4x zoom.
---

# Sub-Pixel Convolution (ESPCN)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when pixel-shuffling must deliver low-latency 2x-4x zoom.

## Workflow

1. Replace deconvolution with sub-pixel convolution (pixel shuffle).
2. Move upsampling to the network tail for efficiency.
3. Train with MSE or perceptual loss per use case.
4. Profile latency for real-time streams.

## Output

Low-latency pixel-shuffled upscaled frames.
