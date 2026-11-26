---
name: Background Subtraction (MOG2 / KNN)
description: Use when moving foreground blobs must be isolated on static cameras.
---

# Background Subtraction (MOG2 / KNN)

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when moving foreground blobs must be isolated on static cameras.

## Workflow

1. Model background with MOG2/KNN.
2. Extract foreground blobs.
3. Filter by size and motion.
4. Run before heavy neural nets.

## Output

Foreground blob masks.
