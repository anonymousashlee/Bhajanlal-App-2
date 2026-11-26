---
name: Multi-Object Tracker (ByteTrack)
description: Use when implementing ByteTrack or DeepSORT to maintain persistent IDs across frames.
---

# Multi-Object Tracker (ByteTrack)

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when implementing ByteTrack or DeepSORT to maintain persistent IDs across frames.

## Workflow

1. Run per-frame detections.
2. Associate detections by IoU and motion.
3. Keep low-confidence detections for second association.
4. Manage track lifecycle and IDs.
5. Evaluate ID switches and MOTA.

## Output

Persistent multi-object tracking.
