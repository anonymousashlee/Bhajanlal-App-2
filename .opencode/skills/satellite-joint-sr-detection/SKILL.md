---
name: Super-Resolution Assisted Detection (Joint SR + Detection)
description: Use when backpropagating object detection loss directly into the super-resolution generator.
---

# Super-Resolution Assisted Detection (Joint SR + Detection)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when backpropagating object detection loss directly into the super-resolution generator.

## Workflow

1. Chain the SR generator into the detector as one network.
2. Backpropagate detection loss through the SR stage.
3. Add a fidelity term so SR cannot invent target-like texture.
4. Compare end-to-end mAP against detect-on-raw and SR-then-detect pipelines.

## Output

Joint model where SR is optimized for detection recall.
