---
name: WebRTC Low-Latency Relay
description: Use when converting RTSP feeds to WebRTC via MediaMTX or Janus for browser playback.
---

# WebRTC Low-Latency Relay

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when converting RTSP feeds to WebRTC via MediaMTX or Janus for browser playback.

## Workflow

1. Ingest the RTSP source into MediaMTX/Janus.
2. Configure STUN/TURN and ICE candidates.
3. Expose a WHEP/WHIP endpoint for browsers.
4. Tune jitter buffer and bitrate for sub-second latency.
5. Monitor connection state and re-negotiate on drops.

## Output

Sub-second browser playback of camera feeds.
