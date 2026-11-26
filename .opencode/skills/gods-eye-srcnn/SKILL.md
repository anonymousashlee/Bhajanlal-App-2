---
name: SRCNN
description: Use when a lightweight 3-layer CNN must super-resolve real-time edge streams.
---

# SRCNN

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when a lightweight 3-layer CNN must super-resolve real-time edge streams.

## Workflow

1. Patch and represent the input with a learned feature extractor.
2. Map features non-linearly then reconstruct the high-res output.
3. Keep the network shallow for sub-30ms inference on edge devices.
4. Validate PSNR/SSIM against heavier models before accepting trade-offs.

## Output

Fast lightweight super-resolved stream frames.
