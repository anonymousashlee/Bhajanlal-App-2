---
name: ONVIF Device Discovery
description: Use when scanning local networks for ONVIF-compliant IP cameras and extracting stream profiles.
---

# ONVIF Device Discovery

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when scanning local networks for ONVIF-compliant IP cameras and extracting stream profiles.

## Workflow

1. Run WS-Discovery multicast probe on the LAN.
2. Parse device service URLs and capabilities.
3. Authenticate and fetch media profiles and RTSP URIs.
4. Store discovered cameras and profiles in a registry.
5. Handle non-ONVIF fallbacks gracefully.

## Output

Inventory of ONVIF cameras with stream profiles.
