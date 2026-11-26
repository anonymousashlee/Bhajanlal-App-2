---
name: Total Variation (TV) Denoising
description: Use when image gradient variation must be minimized while preserving sharp boundaries.
---

# Total Variation (TV) Denoising

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when image gradient variation must be minimized while preserving sharp boundaries.

## Workflow

1. Minimize TV functional with gradient descent.
2. Tune regularization lambda for noise vs detail.
3. Use anisotropic TV for directional preservation.
4. Validate object boundary sharpness.

## Output

TV-denoised frames with sharp boundaries.
