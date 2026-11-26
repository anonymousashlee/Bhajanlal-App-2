---
name: S3 Clip Uploader
description: Use when automatically pushing high-priority alert clips to S3-compatible object storage with lifecycle rules.
---

# S3 Clip Uploader

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when automatically pushing high-priority alert clips to S3-compatible object storage with lifecycle rules.

## Workflow

1. Watch alert clip directory.
2. Upload with retry and checksum.
3. Apply lifecycle and retention rules.
4. Tag objects with metadata.
5. Log upload status.

## Output

Automated alert clip uploads to S3.
