---
name: High-Boost Filtering
description: Use when high-frequency edge details must be amplified while retaining luminance.
---

# High-Boost Filtering

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when high-frequency edge details must be amplified while retaining luminance.

## Workflow

1. Compute high-boost = original + k*(original - blurred).
2. Tune k for desired sharpening strength.
3. Preserve background luminance.
4. Avoid over-amplification of noise.

## Output

High-boost sharpened frames.
