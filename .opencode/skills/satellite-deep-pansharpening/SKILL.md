---
name: Deep Residual Pansharpening (PanNet / FusionNet)
description: Use when deep pansharpening networks must preserve sharp narrow road features while retaining true color radiometry.
---

# Deep Residual Pansharpening (PanNet / FusionNet)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when deep pansharpening networks must preserve sharp narrow road features while retaining true color radiometry.

## Workflow

1. Train or apply the network in the reduced-resolution setting to respect Wald protocol.
2. Feed both PAN and MS bands and let the network inject spatial detail into the MS product.
3. Check spectral fidelity with Q2n and ERGAS metrics, not just visual sharpness.
4. Fall back to classical Gram-Schmidt if the network shifts color on vegetation or asphalt.

## Output

Pan-sharpened output with joint spatial-spectral fidelity.
