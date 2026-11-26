---
name: Query-Based Tiny Object Detection (DINO / RT-DETR)
description: Use when transformer cross-attention must locate sub-10-pixel targets without anchor-box mismatches.
---

# Query-Based Tiny Object Detection (DINO / RT-DETR)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when transformer cross-attention must locate sub-10-pixel targets without anchor-box mismatches.

## Workflow

1. Set up a query-based detector with multi-scale feature attention.
2. Tune the number of queries to cover expected target density.
3. Train with denoising queries to stabilize small-box learning.
4. Check borderline 3-5 pixel targets against anchor-based baseline recall.

## Output

Anchor-free detections of sub-10-pixel targets.
