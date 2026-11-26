---
name: RTSP Stream Ingestor
description: Use when configuring and troubleshooting RTSP/RTP video streams using FFmpeg or GStreamer.
---

# RTSP Stream Ingestor

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when configuring and troubleshooting RTSP/RTP video streams using FFmpeg or GStreamer.

## Workflow

1. Identify the camera RTSP URL, credentials, and transport (TCP/UDP).
2. Probe the stream with ffprobe to confirm codec, resolution, and FPS.
3. Build an FFmpeg/GStreamer pipeline with reconnect and timeout flags.
4. Tune buffer sizes and latency for stable ingestion.
5. Log errors and auto-restart on stream drops.

## Output

Working, auto-reconnecting RTSP ingestion pipeline.
