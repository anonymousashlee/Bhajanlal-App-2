---
name: Dense Optical Flow (RAFT / Farnebäck)
description: Use when per-pixel motion vectors must spot moving objects even when camouflaged.
---

# Dense Optical Flow (RAFT / Farnebäck)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when per-pixel motion vectors must spot moving objects even when camouflaged.

## Workflow

1. Compute dense flow with RAFT/Farnebäck.
2. Threshold motion magnitude.
3. Detect moving objects by flow.
4. Validate on camouflaged targets.

## Output

Motion-vector maps.
