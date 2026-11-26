---
name: True-Color & False-Color Band Synthesis
description: Use when combining Red-Edge and Near-Infrared (NIR) bands to separate organic skin/clothing from mineral asphalt.
---

# True-Color & False-Color Band Synthesis

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when combining Red-Edge and Near-Infrared (NIR) bands to separate organic skin/clothing from mineral asphalt.

## Workflow

1. Pick the band combination for the goal - NIR false color for vegetation/skin, red-edge for stress.
2. Normalize each band before compositing to avoid channel dominance.
3. Render as RGB and check class separability on labeled crops.
4. Document the band mapping so results are interpretable.

## Output

Band composite that separates targets from asphalt background.
