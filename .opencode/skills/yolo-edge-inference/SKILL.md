---
name: YOLO Edge Inference
description: Use when deploying YOLOv8/v11 models on TensorRT or OpenVINO for real-time person and vehicle detection.
---

# YOLO Edge Inference

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when deploying YOLOv8/v11 models on TensorRT or OpenVINO for real-time person and vehicle detection.

## Workflow

1. Export the YOLO model to ONNX/TensorRT/OpenVINO.
2. Calibrate INT8/FP16 for target hardware.
3. Build a threaded inference pipeline.
4. Apply NMS and confidence thresholds.
5. Benchmark FPS and accuracy on target device.

## Output

Real-time edge detection pipeline.
