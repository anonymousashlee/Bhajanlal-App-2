---
name: Feature Pyramid Networks (FPN / PANet / BiFPN)
description: Use when fusing shallow, high-resolution P2 feature layers where single-pixel spatial details still survive.
---

# Feature Pyramid Networks (FPN / PANet / BiFPN)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when fusing shallow, high-resolution P2 feature layers where single-pixel spatial details still survive.

## Workflow

1. Enable a P2 output level so tiny targets are not downsampled away.
2. Fuse top-down and bottom-up paths (BiFPN for weighted fusion).
3. Attach detection heads at P2 and P3 for scale coverage.
4. Check that single-pixel candidates still activate at P2.

## Output

Multi-scale features retaining tiny-target signal.
