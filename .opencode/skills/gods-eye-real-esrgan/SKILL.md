---
name: Real-ESRGAN
description: Use when upscaling real-world degraded surveillance footage to recover recognizable cars and pedestrians.
---

# Real-ESRGAN

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when upscaling real-world degraded surveillance footage to recover recognizable cars and pedestrians.

## Workflow

1. Confirm the source resolution and pick a 2x/4x scale whose degradation matches the sensor.
2. Run tiled inference with overlap so large frames stay inside GPU memory.
3. Prefer the RRDB-based generator for heavy compression artifacts and blur.
4. Inspect upscaled crops at 100% for hallucinated texture before accepting.

## Output

Sharper surveillance frames with recovered vehicle and pedestrian detail.
