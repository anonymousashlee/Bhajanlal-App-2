---
name: Non-Local Means (NLM) Denoising
description: Use when similar patches must be averaged while keeping edges intact.
---

# Non-Local Means (NLM) Denoising

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when similar patches must be averaged while keeping edges intact.

## Workflow

1. Search for similar patches across the frame.
2. Weighted average by patch similarity.
3. Tune patch size and search window.
4. Preserve edges on pedestrians and vehicles.

## Output

Edge-preserving denoised frames.
