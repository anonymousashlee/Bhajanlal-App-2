---
name: Dark Channel Prior (DCP) Dehazing
description: Use when atmospheric transmission must be estimated to strip fog/smog.
---

# Dark Channel Prior (DCP) Dehazing

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when atmospheric transmission must be estimated to strip fog/smog.

## Workflow

1. Estimate dark channel and transmission map.
2. Refine transmission with guided filter.
3. Recover scene radiance.
4. Validate on hazy roads.

## Output

Dehazed frames.
