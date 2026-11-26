---
name: Multi-Constellation Temporal Fusion
description: Use when combining morning, midday, and afternoon passes from different constellations to capture optimal sun-shadow angles.
---

# Multi-Constellation Temporal Fusion

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when combining morning, midday, and afternoon passes from different constellations to capture optimal sun-shadow angles.

## Workflow

1. Co-register passes from each constellation to a common grid.
2. Normalize radiometry across sensors and illumination conditions.
3. Fuse temporally, keeping the pass with the best sun-shadow geometry per region.
4. Preserve per-pass provenance so results stay auditable.

## Output

Fused multi-pass product with optimal shadow geometry.
