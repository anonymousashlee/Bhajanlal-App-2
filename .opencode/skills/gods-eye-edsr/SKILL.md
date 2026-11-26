---
name: EDSR (Enhanced Deep Super-Resolution)
description: Use when deep residual super-resolution must sharpen vehicle edges without batch-norm artifacts.
---

# EDSR (Enhanced Deep Super-Resolution)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when deep residual super-resolution must sharpen vehicle edges without batch-norm artifacts.

## Workflow

1. Remove batch normalization to preserve range and reduce memory.
2. Stack residual blocks with skip connections for stable deep training.
3. Train with L1 or perceptual loss depending on downstream detector needs.
4. Benchmark edge acutance on car silhouettes before deployment.

## Output

Residual-upscaled frames with sharp vehicle edges.
