---
name: Temporal Frame Averaging
description: Use when static background pixels must be averaged to drop the noise floor.
---

# Temporal Frame Averaging

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when static background pixels must be averaged to drop the noise floor.

## Workflow

1. Maintain exponential moving average of background.
2. Update only static regions; mask moving objects.
3. Tune decay factor for noise vs responsiveness.
4. Use before detection on fixed cameras.

## Output

Temporally averaged low-noise frames.
