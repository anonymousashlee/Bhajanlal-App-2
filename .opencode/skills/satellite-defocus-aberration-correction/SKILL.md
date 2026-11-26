---
name: Defocus Aberration Correction
description: Use when compensating for thermal expansion shifts in orbital mirror focal lengths.
---

# Defocus Aberration Correction

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when compensating for thermal expansion shifts in orbital mirror focal lengths.

## Workflow

1. Estimate defocus from the edge spread function or a phase-retrieval method.
2. Apply inverse filtering or a defocus-trained restoration network.
3. If focus drifts over the pass, correct in tiles with per-tile estimates.
4. Re-measure MTF after correction to confirm improvement.

## Output

In-focus imagery despite thermal focus drift.
