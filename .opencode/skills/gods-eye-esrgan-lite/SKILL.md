---
name: ESRGAN-Lite
description: Use when pruned generator weights must run super-resolution in browser/WebGPU.
---

# ESRGAN-Lite

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when pruned generator weights must run super-resolution in browser/WebGPU.

## Workflow

1. Prune and quantize ESRGAN generator weights for web inference.
2. Keep patch size small to fit WebGPU memory limits.
3. Use FP16 or INT8 weights for 2-3x speedup.
4. Benchmark on-device FPS before shipping.

## Output

WebGPU-ready lightweight super-resolution.
