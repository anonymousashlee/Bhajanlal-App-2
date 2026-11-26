---
name: BasicVSR++
description: Use when bidirectional propagation across adjacent CCTV frames must upscale moving vehicles.
---

# BasicVSR++

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when bidirectional propagation across adjacent CCTV frames must upscale moving vehicles.

## Workflow

1. Align adjacent frames with flow-guided deformable alignment.
2. Propagate features bidirectionally through the sequence.
3. Aggregate temporal information with second-order grid propagation.
4. Check for ghosting on fast-moving cars and pedestrians.

## Output

Temporally fused super-resolved video frames.
