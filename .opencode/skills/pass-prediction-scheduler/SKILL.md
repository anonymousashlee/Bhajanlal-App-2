---
name: Pass Prediction Scheduler
description: Use when calculating upcoming AOS/LOS elevation windows for a given ground station lat/lon.
---

# Pass Prediction Scheduler

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when calculating upcoming AOS/LOS elevation windows for a given ground station lat/lon.

## Workflow

1. Set station coordinates.
2. Propagate satellite orbit.
3. Find AOS/LOS windows.
4. Filter by min elevation.
5. Schedule observations.

## Output

Pass prediction schedule.
