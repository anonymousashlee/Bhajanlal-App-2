---
name: Perspective / Homography Warping (Bird's-Eye View)
description: Use when angled traffic cameras must be projected onto top-down ground planes.
---

# Perspective / Homography Warping (Bird's-Eye View)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when angled traffic cameras must be projected onto top-down ground planes.

## Workflow

1. Estimate homography from camera to ground plane.
2. Warp frame to bird's-eye view.
3. Preserve metric scale.
4. Validate vehicle shapes.

## Output

Bird's-eye view frames.
