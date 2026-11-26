---
name: Thermal Infrared (LWIR) Anomaly Fusion
description: Use when pairing thermal contrast with optical imagery to spot warm human signatures against cool pavement.
---

# Thermal Infrared (LWIR) Anomaly Fusion

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when pairing thermal contrast with optical imagery to spot warm human signatures against cool pavement.

## Workflow

1. Co-register thermal and optical bands geometrically.
2. Detect thermal anomalies against local pavement temperature statistics.
3. Fuse thermal anomaly maps with optical detections as an extra channel.
4. Validate against time-of-day thermal drift (night vs noon).

## Output

Fused thermal-optical detection of warm human signatures.
