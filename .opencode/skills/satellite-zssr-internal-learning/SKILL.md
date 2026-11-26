---
name: Zero-Shot Internal Learning (ZSSR)
description: Use when adapting super-resolution weights on the fly from recurring patches within a single satellite scene with no external data.
---

# Zero-Shot Internal Learning (ZSSR)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when adapting super-resolution weights on the fly from recurring patches within a single satellite scene with no external data.

## Workflow

1. Extract self-similar low-res/high-res patch pairs from the scene itself.
2. Fine-tune a small SR network for a few hundred iterations on those pairs.
3. Apply the scene-specific model to the target region.
4. Stop early if validation on held-out internal pairs degrades.

## Output

Scene-adapted SR model trained with zero external data.
