#!/usr/bin/env python3
"""Generate 100 CCTV & Satellite/Geospatial engineering skills.

50 CCTV/video surveillance + 50 satellite/geospatial. Each follows the
Bhajanlal SKILL.md convention (YAML frontmatter + pillar line + workflow).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "skills"

PILLAR_CCTV = ("Part of the **Bhajanlal** model-building skill library. "
               "Pillar: 111. CCTV & Video Surveillance Engineering (50 skills)")
PILLAR_SAT = ("Part of the **Bhajanlal** model-building skill library. "
              "Pillar: 112. Satellite & Geospatial Engineering (50 skills)")

# (id, name, desc, steps, output, pillar)
SKILLS = []

def add(pid, name, desc, steps, output, pillar):
    SKILLS.append({"id": pid, "name": name, "desc": desc,
                   "steps": steps, "output": output, "pillar": pillar})

# ============================================================ Part 1: CCTV
C = PILLAR_CCTV
add("rtsp-stream-ingestor", "RTSP Stream Ingestor",
 "Use when configuring and troubleshooting RTSP/RTP video streams using FFmpeg or GStreamer.",
 ["Identify the camera RTSP URL, credentials, and transport (TCP/UDP).",
  "Probe the stream with ffprobe to confirm codec, resolution, and FPS.",
  "Build an FFmpeg/GStreamer pipeline with reconnect and timeout flags.",
  "Tune buffer sizes and latency for stable ingestion.",
  "Log errors and auto-restart on stream drops."],
 "Working, auto-reconnecting RTSP ingestion pipeline.", C)
add("onvif-device-discovery", "ONVIF Device Discovery",
 "Use when scanning local networks for ONVIF-compliant IP cameras and extracting stream profiles.",
 ["Run WS-Discovery multicast probe on the LAN.",
  "Parse device service URLs and capabilities.",
  "Authenticate and fetch media profiles and RTSP URIs.",
  "Store discovered cameras and profiles in a registry.",
  "Handle non-ONVIF fallbacks gracefully."],
 "Inventory of ONVIF cameras with stream profiles.", C)
add("webrtc-low-latency-relay", "WebRTC Low-Latency Relay",
 "Use when converting RTSP feeds to WebRTC via MediaMTX or Janus for browser playback.",
 ["Ingest the RTSP source into MediaMTX/Janus.",
  "Configure STUN/TURN and ICE candidates.",
  "Expose a WHEP/WHIP endpoint for browsers.",
  "Tune jitter buffer and bitrate for sub-second latency.",
  "Monitor connection state and re-negotiate on drops."],
 "Sub-second browser playback of camera feeds.", C)
add("hls-dash-packager", "HLS/DASH Packager",
 "Use when segmenting live camera feeds into HLS or MPEG-DASH playlists for scalable web delivery.",
 ["Transmux RTSP into segmented fMP4/CMAF.",
  "Generate master and media playlists with multiple bitrates.",
  "Configure segment duration and keyframe alignment.",
  "Serve via CDN or local HTTP origin.",
  "Validate playback across target players."],
 "Adaptive HLS/DASH live stream with ABR.", C)
add("multicast-udp-router", "Multicast UDP Router",
 "Use when optimizing local network multicast settings to prevent packet loss across multi-camera setups.",
 ["Enable IGMP snooping on switches.",
  "Assign unique multicast groups per camera.",
  "Set TTL and socket buffers appropriately.",
  "Monitor packet loss and jitter.",
  "Document network topology and group map."],
 "Loss-minimized multicast video distribution.", C)
add("rtmp-ingest-server", "RTMP Ingest Server",
 "Use when setting up Nginx-RTMP endpoints for remote cellular or edge camera uploads.",
 ["Install and configure nginx-rtmp module.",
  "Define application endpoints and stream keys.",
  "Enable recording and HLS repackaging.",
  "Secure with stream-key auth or token validation.",
  "Monitor ingest health and bandwidth."],
 "RTMP ingest endpoint accepting edge uploads.", C)
add("sriov-gpu-passthrough", "SR-IOV GPU Passthrough",
 "Use when configuring hardware-accelerated video decoding (NVDEC/VAAPI) in Docker containers.",
 ["Enable IOMMU and GPU passthrough on host.",
  "Install container toolkit and device plugins.",
  "Map GPU devices into containers.",
  "Configure NVDEC/VAAPI decode in FFmpeg/GStreamer.",
  "Benchmark decode throughput and latency."],
 "Hardware-accelerated decode inside containers.", C)
add("camera-health-watchdog", "Camera Health Watchdog",
 "Use when writing heartbeat scripts to detect frozen frames, black screens, or offline IP cameras.",
 ["Periodically grab a frame from each camera.",
  "Compute frame hash / motion / brightness metrics.",
  "Detect freeze, black screen, or offline state.",
  "Emit alerts and attempt reconnect.",
  "Log incidents with timestamps."],
 "Automated camera uptime and quality watchdog.", C)
add("ptz-pelco-onvif-controller", "PTZ Pelco/ONVIF Controller",
 "Use when implementing pan-tilt-zoom preset tours and HTTP/ONVIF control APIs.",
 ["Map ONVIF/Pelco-D/P commands to camera endpoints.",
  "Implement preset save/recall and patrol tours.",
  "Expose REST/HTTP control API.",
  "Add speed and limit validation.",
  "Log all PTZ actions for audit."],
 "PTZ control service with presets and tours.", C)
add("audio-two-way-sip-bridge", "Audio Two-Way SIP Bridge",
 "Use when integrating G.711/AAC two-way audio channels from intercom cameras.",
 ["Negotiate SIP/RTP session with the camera.",
  "Configure G.711/AAC codecs and jitter buffers.",
  "Bridge audio to the operator client.",
  "Handle echo cancellation and gain control.",
  "Monitor audio quality and dropouts."],
 "Two-way audio bridge for intercom cameras.", C)
add("yolo-edge-inference", "YOLO Edge Inference",
 "Use when deploying YOLOv8/v11 models on TensorRT or OpenVINO for real-time person and vehicle detection.",
 ["Export the YOLO model to ONNX/TensorRT/OpenVINO.",
  "Calibrate INT8/FP16 for target hardware.",
  "Build a threaded inference pipeline.",
  "Apply NMS and confidence thresholds.",
  "Benchmark FPS and accuracy on target device."],
 "Real-time edge detection pipeline.", C)
add("frigate-nvr-configurator", "Frigate NVR Configurator",
 "Use when generating and validating YAML configurations for Frigate NVR object detection and zones.",
 ["Define cameras, roles, and stream inputs.",
  "Configure detectors and model paths.",
  "Set zones, masks, and object filters.",
  "Validate YAML and test detection.",
  "Tune retention and recording policies."],
 "Validated Frigate NVR configuration.", C)
add("anpr-license-plate-ocr", "ANPR License Plate OCR",
 "Use when building pipelines combining vehicle bounding boxes with PaddleOCR/EasyOCR for plate reading.",
 ["Detect vehicles and crop plate regions.",
  "Preprocess crops (deskew, threshold).",
  "Run OCR with plate-specific models.",
  "Post-process and validate plate format.",
  "Log reads with confidence and images."],
 "License plate recognition pipeline.", C)
add("multi-object-tracker-bytetrack", "Multi-Object Tracker (ByteTrack)",
 "Use when implementing ByteTrack or DeepSORT to maintain persistent IDs across frames.",
 ["Run per-frame detections.",
  "Associate detections by IoU and motion.",
  "Keep low-confidence detections for second association.",
  "Manage track lifecycle and IDs.",
  "Evaluate ID switches and MOTA."],
 "Persistent multi-object tracking.", C)
add("virtual-tripwire-line-crossing", "Virtual Tripwire Line Crossing",
 "Use when calculating vector intersections to trigger alerts when targets cross boundary lines.",
 ["Define tripwire line segments in scene coordinates.",
  "Track object centroids per frame.",
  "Compute vector intersection per crossing.",
  "Debounce and direction-filter events.",
  "Emit alerts with metadata."],
 "Line-crossing event detector.", C)
add("polygon-intrusion-zone", "Polygon Intrusion Zone",
 "Use when defining and testing region-of-interest (ROI) polygons for restricted area monitoring.",
 ["Define ROI polygons in camera coordinates.",
  "Test point-in-polygon for each target.",
  "Handle polygon updates at runtime.",
  "Visualize zones for operators.",
  "Log intrusions with snapshots."],
 "ROI-based intrusion monitoring.", C)
add("loitering-dwell-timer", "Loitering Dwell Timer",
 "Use when tracking object persistence inside a zone and alerting when dwell thresholds are exceeded.",
 ["Track objects inside the zone over time.",
  "Accumulate dwell time per ID.",
  "Apply movement tolerance to avoid false resets.",
  "Trigger alerts at threshold.",
  "Reset on exit and log events."],
 "Loitering detection with dwell timers.", C)
add("crowd-density-heatmap", "Crowd Density Heatmap",
 "Use when generating spatial occupancy heatmaps and headcount estimates from overhead feeds.",
 ["Detect or count people per frame.",
  "Accumulate counts into a spatial grid.",
  "Render heatmap overlays.",
  "Estimate total headcount.",
  "Alert on density thresholds."],
 "Crowd density heatmap and counts.", C)
add("ppe-safety-compliance", "PPE Safety Compliance",
 "Use when detecting hardhats, high-vis vests, and safety gear in industrial camera feeds.",
 ["Detect persons and PPE items.",
  "Associate PPE to each person.",
  "Evaluate compliance per zone.",
  "Log violations with snapshots.",
  "Generate compliance reports."],
 "PPE compliance monitoring.", C)
add("slip-and-fall-pose-estimator", "Slip and Fall Pose Estimator",
 "Use when using keypoint pose estimation to detect sudden falls in healthcare or warehouse settings.",
 ["Run pose estimation per frame.",
  "Compute body orientation and velocity.",
  "Detect sudden fall patterns.",
  "Trigger alerts and save clips.",
  "Reduce false positives via context."],
 "Fall detection via pose estimation.", C)
add("abandoned-object-detector", "Abandoned Object Detector",
 "Use when identifying stationary foreground objects left unattended for configurable durations.",
 ["Maintain background model and foreground blobs.",
  "Track stationary objects over time.",
  "Associate with nearby persons (owner).",
  "Trigger alert after duration threshold.",
  "Handle occlusions and scene changes."],
 "Abandoned object detection.", C)
add("camera-tamper-blur-detector", "Camera Tamper/Blur Detector",
 "Use when detecting lens obstruction, spray-paint occlusion, or sudden field-of-view shifts.",
 ["Monitor frame brightness and edge energy.",
  "Detect blur, occlusion, or shift.",
  "Compare against reference frame.",
  "Alert on tamper events.",
  "Log and snapshot evidence."],
 "Camera tamper detection.", C)
add("circular-buffer-retention", "Circular Buffer Retention",
 "Use when writing cron/systemd scripts to prune oldest recordings when disk usage hits 85%.",
 ["Monitor disk usage per camera pool.",
  "Define retention policies by priority.",
  "Prune oldest files when threshold exceeded.",
  "Protect active/alert clips.",
  "Log deletions and report freed space."],
 "Automated retention pruning scripts.", C)
add("motion-triggered-prebuffer", "Motion-Triggered Prebuffer",
 "Use when maintaining a 5-second RAM ring buffer to save pre-event footage upon motion triggers.",
 ["Maintain in-memory ring buffer of frames.",
  "On trigger, flush pre + post event footage.",
  "Write clips to disk with metadata.",
  "Tune buffer duration and size.",
  "Handle concurrent triggers."],
 "Pre-event capture on motion triggers.", C)
add("h265-transcode-archiver", "H.265 Transcode Archiver",
 "Use when batch-transcoding older H.264 archives to HEVC/AV1 to reduce cold storage costs.",
 ["Scan archive for H.264 candidates.",
  "Transcode to HEVC/AV1 with quality targets.",
  "Verify integrity and metadata.",
  "Replace originals after validation.",
  "Report space savings."],
 "Cold-storage transcoding pipeline.", C)
add("zfs-surveillance-pool-tuner", "ZFS Surveillance Pool Tuner",
 "Use when optimizing ZFS recordsize and sync settings for continuous multi-stream video writes.",
 ["Set recordsize to match video segment size.",
  "Tune sync/async and ARC cache.",
  "Enable compression and atime off.",
  "Monitor write latency and IOPS.",
  "Document pool configuration."],
 "ZFS pool tuned for video writes.", C)
add("s3-clip-uploader", "S3 Clip Uploader",
 "Use when automatically pushing high-priority alert clips to S3-compatible object storage with lifecycle rules.",
 ["Watch alert clip directory.",
  "Upload with retry and checksum.",
  "Apply lifecycle and retention rules.",
  "Tag objects with metadata.",
  "Log upload status."],
 "Automated alert clip uploads to S3.", C)
add("timelapse-frame-extractor", "Timelapse Frame Extractor",
 "Use when sampling one frame per minute from 24/7 footage and stitching daily MP4 summaries.",
 ["Sample frames at configured interval.",
  "Filter by time of day if needed.",
  "Stitch into daily MP4.",
  "Add timestamps and watermark.",
  "Archive and notify."],
 "Daily timelapse MP4 summaries.", C)
add("video-watermark-hasher", "Video Watermark Hasher",
 "Use when embedding cryptographic timestamps and SHA-256 hashes for evidentiary chain-of-custody.",
 ["Compute SHA-256 of source clip.",
  "Embed timestamp and hash watermark.",
  "Store manifest with signatures.",
  "Verify on export.",
  "Log chain-of-custody events."],
 "Tamper-evident watermarked clips.", C)
add("zoneminder-shinobi-migrator", "ZoneMinder/Shinobi Migrator",
 "Use when converting camera configurations between ZoneMinder, Shinobi, and Blue Iris.",
 ["Export camera configs from source NVR.",
  "Map fields to target schema.",
  "Generate target config files.",
  "Validate connectivity and streams.",
  "Document migration steps."],
 "Migrated NVR configuration.", C)
add("raid-array-io-monitor", "RAID Array I/O Monitor",
 "Use when monitoring disk write latency and IOPS bottlenecks on dedicated NVR servers.",
 ["Collect SMART and I/O stats.",
  "Track latency and IOPS per disk.",
  "Detect degraded arrays.",
  "Alert on thresholds.",
  "Report trends."],
 "RAID I/O health monitoring.", C)
add("event-clip-thumbnail-grid", "Event Clip Thumbnail Grid",
 "Use when generating sprite sheets and animated WebP previews for fast timeline scrubbing.",
 ["Extract keyframes from clips.",
  "Build sprite sheets.",
  "Generate animated WebP previews.",
  "Index for timeline UI.",
  "Cache and serve efficiently."],
 "Thumbnail grids and previews.", C)
add("face-blur-anonymizer", "Face Blur Anonymizer",
 "Use when applying real-time Gaussian blur to detected faces for GDPR/privacy compliance.",
 ["Detect faces in frame.",
  "Apply Gaussian blur to ROIs.",
  "Handle tracking to keep blur stable.",
  "Preserve audit logs.",
  "Configure blur strength and zones."],
 "Privacy-compliant blurred video.", C)
add("license-plate-redactor", "License Plate Redactor",
 "Use when automatically masking vehicle plates in public-facing or shared video exports.",
 ["Detect and track plates.",
  "Apply mask/blur to plate regions.",
  "Render redacted export.",
  "Keep original secured.",
  "Log redaction actions."],
 "Redacted video exports.", C)
add("camera-vlan-firewall-rules", "Camera VLAN Firewall Rules",
 "Use when generating iptables/nftables rules isolating IoT cameras from internet access.",
 ["Define VLAN and subnets.",
  "Generate firewall rules.",
  "Block outbound internet from cameras.",
  "Allow NVR/management access.",
  "Test and document rules."],
 "Firewall rules isolating cameras.", C)
add("tls-mutual-auth-proxy", "TLS Mutual Auth Proxy",
 "Use when wrapping legacy HTTP-only cameras behind an mTLS reverse proxy (Caddy/Nginx).",
 ["Configure reverse proxy.",
  "Issue client/server certs.",
  "Enforce mTLS authentication.",
  "Proxy camera endpoints.",
  "Log access."],
 "mTLS proxy for legacy cameras.", C)
add("default-credential-auditor", "Default Credential Auditor",
 "Use when scanning local camera endpoints for weak passwords or exposed telnet/HTTP ports.",
 ["Scan camera endpoints.",
  "Test default credentials.",
  "Check exposed services.",
  "Report vulnerabilities.",
  "Recommend remediation."],
 "Credential audit report.", C)
add("privacy-mask-overlay", "Privacy Mask Overlay",
 "Use when hard-burning static black polygons over neighboring properties at the ingestion layer.",
 ["Define mask polygons.",
  "Burn masks into frames at ingest.",
  "Persist mask config.",
  "Verify coverage.",
  "Log changes."],
 "Hard-burned privacy masks.", C)
add("gdpr-access-log-auditor", "GDPR Access Log Auditor",
 "Use when tracking and logging every user view or download of recorded surveillance footage.",
 ["Instrument view/download events.",
  "Store audit logs immutably.",
  "Generate access reports.",
  "Alert on anomalies.",
  "Support data subject requests."],
 "GDPR-compliant access audit trail.", C)
add("firmware-cve-checker", "Firmware CVE Checker",
 "Use when cross-referencing camera model numbers and firmware versions against known vulnerability databases.",
 ["Collect model/firmware inventory.",
  "Query CVE databases.",
  "Match and score risks.",
  "Report affected devices.",
  "Plan patching."],
 "Firmware vulnerability report.", C)
add("encrypted-at-rest-vault", "Encrypted-at-Rest Vault",
 "Use when configuring LUKS or fscrypt encryption for local NVR storage drives.",
 ["Select encryption scheme.",
  "Configure LUKS/fscrypt.",
  "Manage keys securely.",
  "Mount and verify.",
  "Document recovery."],
 "Encrypted NVR storage.", C)
add("mqtt-event-publisher", "MQTT Event Publisher",
 "Use when publishing structured JSON detection payloads to Mosquitto/EMQX brokers.",
 ["Connect to MQTT broker.",
  "Define topic schema.",
  "Publish detection events.",
  "Handle QoS and retries.",
  "Monitor broker health."],
 "MQTT detection event stream.", C)
add("home-assistant-webhook-bridge", "Home Assistant Webhook Bridge",
 "Use when triggering smart lighting, sirens, or mobile notifications on verified detections.",
 ["Configure webhook endpoints.",
  "Map detection types to actions.",
  "Send authenticated requests.",
  "Handle retries and failures.",
  "Log automations."],
 "Home Assistant automation bridge.", C)
add("telegram-snapshot-bot", "Telegram Snapshot Bot",
 "Use when sending annotated bounding-box snapshots with inline action buttons to Telegram.",
 ["Create bot and chat IDs.",
  "Send annotated images.",
  "Add inline buttons.",
  "Handle callbacks.",
  "Rate-limit messages."],
 "Telegram alert bot.", C)
add("false-positive-night-filter", "False Positive Night Filter",
 "Use when suppressing insect, rain, and IR-reflection triggers using confidence thresholds and size filters.",
 ["Analyze night false positives.",
  "Set confidence and size filters.",
  "Filter IR reflections and insects.",
  "Track false positive rate.",
  "Tune per scene."],
 "Night false-positive suppression.", C)
add("vlm-scene-describer", "VLM Scene Describer",
 "Use when sending keyframe snapshots to a Vision-Language Model for natural-language incident summaries.",
 ["Select keyframes on events.",
  "Send to VLM with prompt.",
  "Parse and store summaries.",
  "Attach to incident records.",
  "Review for accuracy."],
 "Natural-language incident summaries.", C)
add("vector-db-clip-search", "Vector DB CLIP Search",
 "Use when indexing frame embeddings in Qdrant/pgvector for natural-language video search.",
 ["Extract CLIP embeddings per frame.",
  "Store in vector DB.",
  "Implement similarity search.",
  "Return timestamps and thumbnails.",
  "Optimize indexing throughput."],
 "Semantic video search.", C)
add("slack-pagerduty-escalation", "Slack/PagerDuty Escalation",
 "Use when routing after-hours perimeter breaches to on-call security channels.",
 ["Define escalation policies.",
  "Integrate Slack/PagerDuty APIs.",
  "Route alerts by severity/time.",
  "Handle acknowledgements.",
  "Log incidents."],
 "After-hours escalation routing.", C)
add("solar-battery-camera-scheduler", "Solar Battery Camera Scheduler",
 "Use when dynamically adjusting frame rates and resolution based on edge battery telemetry.",
 ["Read battery telemetry.",
  "Adjust FPS/resolution thresholds.",
  "Schedule sleep/wake cycles.",
  "Protect critical events.",
  "Report battery trends."],
 "Battery-aware camera scheduling.", C)
add("multi-cam-reid-handoff", "Multi-Cam ReID Handoff",
 "Use when stitching movement timelines of the same person or vehicle across adjacent cameras.",
 ["Extract ReID embeddings.",
  "Match across camera views.",
  "Build global timelines.",
  "Handle handoff gaps.",
  "Visualize tracks."],
 "Cross-camera ReID timelines.", C)

# ============================================================ Part 2: Satellite/Geospatial
S = PILLAR_SAT
add("stac-api-query-builder", "STAC API Query Builder",
 "Use when querying SpatioTemporal Asset Catalogs (Sentinel, Landsat, Planet) by bounding box and cloud cover.",
 ["Define AOI and time range.",
  "Build STAC search request with filters.",
  "Paginate and collect items.",
  "Filter by cloud cover and bands.",
  "Export asset links."],
 "STAC query results and asset links.", S)
add("sentinel-hub-downloader", "Sentinel Hub Downloader",
 "Use when automating multi-band GeoTIFF downloads from Copernicus Data Space APIs.",
 ["Authenticate with Copernicus.",
  "Select collection and bands.",
  "Download GeoTIFFs with retry.",
  "Validate CRS and metadata.",
  "Store organized by tile/date."],
 "Downloaded Sentinel multi-band rasters.", S)
add("google-earth-engine-script", "Google Earth Engine Script",
 "Use when generating Python/JS GEE scripts for planetary-scale raster filtering and exports.",
 ["Define study area and collection.",
  "Filter and composite imagery.",
  "Apply spectral indices.",
  "Export to Drive/Cloud Storage.",
  "Document parameters."],
 "GEE processing script.", S)
add("cloud-optimized-geotiff-maker", "Cloud-Optimized GeoTIFF Maker",
 "Use when converting raw rasters into tiled, overview-enabled COGs using GDAL.",
 ["Inspect input raster.",
  "Build overviews with gdaladdo.",
  "Convert to COG with tiling.",
  "Validate with rio-cogeo.",
  "Upload to object storage."],
 "COG-ready raster files.", S)
add("band-stacking-compositor", "Band Stacking Compositor",
 "Use when merging individual spectral band files (Red, Green, Blue, NIR) into multi-band rasters.",
 ["List band files and order.",
  "Stack with rasterio/GDAL.",
  "Set band names and metadata.",
  "Validate dimensions/CRS.",
  "Write multi-band GeoTIFF."],
 "Multi-band composite raster.", S)
add("pansharpening-fusion", "Pansharpening Fusion",
 "Use when fusing high-resolution panchromatic bands with lower-resolution multispectral imagery.",
 ["Co-register PAN and MS.",
  "Choose fusion method (IHS/GS/Brovey).",
  "Fuse and restore colors.",
  "Evaluate spectral fidelity.",
  "Export sharpened product."],
 "Pansharpened imagery.", S)
add("scene-cloud-masking", "Scene Cloud Masking",
 "Use when applying QA60 or s2cloudless masks to remove clouds and cloud shadows from optical scenes.",
 ["Load QA band or run s2cloudless.",
  "Build cloud/shadow mask.",
  "Apply mask to scene.",
  "Interpolate or leave nodata.",
  "Validate mask quality."],
 "Cloud-masked satellite scene.", S)
add("mosaic-seamline-blender", "Mosaic Seamline Blender",
 "Use when stitching adjacent satellite tiles with histogram matching and feathering.",
 ["Co-register tiles.",
  "Compute seamlines avoiding features.",
  "Apply histogram matching.",
  "Blend with feathering.",
  "Validate seams."],
 "Seamless satellite mosaic.", S)
add("sar-sentinel1-preprocessor", "SAR Sentinel-1 Preprocessor",
 "Use when performing radiometric calibration, speckle filtering, and terrain correction on SAR data.",
 ["Apply orbit and calibration.",
  "Convert to backscatter (dB).",
  "Filter speckle.",
  "Terrain-correct with DEM.",
  "Export analysis-ready product."],
 "Analysis-ready SAR product.", S)
add("planetary-computer-auth", "Planetary Computer Auth",
 "Use when managing SAS token signing and lazy Xarray loading for Microsoft Planetary Computer datasets.",
 ["Configure authentication.",
  "Sign asset URLs with SAS tokens.",
  "Load via Xarray lazily.",
  "Handle token expiry.",
  "Document usage."],
 "Authenticated Planetary Computer access.", S)
add("ndvi-vegetation-health", "NDVI Vegetation Health",
 "Use when computing Normalized Difference Vegetation Index rasters and classifying crop vigor.",
 ["Compute (NIR-Red)/(NIR+Red).",
  "Handle nodata and scaling.",
  "Classify vigor thresholds.",
  "Visualize and export.",
  "Validate against ground truth."],
 "NDVI vegetation health raster.", S)
add("ndwi-surface-water-mapper", "NDWI Surface Water Mapper",
 "Use when extracting water bodies, reservoirs, and flood extents using green and NIR bands.",
 ["Compute (Green-NIR)/(Green+NIR).",
  "Threshold water pixels.",
  "Clean with morphology.",
  "Vectorize water bodies.",
  "Export water mask."],
 "Surface water extent map.", S)
add("nbr-wildfire-burn-severity", "NBR Wildfire Burn Severity",
 "Use when calculating Normalized Burn Ratio (pre- and post-fire) to map burn scars.",
 ["Compute NBR pre and post fire.",
  "Calculate dNBR.",
  "Classify burn severity.",
  "Map burn scars.",
  "Validate with field data."],
 "Burn severity map.", S)
add("ndbi-urban-sprawl-tracker", "NDBI Urban Sprawl Tracker",
 "Use when quantifying built-up impervious surfaces and urban expansion over multi-year intervals.",
 ["Compute NDBI per date.",
  "Threshold built-up areas.",
  "Compare multi-year extents.",
  "Quantify expansion.",
  "Visualize change."],
 "Urban sprawl change analysis.", S)
add("land-surface-temperature-lst", "Land Surface Temperature (LST)",
 "Use when deriving thermal heat-island maps from Landsat Thermal Infrared (TIRS) bands.",
 ["Convert TIRS to radiance.",
  "Compute brightness temperature.",
  "Apply emissivity correction.",
  "Derive LST.",
  "Map heat islands."],
 "Land surface temperature raster.", S)
add("chlorophyll-algal-bloom-detector", "Chlorophyll/Algal Bloom Detector",
 "Use when monitoring coastal and lake water quality using red-edge spectral ratios.",
 ["Compute chlorophyll indices.",
  "Threshold bloom areas.",
  "Track temporal changes.",
  "Validate with in-situ data.",
  "Export alerts."],
 "Algal bloom detection map.", S)
add("soil-moisture-sar-estimator", "Soil Moisture SAR Estimator",
 "Use when correlating C-band radar backscatter with topsoil moisture levels.",
 ["Calibrate SAR backscatter.",
  "Apply moisture retrieval model.",
  "Validate with ground sensors.",
  "Map soil moisture.",
  "Handle vegetation effects."],
 "Soil moisture estimates.", S)
add("change-detection-differencing", "Change Detection Differencing",
 "Use when computing pixel-wise temporal deltas to highlight deforestation or new construction.",
 ["Co-register images.",
  "Normalize radiometry.",
  "Compute difference metrics.",
  "Threshold change pixels.",
  "Classify change types."],
 "Change detection map.", S)
add("lulc-random-forest-classifier", "LULC Random Forest Classifier",
 "Use when training supervised land-use/land-cover models using scikit-learn and rasterio.",
 ["Prepare training samples.",
  "Extract spectral features.",
  "Train Random Forest.",
  "Predict full raster.",
  "Evaluate accuracy."],
 "Land-use/land-cover classification.", S)
add("building-footprint-segmenter", "Building Footprint Segmenter",
 "Use when running semantic segmentation (U-Net/SAM) on sub-meter imagery to extract building polygons.",
 ["Run segmentation model.",
  "Post-process masks.",
  "Vectorize footprints.",
  "Clean topology.",
  "Export GeoJSON."],
 "Building footprint polygons.", S)
add("ship-detection-sar-cfar", "Ship Detection SAR CFAR",
 "Use when implementing Constant False Alarm Rate algorithms to detect maritime vessels in radar imagery.",
 ["Estimate background statistics.",
  "Apply CFAR detector.",
  "Cluster detections.",
  "Filter land false positives.",
  "Export vessel positions."],
 "SAR ship detection results.", S)
add("dem-terrain-derivatives", "DEM Terrain Derivatives",
 "Use when generating slope, aspect, hillshade, and watershed accumulation layers from SRTM/Copernicus DEMs.",
 ["Load DEM.",
  "Compute slope/aspect/hillshade.",
  "Derive watersheds.",
  "Handle edge effects.",
  "Export derivatives."],
 "Terrain derivative layers.", S)
add("tle-celestrak-fetcher", "TLE CelesTrak Fetcher",
 "Use when pulling and caching fresh Two-Line Element sets from CelesTrak or Space-Track.org.",
 ["Fetch TLE from CelesTrak/Space-Track.",
  "Parse and validate TLE.",
  "Cache with timestamps.",
  "Handle rate limits.",
  "Provide lookup API."],
 "Cached TLE sets.", S)
add("sgp4-orbit-propagator", "SGP4 Orbit Propagator",
 "Use when computing satellite ECI/ECEF positions and ground tracks using Skyfield or sgp4.",
 ["Load TLE.",
  "Propagate with SGP4.",
  "Convert to ECI/ECEF.",
  "Generate ground track.",
  "Export positions."],
 "Satellite orbit positions.", S)
add("pass-prediction-scheduler", "Pass Prediction Scheduler",
 "Use when calculating upcoming AOS/LOS elevation windows for a given ground station lat/lon.",
 ["Set station coordinates.",
  "Propagate satellite orbit.",
  "Find AOS/LOS windows.",
  "Filter by min elevation.",
  "Schedule observations."],
 "Pass prediction schedule.", S)
add("doppler-shift-compensator", "Doppler Shift Compensator",
 "Use when computing real-time frequency offsets for UHF/S-band/X-band downlinks during passes.",
 ["Compute relative velocity.",
  "Calculate Doppler offset.",
  "Generate correction curve.",
  "Apply to SDR.",
  "Log compensation."],
 "Doppler correction profile.", S)
add("rotator-az-el-controller", "Rotator Az/El Controller",
 "Use when outputting rotctld/Hamlib commands to steer dish antennas across satellite passes.",
 ["Compute az/el over pass.",
  "Generate rotctld commands.",
  "Handle limits and backlash.",
  "Log tracking.",
  "Failsafe on errors."],
 "Antenna rotator control.", S)
add("link-budget-calculator", "Link Budget Calculator",
 "Use when modeling free-space path loss, Eb/N0, rain fade, and antenna gain for RF links.",
 ["Input TX/RX parameters.",
  "Compute FSPL and gains.",
  "Add rain fade and margins.",
  "Calculate Eb/N0.",
  "Report link feasibility."],
 "RF link budget report.", S)
add("noaa-meteor-apt-decoder", "NOAA/Meteor APT Decoder",
 "Use when automating SDR IQ recording and decoding of NOAA APT / Meteor LRPT weather images.",
 ["Record IQ samples.",
  "Decode APT/LRPT.",
  "Apply corrections.",
  "Save images.",
  "Schedule passes."],
 "Decoded weather satellite images.", S)
add("satnogs-observation-uploader", "SatNOGS Observation Uploader",
 "Use when formatting waterfall plots and demodulated frames for SatNOGS network submission.",
 ["Prepare observation metadata.",
  "Generate waterfall.",
  "Upload demod frames.",
  "Handle API auth.",
  "Log submissions."],
 "SatNOGS observation uploads.", S)
add("conjunction-debris-screener", "Conjunction Debris Screener",
 "Use when calculating closest-approach distances between active satellites and cataloged debris.",
 ["Load catalogs.",
  "Propagate both objects.",
  "Compute closest approach.",
  "Flag high-risk conjunctions.",
  "Report events."],
 "Conjunction screening report.", S)
add("solar-beta-angle-analyzer", "Solar Beta Angle Analyzer",
 "Use when modeling eclipse durations and solar array power generation across orbital seasons.",
 ["Compute beta angle.",
  "Model eclipse periods.",
  "Estimate solar power.",
  "Analyze seasonal trends.",
  "Report results."],
 "Solar beta angle analysis.", S)
add("postgis-spatial-query-writer", "PostGIS Spatial Query Writer",
 "Use when writing optimized ST_Intersects, ST_Buffer, and ST_DWithin SQL queries with GiST indexes.",
 ["Identify spatial predicate.",
  "Write optimized SQL.",
  "Add GiST indexes.",
  "Validate query plans.",
  "Document usage."],
 "Optimized PostGIS queries.", S)
add("crs-reprojection-pipeline", "CRS Reprojection Pipeline",
 "Use when safely transforming geometries and rasters between WGS84 (EPSG:4326) and local UTM zones.",
 ["Detect source CRS.",
  "Choose target CRS.",
  "Reproject with GDAL/Shapely.",
  "Validate accuracy.",
  "Handle edge cases."],
 "Reprojected geospatial data.", S)
add("geojson-topojson-optimizer", "GeoJSON/TopoJSON Optimizer",
 "Use when simplifying complex polygons with Shapely/Mapshaper while preserving topology.",
 ["Load geometries.",
  "Simplify with tolerance.",
  "Preserve topology.",
  "Validate outputs.",
  "Export optimized files."],
 "Optimized vector geometries.", S)
add("h3-hexagonal-grid-indexer", "H3 Hexagonal Grid Indexer",
 "Use when aggregating point and raster data into Uber H3 spatial hexagons for fast analytics.",
 ["Convert coordinates to H3.",
  "Aggregate data per hex.",
  "Build hex grid layers.",
  "Query and visualize.",
  "Export results."],
 "H3-aggregated spatial analytics.", S)
add("pmtiles-vector-tile-generator", "PMTiles Vector Tile Generator",
 "Use when building serverless cloud-hosted vector tilesets using Tippecanoe and PMTiles.",
 ["Prepare GeoJSON/MBTiles.",
  "Run Tippecanoe.",
  "Convert to PMTiles.",
  "Upload to storage.",
  "Serve and validate."],
 "Serverless vector tileset.", S)
add("geocoding-reverse-lookup-batch", "Geocoding Reverse Lookup Batch",
 "Use when batch-resolving coordinates to administrative boundaries using Nominatim or Pelias.",
 ["Prepare coordinate list.",
  "Query geocoder in batches.",
  "Handle rate limits.",
  "Parse admin boundaries.",
  "Export results."],
 "Batch reverse geocoding results.", S)
add("geoparquet-converter", "GeoParquet Converter",
 "Use when converting shapefiles and GeoJSONs into partitioned GeoParquet for DuckDB spatial queries.",
 ["Read source vectors.",
  "Convert to GeoParquet.",
  "Partition by region/time.",
  "Validate with DuckDB.",
  "Document schema."],
 "GeoParquet datasets.", S)
add("zonal-statistics-aggregator", "Zonal Statistics Aggregator",
 "Use when computing mean, median, and percentile raster values inside administrative polygons.",
 ["Load raster and zones.",
  "Compute zonal stats.",
  "Handle nodata.",
  "Export tables.",
  "Visualize results."],
 "Zonal statistics table.", S)
add("ais-adsb-track-correlator", "AIS/ADS-B Track Correlator",
 "Use when fusing satellite imagery detections with maritime AIS or aviation ADS-B transponder logs.",
 ["Load detection and track data.",
  "Match by time/location.",
  "Resolve identities.",
  "Build fused tracks.",
  "Report correlations."],
 "Fused AIS/ADS-B tracks.", S)
add("maplibre-gl-layer-builder", "MapLibre GL Layer Builder",
 "Use when scaffolding interactive web maps with custom raster tile layers and vector styling.",
 ["Set up MapLibre map.",
  "Add raster/vector layers.",
  "Style and interactivity.",
  "Add controls.",
  "Test performance."],
 "Interactive web map.", S)
add("titiler-dynamic-tile-server", "TiTiler Dynamic Tile Server",
 "Use when deploying a FastAPI + TiTiler server to render COGs on the fly with custom colormaps.",
 ["Install TiTiler.",
  "Configure COG endpoints.",
  "Add colormaps.",
  "Deploy FastAPI.",
  "Test tile serving."],
 "Dynamic tile server.", S)
add("cesiumjs-3d-globe-viewer", "CesiumJS 3D Globe Viewer",
 "Use when visualizing 3D satellite orbits, sensor swath cones, and terrain meshes in CesiumJS.",
 ["Set up Cesium viewer.",
  "Add terrain and imagery.",
  "Render orbits/swaths.",
  "Add interactions.",
  "Optimize rendering."],
 "3D globe visualization.", S)
add("kepler-deckgl-time-slider", "Kepler.gl/deck.gl Time Slider",
 "Use when building GPU-accelerated spatio-temporal visualizations for vessel or vehicle trajectories.",
 ["Prepare trajectory data.",
  "Configure deck.gl layers.",
  "Add time slider.",
  "Optimize rendering.",
  "Export/share."],
 "Spatio-temporal visualization.", S)
add("false-color-band-visualizer", "False Color Band Visualizer",
 "Use when rendering NIR-Red-Green or SWIR composites to highlight vegetation and burn scars.",
 ["Select bands.",
  "Normalize and composite.",
  "Apply colormaps.",
  "Visualize results.",
  "Export images."],
 "False-color composites.", S)
add("split-screen-swipe-comparator", "Split-Screen Swipe Comparator",
 "Use when creating before/after map sliders for disaster response and urban growth reviews.",
 ["Prepare before/after layers.",
  "Implement swipe slider.",
  "Sync maps.",
  "Add labels.",
  "Test usability."],
 "Before/after map comparator.", S)
add("qgis-pyqgis-batch-styler", "QGIS PyQGIS Batch Styler",
 "Use when automating map layout exports and symbology rules via headless PyQGIS scripts.",
 ["Set up headless QGIS.",
  "Apply symbology.",
  "Generate layouts.",
  "Export maps.",
  "Batch process."],
 "Automated QGIS map exports.", S)
add("folium-jupyter-quickmap", "Folium Jupyter Quickmap",
 "Use when generating lightweight interactive HTML maps directly inside data science notebooks.",
 ["Create Folium map.",
  "Add layers/markers.",
  "Display in notebook.",
  "Export HTML.",
  "Share results."],
 "Interactive notebook maps.", S)
add("geotiff-legend-colorbar-gen", "GeoTIFF Legend Colorbar Gen",
 "Use when rendering publication-ready scale bars, north arrows, and colormaps for raster exports.",
 ["Define colormap and range.",
  "Render colorbar.",
  "Add scale bar/north arrow.",
  "Compose final figure.",
  "Export high-DPI."],
 "Publication-ready raster figures.", S)


TEMPLATE = """---
name: {name}
description: {desc}
---

# {name}

{pillar}

{desc}

## Workflow

{workflow}

## Output

{output}
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ids = set()
    for s in SKILLS:
        if s["id"] in ids:
            raise SystemExit(f"duplicate id: {s['id']}")
        ids.add(s["id"])
        d = OUT / s["id"]
        d.mkdir(parents=True, exist_ok=True)
        workflow = "\n".join(f"{n}. {step}" for n, step in enumerate(s["steps"], 1))
        body = TEMPLATE.format(name=s["name"], desc=s["desc"],
                               pillar=s["pillar"], workflow=workflow,
                               output=s["output"])
        (d / "SKILL.md").write_text(body, encoding="utf-8")
    print(f"wrote {len(SKILLS)} skills to {OUT}")
    assert len(SKILLS) == 100, len(SKILLS)


if __name__ == "__main__":
    main()
    # second pass safety write
    written = 0
    for s in SKILLS:
        target = OUT / s["id"] / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        steps = "\n".join(f"{i}. {step}" for i, step in enumerate(s["steps"], 1))
        content = (
            "---\n"
            f"name: {s['name']}\n"
            f"description: {s['desc']}\n"
            "---\n\n"
            f"# {s['name']}\n\n"
            f"{s['pillar']}\n\n"
            f"{s['desc']}\n\n"
            "## Workflow\n\n"
            f"{steps}\n\n"
            "## Output\n\n"
            f"{s['output']}\n"
        )
        target.write_text(content, encoding="utf-8")
        written += 1
    print(f"Wrote {written} CCTV/satellite skills to {OUT}")