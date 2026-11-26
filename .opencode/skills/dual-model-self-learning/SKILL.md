---
name: dual-model-self-learning
description: Use when running Bhajanlal Pro Max 2.5 Free (ensemble) and Bhajanlal Local 0.5B together for self-learning and skills learning.
---

# dual-model-self-learning

Part of the **Bhajanlal** model-building skill library. Pillar: 110. Dual-Model Self-Learning (1 skill)

Use when running Bhajanlal Pro Max 2.5 Free (ensemble) and Bhajanlal Local 0.5B together for self-learning and skills learning.

## Workflow

1. Route high-quality requests to the ensemble (Bhajanlal Pro Max 2.5 Free).
2. Distill ensemble responses into training data via train/gen_distill.py.
3. Train the local 0.5B student on distilled + skill data (train_v18).
4. Evaluate and promote the local checkpoint if gates pass.
5. Both models share the skill library (.opencode/skills).

## Output

A self-improving local model guided by the ensemble, with shared skills.
