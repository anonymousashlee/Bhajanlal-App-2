---
name: Multi-Object Tracking (ByteTrack / StrongSORT for Overhead Video)
description: Use when linking faint detections across frames to maintain identity even when a target briefly fades into noise.
---

# Multi-Object Tracking (ByteTrack / StrongSORT for Overhead Video)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when linking faint detections across frames to maintain identity even when a target briefly fades into noise.

## Workflow

1. Run per-frame detection and compute motion-constant predictions.
2. Associate by IoU plus appearance or motion features across gaps.
3. Keep low-confidence detections in a second association stage (ByteTrack).
4. Report identity switches and track fragmentation rates.

## Output

Stable tracks with persistent IDs across frames.
