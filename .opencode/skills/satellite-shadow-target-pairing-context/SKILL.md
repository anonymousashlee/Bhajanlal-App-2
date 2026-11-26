---
name: Context-Aware Shadow-Target Pairing
description: Use when training detectors to recognize a pedestrian and their elongated cast shadow as a single joint signature.
---

# Context-Aware Shadow-Target Pairing

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when training detectors to recognize a pedestrian and their elongated cast shadow as a single joint signature.

## Workflow

1. Annotate the target together with its cast shadow as one region.
2. Add shadow-context features or a shadow channel as detector input.
3. Balance training so shadowless targets (overcast) still detect.
4. Verify paired detections merge target and shadow into one box.

## Output

Detector using joint target-shadow signatures for recall.
