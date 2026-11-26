---
name: Edge-Guided Proposal Refinement
description: Use when loose boxes must be snapped onto vehicle chassis edges.
---

# Edge-Guided Proposal Refinement

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when loose boxes must be snapped onto vehicle chassis edges.

## Workflow

1. Detect edges with Canny.
2. Refine box boundaries to edges.
3. Use morphological ops.
4. Validate on vehicle contours.

## Output

Tightly snapped boxes.
