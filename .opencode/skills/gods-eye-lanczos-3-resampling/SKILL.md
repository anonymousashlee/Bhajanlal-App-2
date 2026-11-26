---
name: Lanczos-3 Resampling
description: Use when sinc-based windowing must minimize aliasing during zoom.
---

# Lanczos-3 Resampling

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when sinc-based windowing must minimize aliasing during zoom.

## Workflow

1. Apply the Lanczos-3 kernel for high-quality resampling.
2. Use for offline tile preprocessing and UI zoom previews.
3. Clip negative lobes carefully to avoid ringing on high contrast.
4. Compare against bicubic for aliasing on diagonal road lines.

## Output

Alias-minimized resampled frames.
