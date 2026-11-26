---
name: Sub-Pixel Shift Estimation (Sub-Pixel Registration)
description: Use when aligning sequential burst frames to within 0.05-pixel accuracy before multi-frame fusion.
---

# Sub-Pixel Shift Estimation (Sub-Pixel Registration)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when aligning sequential burst frames to within 0.05-pixel accuracy before multi-frame fusion.

## Workflow

1. Estimate the coarse shift with phase correlation on overlapping regions.
2. Refine with sub-pixel interpolation of the correlation peak (parabolic fit).
3. Reject frames whose shift error exceeds the threshold or that are cloud-covered.
4. Verify residuals on static road features after alignment.

## Output

Frame stack aligned to about 0.05 px, ready for fusion.
