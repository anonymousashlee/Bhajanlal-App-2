---
name: Auto-Camera Pose Estimation (PnP / PnL)
description: Use when live 2D CCTV feeds must be aligned onto 3D building geometry.
---

# Auto-Camera Pose Estimation (PnP / PnL)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when live 2D CCTV feeds must be aligned onto 3D building geometry.

## Workflow

1. Detect 2D-3D correspondences.
2. Solve PnP for camera pose.
3. Align feed to 3D geometry.
4. Validate on auto-calibrated globes.

## Output

Pose-aligned camera feeds.
