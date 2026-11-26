---
name: ByteTrack
description: Use when low-confidence detections must be associated to track occluded pedestrians.
---

# ByteTrack

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when low-confidence detections must be associated to track occluded pedestrians.

## Workflow

1. Track high and low confidence detections.
2. Associate via IoU and motion.
3. Maintain IDs through occlusion.
4. Validate on crowded scenes.

## Output

Robust multi-object tracks.
