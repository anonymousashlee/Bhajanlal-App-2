---
name: Median Filtering
description: Use when salt-and-pepper impulse noise must be removed from analog/wireless feeds.
---

# Median Filtering

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when salt-and-pepper impulse noise must be removed from analog/wireless feeds.

## Workflow

1. Apply median filter with small kernel (3x3/5x5).
2. Use on grayscale or per-channel.
3. Avoid on fine textures - can blur thin lines.
4. Combine with outlier detection for hot pixels.

## Output

Impulse-noise-cleaned frames.
