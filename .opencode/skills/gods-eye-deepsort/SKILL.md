---
name: DeepSORT
description: Use when appearance embeddings must maintain IDs after occlusion.
---

# DeepSORT

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when appearance embeddings must maintain IDs after occlusion.

## Workflow

1. Extract appearance embeddings.
2. Match via cosine distance + motion.
3. Maintain IDs through occlusion.
4. Validate on pedestrians.

## Output

Appearance-stable tracks.
