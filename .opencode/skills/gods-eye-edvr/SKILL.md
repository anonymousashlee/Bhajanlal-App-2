---
name: EDVR
description: Use when deformable convolution alignment must upscale multi-frame video of moving cars.
---

# EDVR

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when deformable convolution alignment must upscale multi-frame video of moving cars.

## Workflow

1. Estimate optical flow between reference and neighbor frames.
2. Align features with deformable convolutions guided by flow.
3. Fuse aligned features with temporal attention.
4. Validate on sequences with fast vehicle motion.

## Output

Aligned multi-frame upscaled video.
