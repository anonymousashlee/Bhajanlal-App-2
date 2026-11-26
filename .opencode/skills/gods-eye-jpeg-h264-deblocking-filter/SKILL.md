---
name: JPEG/H.264 Deblocking Filter
description: Use when 8x8/16x16 macroblock boundaries must be smoothed in low-bitrate streams.
---

# JPEG/H.264 Deblocking Filter

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when 8x8/16x16 macroblock boundaries must be smoothed in low-bitrate streams.

## Workflow

1. Detect block boundaries and apply deblocking.
2. Tune strength by QP and edge activity.
3. Preserve true edges while smoothing blocks.
4. Apply on decoded frames before detection.

## Output

Deblocked stream frames.
