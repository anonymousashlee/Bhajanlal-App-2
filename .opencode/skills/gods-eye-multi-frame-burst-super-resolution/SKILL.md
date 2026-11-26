---
name: Multi-Frame Burst Super-Resolution
description: Use when sub-pixel camera jitter across frames must be fused into higher resolution.
---

# Multi-Frame Burst Super-Resolution

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when sub-pixel camera jitter across frames must be fused into higher resolution.

## Workflow

1. Register burst frames to sub-pixel accuracy.
2. Estimate per-frame shifts and sharpness weights.
3. Fuse with robust averaging rejecting outlier frames.
4. Mask moving objects to avoid ghosting.

## Output

Burst-fused higher-resolution frame.
