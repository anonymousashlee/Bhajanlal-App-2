---
name: Active Zoom-and-Crop (Foveated Inference)
description: Use when fast low-res detection must trigger SR + high-res detection on candidate regions.
---

# Active Zoom-and-Crop (Foveated Inference)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when fast low-res detection must trigger SR + high-res detection on candidate regions.

## Workflow

1. Run fast low-res detector on full frame.
2. Crop regions with candidates.
3. Apply SR + high-res detection on crops.
4. Merge results back.

## Output

Foveated high-res detections.
