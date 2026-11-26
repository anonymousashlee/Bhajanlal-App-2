---
name: Rotator Az/El Controller
description: Use when outputting rotctld/Hamlib commands to steer dish antennas across satellite passes.
---

# Rotator Az/El Controller

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when outputting rotctld/Hamlib commands to steer dish antennas across satellite passes.

## Workflow

1. Compute az/el over pass.
2. Generate rotctld commands.
3. Handle limits and backlash.
4. Log tracking.
5. Failsafe on errors.

## Output

Antenna rotator control.
