---
name: Jitter & Attitude Distortion Compensation
description: Use when correcting micro-vibration ripples using onboard star-tracker and gyroscope telemetry.
---

# Jitter & Attitude Distortion Compensation

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when correcting micro-vibration ripples using onboard star-tracker and gyroscope telemetry.

## Workflow

1. Pull per-frame attitude telemetry covering the exposure window.
2. Convert attitude deltas into a per-row or per-pixel displacement map.
3. Warp the image to cancel the ripple, then apply mild sharpening.
4. Verify straight road edges are actually straight after correction.

## Output

Jitter-free image corrected from spacecraft telemetry.
