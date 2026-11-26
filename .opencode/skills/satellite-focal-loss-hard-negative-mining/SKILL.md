---
name: Focal Loss & Hard Negative Mining
description: Use when suppressing false positives from manhole covers, fire hydrants, road markings, and trash bins.
---

# Focal Loss & Hard Negative Mining

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when suppressing false positives from manhole covers, fire hydrants, road markings, and trash bins.

## Workflow

1. Apply focal loss to down-weight easy background examples.
2. Mine hard negatives - confident false positives - and add them to training.
3. Keep a curated hard-negative set of road furniture lookalikes.
4. Track false-positive rate per category across training rounds.

## Output

Detector with fewer road-furniture false alarms.
