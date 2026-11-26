---
name: SwinIR
description: Use when transformer-based image restoration must recover high-frequency detail from CCTV and aerial tiles.
---

# SwinIR

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when transformer-based image restoration must recover high-frequency detail from CCTV and aerial tiles.

## Workflow

1. Choose window size and shift size to cover whole road segments.
2. Run overlapping-window inference to avoid seam artifacts between patches.
3. Apply on luminance-first or full RGB depending on color fidelity needs.
4. Verify lane lines and silhouettes stay continuous across patch borders.

## Output

Transformer-restored imagery with crisp high-frequency detail.
