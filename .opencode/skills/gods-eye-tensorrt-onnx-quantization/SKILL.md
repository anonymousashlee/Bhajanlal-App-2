---
name: TensorRT / ONNX FP16/INT8 Quantization
description: Use when vision models must be compiled for 3x-5x faster real-time FPS.
---

# TensorRT / ONNX FP16/INT8 Quantization

Part of the **Bhajanlal** model-building skill library. Pillar: 104. God's Eye View - Image Clarity & Car/Human Detection (100 skills)

Use when vision models must be compiled for 3x-5x faster real-time FPS.

## Workflow

1. Export to ONNX.
2. Quantize to FP16/INT8.
3. Compile with TensorRT.
4. Benchmark FPS on target GPU.

## Output

Quantized fast inference engine.
