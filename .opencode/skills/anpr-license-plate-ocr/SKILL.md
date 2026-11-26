---
name: ANPR License Plate OCR
description: Use when building pipelines combining vehicle bounding boxes with PaddleOCR/EasyOCR for plate reading.
---

# ANPR License Plate OCR

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when building pipelines combining vehicle bounding boxes with PaddleOCR/EasyOCR for plate reading.

## Workflow

1. Detect vehicles and crop plate regions.
2. Preprocess crops (deskew, threshold).
3. Run OCR with plate-specific models.
4. Post-process and validate plate format.
5. Log reads with confidence and images.

## Output

License plate recognition pipeline.
