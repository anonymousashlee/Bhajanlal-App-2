---
name: Video Satellite Super-Resolution (VSR)
description: Use when exploiting temporal continuity across full-motion satellite video to resolve moving pedestrians frame to frame.
---

# Video Satellite Super-Resolution (VSR)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when exploiting temporal continuity across full-motion satellite video to resolve moving pedestrians frame to frame.

## Workflow

1. Align frames with motion compensation or optical flow first.
2. Fuse information across a temporal window of 3-9 frames into the target frame.
3. Mask moving objects from naive averaging to prevent ghosting.
4. Evaluate on tracked targets - identity must stay stable across frames.

## Output

Temporally consistent super-resolved video frames.
