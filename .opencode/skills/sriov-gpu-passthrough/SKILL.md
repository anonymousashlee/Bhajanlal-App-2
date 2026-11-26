---
name: SR-IOV GPU Passthrough
description: Use when configuring hardware-accelerated video decoding (NVDEC/VAAPI) in Docker containers.
---

# SR-IOV GPU Passthrough

Part of the **Bhajanlal** model-building skill library. Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)

Use when configuring hardware-accelerated video decoding (NVDEC/VAAPI) in Docker containers.

## Workflow

1. Enable IOMMU and GPU passthrough on host.
2. Install container toolkit and device plugins.
3. Map GPU devices into containers.
4. Configure NVDEC/VAAPI decode in FFmpeg/GStreamer.
5. Benchmark decode throughput and latency.

## Output

Hardware-accelerated decode inside containers.
