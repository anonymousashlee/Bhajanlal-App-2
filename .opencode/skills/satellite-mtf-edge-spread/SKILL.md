---
name: Modulation Transfer Function (MTF) & Edge Spread Measurement
description: Use when measuring true spatial sharpness using painted road crosswalks as natural slanted-edge targets.
---

# Modulation Transfer Function (MTF) & Edge Spread Measurement

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when measuring true spatial sharpness using painted road crosswalks as natural slanted-edge targets.

## Workflow

1. Locate a slanted high-contrast edge (crosswalk stripe, curb line).
2. Extract the edge spread function and differentiate to the line spread function.
3. FFT to get the MTF curve and read MTF50.
4. Compare MTF50 across passes and processing versions.

## Output

MTF curve quantifying true spatial sharpness.
