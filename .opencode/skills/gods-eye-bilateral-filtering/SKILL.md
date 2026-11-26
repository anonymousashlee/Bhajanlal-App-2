---
name: Bilateral Filtering
description: Use when flat road surfaces must be cleaned without blurring pedestrians.
---

# Bilateral Filtering

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when flat road surfaces must be cleaned without blurring pedestrians.

## Workflow

1. Filter in spatial and range domains jointly.
2. Tune sigma_s and sigma_r for road vs figure.
3. Apply on luminance to avoid color bleed.
4. Avoid over-smoothing small targets.

## Output

Edge-preserving smoothed frames.
