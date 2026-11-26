---
name: DnCNN
description: Use when residual learning CNN must remove blind Gaussian noise from feeds.
---

# DnCNN

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when residual learning CNN must remove blind Gaussian noise from feeds.

## Workflow

1. Train residual mapping from noisy to clean.
2. Use batch normalization for stable deep training.
3. Handle blind noise via noise-level map input.
4. Validate on real sensor noise, not synthetic only.

## Output

Gaussian-denoised frames.
