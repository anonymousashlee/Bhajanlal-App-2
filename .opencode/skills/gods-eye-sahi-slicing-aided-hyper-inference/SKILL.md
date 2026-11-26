---
name: SAHI (Slicing Aided Hyper Inference)
description: Use when high-res aerial/4K images must be tiled so tiny humans aren't lost.
---

# SAHI (Slicing Aided Hyper Inference)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when high-res aerial/4K images must be tiled so tiny humans aren't lost.

## Workflow

1. Slice image into overlapping patches.
2. Run detector on each patch.
3. Merge results with NMS/WBF.
4. Validate on 15-pixel humans.

## Output

Tiled detections preserving tiny targets.
