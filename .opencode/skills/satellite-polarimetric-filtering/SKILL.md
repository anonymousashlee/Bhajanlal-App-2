---
name: Polarimetric Filtering
description: Use when filtering polarized sunlight reflected off flat asphalt to reveal non-flat vertical objects.
---

# Polarimetric Filtering

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when filtering polarized sunlight reflected off flat asphalt to reveal non-flat vertical objects.

## Workflow

1. Acquire or synthesize polarization channels (Stokes parameters).
2. Suppress the strongly polarized specular road component.
3. Keep depolarized returns that indicate vertical structures.
4. Feed the filtered contrast into detection as an additional cue.

## Output

Polarization-filtered contrast isolating upright objects.
