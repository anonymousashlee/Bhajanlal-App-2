---
name: Virtual Tripwire Line Crossing
description: Use when calculating vector intersections to trigger alerts when targets cross boundary lines.
---

# Virtual Tripwire Line Crossing

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when calculating vector intersections to trigger alerts when targets cross boundary lines.

## Workflow

1. Define tripwire line segments in scene coordinates.
2. Track object centroids per frame.
3. Compute vector intersection per crossing.
4. Debounce and direction-filter events.
5. Emit alerts with metadata.

## Output

Line-crossing event detector.
