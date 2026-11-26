---
name: Video Watermark Hasher
description: Use when embedding cryptographic timestamps and SHA-256 hashes for evidentiary chain-of-custody.
---

# Video Watermark Hasher

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when embedding cryptographic timestamps and SHA-256 hashes for evidentiary chain-of-custody.

## Workflow

1. Compute SHA-256 of source clip.
2. Embed timestamp and hash watermark.
3. Store manifest with signatures.
4. Verify on export.
5. Log chain-of-custody events.

## Output

Tamper-evident watermarked clips.
