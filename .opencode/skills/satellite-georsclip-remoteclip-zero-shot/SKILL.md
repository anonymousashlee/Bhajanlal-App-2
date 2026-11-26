---
name: Zero-Shot / Open-Vocabulary Remote Sensing (GeoRSCLIP / RemoteCLIP)
description: Use when querying ultra-high-res crops using vision-language models fine-tuned on overhead imagery.
---

# Zero-Shot / Open-Vocabulary Remote Sensing (GeoRSCLIP / RemoteCLIP)

Part of the **Bhajanlal** model-building skill library. Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)

Use when querying ultra-high-res crops using vision-language models fine-tuned on overhead imagery.

## Workflow

1. Crop the region of interest at native resolution.
2. Encode the crop and text prompts with the remote-sensing VLM.
3. Rank by similarity and threshold on a validated cut-off.
4. Escalate borderline scores to human review rather than auto-accept.

## Output

Open-vocabulary semantic hits on high-res crops.
