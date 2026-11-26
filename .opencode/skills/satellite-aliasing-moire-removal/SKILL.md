---
name: Aliasing & Moire Pattern Removal
description: Use when suppressing Nyquist aliasing artifacts along dashed lane lines and crosswalks.
---

# Aliasing & Moire Pattern Removal

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when suppressing Nyquist aliasing artifacts along dashed lane lines and crosswalks.

## Workflow

1. Identify aliasing as periodic energy near the Nyquist frequency.
2. Apply an anti-aliasing notch filter or re-sample above Nyquist when possible.
3. For color moire, desaturate only the aliased high-frequency color channel.
4. Verify lane dash geometry looks continuous, not scalloped.

## Output

Anti-aliased image without moire on periodic road features.
