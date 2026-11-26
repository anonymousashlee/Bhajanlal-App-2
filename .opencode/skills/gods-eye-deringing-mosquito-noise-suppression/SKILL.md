---
name: Deringing / Mosquito Noise Suppression
description: Use when ringing artifacts around high-contrast car silhouettes must be removed.
---

# Deringing / Mosquito Noise Suppression

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when ringing artifacts around high-contrast car silhouettes must be removed.

## Workflow

1. Detect ringing near strong edges.
2. Apply directional smoothing in ringing regions.
3. Preserve edge sharpness.
4. Validate on vehicle contours.

## Output

Ringing-suppressed frames.
