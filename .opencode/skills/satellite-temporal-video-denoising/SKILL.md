---
name: Temporal Denoising for Video Satellites
description: Use when filtering frame-to-frame sensor grain while locking onto moving objects.
---

# Temporal Denoising for Video Satellites

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when filtering frame-to-frame sensor grain while locking onto moving objects.

## Workflow

1. Align frames with motion compensation before temporal filtering.
2. Weight a temporal window by photometric and geometric similarity.
3. Exclude pixels where motion indicates a real moving target.
4. Confirm moving pedestrians stay sharp while static noise averages out.

## Output

Temporally denoised frames with moving targets intact.
