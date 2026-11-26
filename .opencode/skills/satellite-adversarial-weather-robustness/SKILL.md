---
name: Adversarial & Weather-Robustness Testing
description: Use when benchmarking clarity pipelines across rain-slicked roads, snow glare, and dusk lighting.
---

# Adversarial & Weather-Robustness Testing

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when benchmarking clarity pipelines across rain-slicked roads, snow glare, and dusk lighting.

## Workflow

1. Assemble a test set spanning rain, snow, glare, dusk, and haze.
2. Run the full pipeline on each condition and score with IQA and detection metrics.
3. Compare against a clear-weather baseline to find condition-specific gaps.
4. Add failing conditions to the training or tuning loop.

## Output

Robustness report per weather and lighting condition.
