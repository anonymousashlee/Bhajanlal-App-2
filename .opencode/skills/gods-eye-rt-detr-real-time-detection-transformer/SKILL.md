---
name: RT-DETR
description: Use when transformer detection must eliminate NMS in dense crowds.
---

# RT-DETR

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when transformer detection must eliminate NMS in dense crowds.

## Workflow

1. Use transformer decoder with IoU-aware queries.
2. Avoid NMS post-processing.
3. Handle dense traffic crowds.
4. Validate on crowded scenes.

## Output

NMS-free dense detections.
