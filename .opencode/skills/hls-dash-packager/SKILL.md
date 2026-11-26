---
name: HLS/DASH Packager
description: Use when segmenting live camera feeds into HLS or MPEG-DASH playlists for scalable web delivery.
---

# HLS/DASH Packager

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when segmenting live camera feeds into HLS or MPEG-DASH playlists for scalable web delivery.

## Workflow

1. Transmux RTSP into segmented fMP4/CMAF.
2. Generate master and media playlists with multiple bitrates.
3. Configure segment duration and keyframe alignment.
4. Serve via CDN or local HTTP origin.
5. Validate playback across target players.

## Output

Adaptive HLS/DASH live stream with ABR.
