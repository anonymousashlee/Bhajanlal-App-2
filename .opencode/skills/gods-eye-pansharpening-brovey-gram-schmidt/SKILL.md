---
name: Pansharpening (Brovey / Gram-Schmidt / PanNet)
description: Use when high-res panchromatic bands must be fused with lower-res RGB bands.
---

# Pansharpening (Brovey / Gram-Schmidt / PanNet)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when high-res panchromatic bands must be fused with lower-res RGB bands.

## Workflow

1. Resample multispectral to PAN grid.
2. Inject spatial detail via chosen method.
3. Restore color statistics.
4. Validate road features.

## Output

Pan-sharpened color frames.
