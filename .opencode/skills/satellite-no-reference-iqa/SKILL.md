---
name: No-Reference Image Quality Assessment (NIQE / BRISQUE / MUSIQ)
description: Use when automatically scoring sharpness and clarity when no ground-truth image exists.
---

# No-Reference Image Quality Assessment (NIQE / BRISQUE / MUSIQ)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when automatically scoring sharpness and clarity when no ground-truth image exists.

## Workflow

1. Run NIQE/BRISQUE for natural-scene quality or MUSIQ for learned quality.
2. Score per-tile and map the worst regions for review.
3. Track scores across pipeline versions as a regression gate.
4. Correlate scores with human clarity ratings before trusting them.

## Output

Per-image clarity scores ranking results without ground truth.
