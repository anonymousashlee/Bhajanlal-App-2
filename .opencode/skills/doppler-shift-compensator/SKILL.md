---
name: Doppler Shift Compensator
description: Use when computing real-time frequency offsets for UHF/S-band/X-band downlinks during passes.
---

# Doppler Shift Compensator

Part of the **Bhajanlal** model-building skill library. Pillar: 112. Satellite & Geospatial Engineering (50 skills)

Use when computing real-time frequency offsets for UHF/S-band/X-band downlinks during passes.

## Workflow

1. Compute relative velocity.
2. Calculate Doppler offset.
3. Generate correction curve.
4. Apply to SDR.
5. Log compensation.

## Output

Doppler correction profile.
