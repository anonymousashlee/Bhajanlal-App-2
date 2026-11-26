---
name: Video Stabilization (Homography / RANSAC)
description: Use when wind-induced pole shake on elevated cameras must be removed.
---

# Video Stabilization (Homography / RANSAC)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when wind-induced pole shake on elevated cameras must be removed.

## Workflow

1. Estimate homography between frames with RANSAC.
2. Smooth the camera path over time.
3. Warp frames to stabilized path.
4. Crop borders to hide empty regions.

## Output

Stabilized elevated-camera frames.
