---
name: Oriented Bounding Box (OBB) Detection
description: Use when predicting rotated bounding boxes aligned with road direction and shadow orientation.
---

# Oriented Bounding Box (OBB) Detection

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when predicting rotated bounding boxes aligned with road direction and shadow orientation.

## Workflow

1. Annotate or fit rotated boxes (angle + dimensions) for targets.
2. Train an OBB detector with rotated IoU or KLD loss.
3. Rotate boxes to road heading for consistent downstream reporting.
4. Check long thin silhouettes are tightly enclosed, not axis-aligned and bloated.

## Output

Rotated detections aligned with target and road orientation.
