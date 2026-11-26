---
name: Matched Filtering & ACE (Adaptive Cosine Estimator)
description: Use when detecting sub-pixel spectral anomalies against local asphalt background statistics.
---

# Matched Filtering & ACE (Adaptive Cosine Estimator)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when detecting sub-pixel spectral anomalies against local asphalt background statistics.

## Workflow

1. Estimate the background mean and covariance from the local region.
2. Project each pixel spectrum onto the target signature (matched filter) or compute ACE.
3. Normalize so the statistic has a constant false-alarm rate.
4. Threshold at a validated CFAR level and cluster the hits.

## Output

CFAR-controlled anomaly hits for sub-pixel targets.
