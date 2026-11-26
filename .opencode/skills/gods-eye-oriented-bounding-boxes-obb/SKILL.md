---
name: Oriented Bounding Boxes (OBB / Rotated YOLO)
description: Use when angled boxes must fit diagonally parked/turning cars.
---

# Oriented Bounding Boxes (OBB / Rotated YOLO)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when angled boxes must fit diagonally parked/turning cars.

## Workflow

1. Predict rotation angle per box.
2. Use rotated IoU for NMS.
3. Tune on aerial vehicle datasets.
4. Validate on angled cars.

## Output

Tightly fitted rotated detections.
