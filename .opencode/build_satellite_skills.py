#!/usr/bin/env python3
"""Generate the 100 satellite image-clarity skills into .opencode/skills/.

Each skill follows the Bhajanlal library convention:
  - YAML frontmatter with name + description (the trigger surface)
  - "Part of the Bhajanlal ... Pillar: ..." line parsed by serve/skills.py
  - Workflow (how to actually apply the technique) + Output sections

Run:  python3 .opencode/build_satellite_skills.py
"""
from pathlib import Path

PILLAR = ("Part of the **Bhajanlal** model-building skill library. "
          "Pillar: 103. Satellite & Aerial Remote-Sensing Imaging (100 skills)")
OUT = Path(__file__).resolve().parent / "skills"

SKILLS = [
    # -------------------------------------------------- 1. Super-Resolution
    {
        "id": "satellite-single-image-super-resolution",
        "name": "Single-Image Super-Resolution (SISR)",
        "desc": "Use when upscaling low-resolution satellite tiles with deep convolutional or transformer networks to recover sub-pixel road and pedestrian detail.",
        "steps": [
            "Confirm the source GSD and pick an integer scale (2x/4x) whose training degradation matches the sensor.",
            "Run tiled inference with overlap so large scenes stay inside GPU memory.",
            "Prefer transformer SISR (SwinIR/HAT class) when road geometry and tiny figures must stay crisp.",
            "Inspect upscaled crops at 100% for hallucinated texture before accepting the result.",
        ],
        "output": "Sharper satellite tiles at 2x-4x scale with recovered sub-pixel detail.",
    },
    {
        "id": "satellite-multi-frame-super-resolution",
        "name": "Multi-Frame Super-Resolution (MFSR)",
        "desc": "Use when fusing multiple slightly shifted satellite passes of the same road to recover sub-pixel detail beyond a single frame GSD.",
        "steps": [
            "Register the frame stack to sub-pixel accuracy first (see satellite-subpixel-shift-registration).",
            "Estimate each frame relative shift and weight frames by sharpness and cloud cover.",
            "Fuse into a high-resolution grid with robust averaging that rejects outlier frames.",
            "Mask or ghost-check moving objects so cars and pedestrians are not doubled.",
        ],
        "output": "One super-resolved frame built from a burst of shifted low-res captures.",
    },
    {
        "id": "satellite-diffusion-rs-super-resolution",
        "name": "Diffusion-Based Remote Sensing SR",
        "desc": "Use when latent diffusion models must synthesize realistic high-frequency texture in satellite imagery without hallucinating fake objects.",
        "steps": [
            "Condition the diffusion SR on the low-res tile with a mild (2x) noise schedule.",
            "Keep guidance strength low so priors add texture, not invented objects.",
            "Compare output structure against the input - any new road marking or figure is a red flag.",
            "Use the deterministic DDIM sampler so results are reproducible across runs.",
        ],
        "output": "Texturally rich upscale with structure locked to the input pixels.",
    },
    {
        "id": "satellite-swinir-hat-upscaling",
        "name": "SwinIR & HAT Transformer Upscaling",
        "desc": "Use when applying Hybrid Attention or Swin transformer upscalers that capture long-range road geometry while sharpening tiny targets.",
        "steps": [
            "Choose the classical or lightweight SwinIR variant to match available VRAM.",
            "Feed patches large enough (64x64+) so attention sees whole road segments.",
            "Run overlapping-window inference to avoid seam artifacts between patches.",
            "Confirm lane lines and silhouettes stay continuous across patch borders.",
        ],
        "output": "Transformer-upscaled tiles with coherent long-range structure.",
    },
    {
        "id": "satellite-realesrgan-bsrgan-degradation",
        "name": "Real-ESRGAN & BSRGAN Degradation Modeling",
        "desc": "Use when training or fine-tuning SR networks on realistic sensor blur, compression, and atmospheric noise instead of simple bicubic downsampling.",
        "steps": [
            "Build a degradation pipeline - blur (realistic PSF), noise (shot/read), JPEG or JPEG2000, downsample.",
            "Match degradation parameters to the target satellite known noise and compression characteristics.",
            "Train with perceptual plus GAN loss (Real-ESRGAN) or residual learning (BSRGAN).",
            "Validate on real held-out tiles, never on synthetic bicubic pairs alone.",
        ],
        "output": "SR model robust to real satellite degradation rather than bicubic only.",
    },
    {
        "id": "satellite-subpixel-shift-registration",
        "name": "Sub-Pixel Shift Estimation (Sub-Pixel Registration)",
        "desc": "Use when aligning sequential burst frames to within 0.05-pixel accuracy before multi-frame fusion.",
        "steps": [
            "Estimate the coarse shift with phase correlation on overlapping regions.",
            "Refine with sub-pixel interpolation of the correlation peak (parabolic fit).",
            "Reject frames whose shift error exceeds the threshold or that are cloud-covered.",
            "Verify residuals on static road features after alignment.",
        ],
        "output": "Frame stack aligned to about 0.05 px, ready for fusion.",
    },
    {
        "id": "satellite-pansharpening",
        "name": "Pansharpening (Brovey, Gram-Schmidt, IHS)",
        "desc": "Use when merging high-resolution panchromatic bands with lower-resolution multispectral color bands to sharpen satellite road imagery.",
        "steps": [
            "Resample the multispectral bands to the panchromatic grid and match histograms.",
            "Pick the injection method - IHS for visual sharpness, Gram-Schmidt for radiometric fidelity, Brovey for quick previews.",
            "Fuse, then restore original color statistics to prevent hue shifts.",
            "Check narrow road features and crosswalks for spectral distortion at 100% zoom.",
        ],
        "output": "Color-preserving imagery at panchromatic resolution with sharp road detail.",
    },
    {
        "id": "satellite-deep-pansharpening",
        "name": "Deep Residual Pansharpening (PanNet / FusionNet)",
        "desc": "Use when deep pansharpening networks must preserve sharp narrow road features while retaining true color radiometry.",
        "steps": [
            "Train or apply the network in the reduced-resolution setting to respect Wald protocol.",
            "Feed both PAN and MS bands and let the network inject spatial detail into the MS product.",
            "Check spectral fidelity with Q2n and ERGAS metrics, not just visual sharpness.",
            "Fall back to classical Gram-Schmidt if the network shifts color on vegetation or asphalt.",
        ],
        "output": "Pan-sharpened output with joint spatial-spectral fidelity.",
    },
    {
        "id": "satellite-inr-liif-zoom",
        "name": "Implicit Neural Representations (INR / LIIF)",
        "desc": "Use when implicit neural representations query continuous coordinates to zoom smoothly into pedestrian-scale regions without pixelation.",
        "steps": [
            "Train the INR on the target tile or load a pretrained LIIF model.",
            "Query at arbitrary output resolution - for example 6-8x for a person-sized crop.",
            "Limit zoom to where the model stays faithful; beyond about 4x flag the crop as uncertain.",
            "Render a coordinate grid overlay to document the zoom factor used.",
        ],
        "output": "Continuously queryable image function for arbitrary-zoom crops.",
    },
    {
        "id": "satellite-edge-guided-super-resolution",
        "name": "Edge-Guided Super-Resolution",
        "desc": "Use when extracting high-frequency gradient maps first so super-resolution does not blur road curbs and human silhouettes.",
        "steps": [
            "Compute gradient maps (Sobel or Canny) from the input tile.",
            "Use them as an extra guidance channel or as an edge loss in the SR network.",
            "After upscaling, blend a detail layer back along the extracted edges.",
            "Verify silhouettes remain sharp against the asphalt background.",
        ],
        "output": "Upscale with preserved edge structure on curbs and silhouettes.",
    },
    {
        "id": "satellite-wavelet-super-resolution",
        "name": "Wavelet-Domain Super-Resolution",
        "desc": "Use when reconstructing high-frequency sub-bands separately in the discrete wavelet domain to recover detail in satellite tiles.",
        "steps": [
            "Decompose the low-res tile into wavelet sub-bands with a 2-level DWT.",
            "Predict or interpolate the high-frequency sub-bands with a small network.",
            "Reconstruct with inverse DWT and check for ringing along lane lines.",
            "Blend with a spatial-domain SR result if artifacts appear.",
        ],
        "output": "Detail-restored tile via wavelet sub-band reconstruction.",
    },
    {
        "id": "satellite-focal-frequency-loss",
        "name": "Frequency-Aware Loss Optimization (Focal Frequency Loss)",
        "desc": "Use when forcing a restoration network to prioritize high-frequency spatial details over flat asphalt backgrounds during training.",
        "steps": [
            "Add a focal frequency loss term that weights hard-to-reconstruct frequencies.",
            "Balance its weight against pixel loss so sensor noise is not amplified.",
            "Monitor the frequency-domain residual during training for convergence.",
            "Validate that road markings gain sharpness without checkerboard artifacts.",
        ],
        "output": "Model that optimizes perceptually important high frequencies.",
    },
    {
        "id": "satellite-zssr-internal-learning",
        "name": "Zero-Shot Internal Learning (ZSSR)",
        "desc": "Use when adapting super-resolution weights on the fly from recurring patches within a single satellite scene with no external data.",
        "steps": [
            "Extract self-similar low-res/high-res patch pairs from the scene itself.",
            "Fine-tune a small SR network for a few hundred iterations on those pairs.",
            "Apply the scene-specific model to the target region.",
            "Stop early if validation on held-out internal pairs degrades.",
        ],
        "output": "Scene-adapted SR model trained with zero external data.",
    },
    {
        "id": "satellite-video-super-resolution",
        "name": "Video Satellite Super-Resolution (VSR)",
        "desc": "Use when exploiting temporal continuity across full-motion satellite video to resolve moving pedestrians frame to frame.",
        "steps": [
            "Align frames with motion compensation or optical flow first.",
            "Fuse information across a temporal window of 3-9 frames into the target frame.",
            "Mask moving objects from naive averaging to prevent ghosting.",
            "Evaluate on tracked targets - identity must stay stable across frames.",
        ],
        "output": "Temporally consistent super-resolved video frames.",
    },
    {
        "id": "satellite-cross-sensor-domain-adaptation",
        "name": "Cross-Sensor Domain Adaptation",
        "desc": "Use when transferring sharpness priors from aerial drone imagery at 5 cm to orbital satellite imagery at 30 cm.",
        "steps": [
            "Collect paired or unpaired drone/satellite scenes of the same area types.",
            "Adapt with domain-adversarial training or style transfer that preserves geometry.",
            "Validate that the adapted model does not invent drone-only detail.",
            "Keep radiometry consistent so downstream detection still works.",
        ],
        "output": "SR model whose priors transfer from drone to satellite imagery.",
    },
    # ---------------------------------------- 2. Deblurring & PSF Restoration
    {
        "id": "satellite-psf-deconvolution",
        "name": "Sensor PSF Estimation & Deconvolution",
        "desc": "Use when modeling the optical diffraction and detector blur kernel of a satellite telescope to restore sharp edges.",
        "steps": [
            "Obtain or estimate the sensor PSF from MTF calibration or point sources.",
            "Apply regularized deconvolution (Wiener or Richardson-Lucy) with that PSF.",
            "Tune regularization so noise on asphalt is not amplified.",
            "Validate edge sharpness against a known slanted-edge target such as a crosswalk.",
        ],
        "output": "Deconvolved tile with diffraction-limited sharpness.",
    },
    {
        "id": "satellite-blind-motion-deblurring",
        "name": "Blind Motion Deblurring",
        "desc": "Use when removing directional smear caused by spacecraft orbital velocity at 7.5 km/s and Time Delay Integration jitter.",
        "steps": [
            "Estimate the blur kernel direction and length from strong edges via gradient statistics.",
            "Apply a blind deconvolution or a motion-blur-trained restoration network.",
            "Re-estimate the kernel once after the first pass if edges still smear.",
            "Check lane lines and vehicle outlines for residual streaking.",
        ],
        "output": "Image with orbital motion smear removed.",
    },
    {
        "id": "satellite-richardson-lucy-deconvolution",
        "name": "Richardson-Lucy Iterative Deconvolution",
        "desc": "Use when restoring sharp edges on high-contrast targets using Poisson noise statistics via iterative Richardson-Lucy deconvolution.",
        "steps": [
            "Start from the PSF estimate and run 10-30 RL iterations.",
            "Stop when noise begins to blossom in flat road regions.",
            "Add a mild total-variation penalty or use early stopping as regularization.",
            "Compare before/after on pedestrian silhouettes for over-sharpening halos.",
        ],
        "output": "Poisson-aware deconvolution with crisp high-contrast edges.",
    },
    {
        "id": "satellite-wiener-filtering",
        "name": "Wiener Filtering",
        "desc": "Use when suppressing optical blur in the Fourier domain while bounding noise amplification with a Wiener filter.",
        "steps": [
            "Estimate the OTF from the PSF and the noise-to-signal power ratio.",
            "Apply the Wiener filter in the frequency domain.",
            "Clip the filter gain to avoid noise blow-up in dark areas.",
            "Verify no periodic artifacts from FFT tiling.",
        ],
        "output": "Blur-suppressed image with controlled noise.",
    },
    {
        "id": "satellite-spatially-varying-deblur",
        "name": "Non-Uniform / Spatially Varying Deblurring",
        "desc": "Use when correcting off-nadir perspective distortion and lens aberrations that blur differently across wide swath edges.",
        "steps": [
            "Model the PSF as a spatially varying field by tiling the scene into PSF zones.",
            "Apply per-tile deconvolution with overlap blending.",
            "Correct residual geometric warp from the same field.",
            "Check that sharpness is uniform from scene center to edge.",
        ],
        "output": "Uniformly sharp wide-swath image.",
    },
    {
        "id": "satellite-restormer-nafnet-restoration",
        "name": "Restormer & NAFNet Restoration",
        "desc": "Use when nonlinear activation-free networks remove complex atmospheric and motion blur simultaneously from satellite imagery.",
        "steps": [
            "Select the pretrained checkpoint sized for the expected degradation mix.",
            "Feed the raw tile and use tiled inference with padding for large scenes.",
            "If retraining, mix blur, haze, and noise degradations in one dataset.",
            "Validate with both PSNR and visual checks on tiny targets.",
        ],
        "output": "One-pass restoration covering blur, haze, and noise.",
    },
    {
        "id": "satellite-jitter-attitude-compensation",
        "name": "Jitter & Attitude Distortion Compensation",
        "desc": "Use when correcting micro-vibration ripples using onboard star-tracker and gyroscope telemetry.",
        "steps": [
            "Pull per-frame attitude telemetry covering the exposure window.",
            "Convert attitude deltas into a per-row or per-pixel displacement map.",
            "Warp the image to cancel the ripple, then apply mild sharpening.",
            "Verify straight road edges are actually straight after correction.",
        ],
        "output": "Jitter-free image corrected from spacecraft telemetry.",
    },
    {
        "id": "satellite-atmospheric-turbulence-mitigation",
        "name": "Atmospheric Turbulence Mitigation",
        "desc": "Use when removing heat-haze shimmer rising off sun-baked asphalt roads.",
        "steps": [
            "Estimate turbulence strength from frame sequences or single-image priors.",
            "Apply a turbulence restoration network or multi-frame lucky selection.",
            "For single images, use a physics-guided dehaze plus deblur cascade.",
            "Confirm distant road features stop shimmering.",
        ],
        "output": "Image with atmospheric shimmer suppressed.",
    },
    {
        "id": "satellite-lucky-imaging-stacking",
        "name": "Lucky Imaging Frame Selection",
        "desc": "Use when selecting and stacking the sharpest micro-exposures from burst captures.",
        "steps": [
            "Score each frame sharpness with variance of Laplacian or an MTF estimate.",
            "Keep the top fraction of frames and align them.",
            "Median-combine the aligned stack to reject noise and outliers.",
            "Use the combined frame as input to SR or detection.",
        ],
        "output": "Low-noise, sharp stack composite.",
    },
    {
        "id": "satellite-defocus-aberration-correction",
        "name": "Defocus Aberration Correction",
        "desc": "Use when compensating for thermal expansion shifts in orbital mirror focal lengths.",
        "steps": [
            "Estimate defocus from the edge spread function or a phase-retrieval method.",
            "Apply inverse filtering or a defocus-trained restoration network.",
            "If focus drifts over the pass, correct in tiles with per-tile estimates.",
            "Re-measure MTF after correction to confirm improvement.",
        ],
        "output": "In-focus imagery despite thermal focus drift.",
    },
    {
        "id": "satellite-tv-regularized-deconvolution",
        "name": "Total Variation (TV) Regularized Deconvolution",
        "desc": "Use when sharpening object boundaries while keeping smooth road surfaces flat via total-variation regularized deconvolution.",
        "steps": [
            "Solve the deconvolution with a TV penalty (Chambolle or primal-dual solver).",
            "Sweep the TV weight - too high staircases asphalt, too low leaves noise.",
            "Preserve radiometry so the TV term does not shift reflectance values.",
            "Inspect pedestrian silhouettes for blocky edges.",
        ],
        "output": "Sharp boundaries with flat, noise-free road surfaces.",
    },
    {
        "id": "satellite-dark-channel-deblurring",
        "name": "Dark Channel Prior Deblurring",
        "desc": "Use when exploiting dark shadow pixels cast by pedestrians to estimate exact blur kernels.",
        "steps": [
            "Detect dark-channel pixels (shadows, dark clothing) as blur references.",
            "Estimate the kernel from those high-contrast dark regions.",
            "Apply non-blind deconvolution with the estimated kernel.",
            "Cross-check the kernel against the sensor known PSF bounds.",
        ],
        "output": "Kernel estimated from scene shadows, applied for deblur.",
    },
    {
        "id": "satellite-subpixel-phase-correlation",
        "name": "Sub-Pixel Phase Correlation",
        "desc": "Use when measuring and reversing fractional-pixel drift between Time Delay Integration sensor stages.",
        "steps": [
            "Compute phase correlation between adjacent stage outputs.",
            "Interpolate the peak for sub-pixel drift estimates.",
            "Shift and align each stage contribution to remove the drift.",
            "Verify residual drift is near zero after correction.",
        ],
        "output": "TDI stages aligned with fractional drift removed.",
    },
    # ---------------------------- 3. Radiometric, Atmospheric & Shadow
    {
        "id": "satellite-dark-object-subtraction-haze",
        "name": "Atmospheric Scattering & Haze Removal (Dark Object Subtraction)",
        "desc": "Use when stripping Rayleigh and Mie scattering veils that wash out low-contrast road targets.",
        "steps": [
            "Find the darkest object in the scene (water, deep shadow) and assume it should be near zero.",
            "Subtract that per-band offset from the whole image to remove the scattering veil.",
            "Re-scale to the original dynamic range so radiometry stays comparable across passes.",
            "Check that contrast on asphalt and silhouettes improved without crushing shadows.",
        ],
        "output": "Haze-stripped imagery with restored low-contrast detail.",
    },
    {
        "id": "satellite-6s-modtran-radiative-transfer",
        "name": "6S & MODTRAN Radiative Transfer Correction",
        "desc": "Use when converting raw Digital Numbers (DN) into true surface reflectance with radiative transfer models.",
        "steps": [
            "Gather acquisition metadata - solar angles, sensor, altitude, aerosol type.",
            "Run 6S or MODTRAN to get the atmosphere transfer coefficients for the pass.",
            "Apply the TOA reflectance equation and the atmospheric correction coefficients.",
            "Validate against ground control reflectance panels or known land-cover spectra.",
        ],
        "output": "Atmospherically corrected surface reflectance product.",
    },
    {
        "id": "satellite-dehazeformer-physics-dehazing",
        "name": "DehazeFormer & Physics-Guided Dehazing",
        "desc": "Use when clearing thin cirrus clouds and urban smog over road networks.",
        "steps": [
            "Estimate the transmission map with a physics haze model or DehazeFormer network.",
            "Recover the scene radiance with the atmospheric scattering model.",
            "Refine transmission edges so building and tree boundaries do not halo.",
            "Leave opaque cloud pixels masked rather than hallucinating content beneath them.",
        ],
        "output": "Dehazed scene with roads and figures visible through thin haze.",
    },
    {
        "id": "satellite-shadow-detection-compensation",
        "name": "Shadow Detection & Radiometric Compensation",
        "desc": "Use when brightening pedestrians inside building or tree shadows without blowing out sunlit asphalt.",
        "steps": [
            "Build a shadow mask from chromaticity, brightness, and NIR ratios.",
            "Estimate the illumination ratio between shadowed and sunlit regions per band.",
            "Brighten shadowed pixels by that ratio while preserving their texture.",
            "Clamp highlights so sunlit road areas keep their original radiometry.",
        ],
        "output": "Shadow-balanced image where figures stay visible in shade.",
    },
    {
        "id": "satellite-sun-glint-suppression",
        "name": "Sun-Glint & Specular Reflection Suppression",
        "desc": "Use when eliminating blinding reflections off car windshields and wet pavement that saturate nearby pixels.",
        "steps": [
            "Flag saturated or near-saturated specular pixels using NIR polarization or intensity thresholds.",
            "Estimate the glint component and subtract it per band.",
            "Inpaint flagged pixels from surrounding texture or from a second pass.",
            "Verify figures near glint regions are no longer masked by bloom.",
        ],
        "output": "Glint-suppressed imagery with recovered detail around reflections.",
    },
    {
        "id": "satellite-dynamic-range-tone-mapping",
        "name": "Dynamic Range Compression & Tone Mapping",
        "desc": "Use when mapping 11-bit/12-bit/16-bit raw satellite radiometry into 8-bit displays without crushing dark tones.",
        "steps": [
            "Normalize raw DN to a float reflectance or radiance range first.",
            "Apply a global curve (gamma or Reinhard) tuned so asphalt mid-tones stay separated.",
            "Use local tone mapping only when global compression loses tiny dark targets.",
            "Record the transform so results remain radiometrically reproducible.",
        ],
        "output": "Display-ready 8-bit imagery with preserved dark detail.",
    },
    {
        "id": "satellite-clahe-micro-contrast",
        "name": "CLAHE (Contrast Limited Adaptive Histogram Equalization)",
        "desc": "Use when enhancing local micro-contrast on uniform gray roads so tiny figures stand out.",
        "steps": [
            "Tile the image and equalize each tile histogram with a clip limit.",
            "Interpolate between tiles to avoid block seams.",
            "Apply on the luminance channel only to prevent color shifts.",
            "Lower the clip limit if noise on flat asphalt is amplified.",
        ],
        "output": "Locally contrast-enhanced image where small targets pop.",
    },
    {
        "id": "satellite-retinex-illumination-decomposition",
        "name": "Retinex Illumination-Reflectance Decomposition",
        "desc": "Use when separating uneven lighting conditions from true object surface albedo.",
        "steps": [
            "Estimate the illumination field with a large-scale Gaussian or Retinex network.",
            "Divide (or log-subtract) illumination to recover reflectance.",
            "Re-composite with a softened illumination so the result does not look flat.",
            "Check that clothing and skin tones stay distinguishable from asphalt.",
        ],
        "output": "Reflectance image free of uneven illumination gradients.",
    },
    {
        "id": "satellite-brdf-normalization",
        "name": "BRDF (Bidirectional Reflectance Distribution Function) Normalization",
        "desc": "Use when correcting brightness changes caused by off-nadir viewing angles.",
        "steps": [
            "Record per-pixel view and solar geometry for the acquisition.",
            "Apply a kernel-driven BRDF model to normalize to a fixed reference geometry.",
            "Mask pixels where the geometry is too extreme for stable normalization.",
            "Confirm multi-date tiles now share comparable brightness.",
        ],
        "output": "Angularly normalized imagery comparable across view angles.",
    },
    {
        "id": "satellite-destriping-flat-field",
        "name": "Destriping & Flat-Field Calibration",
        "desc": "Use when eliminating vertical push-broom sensor banding across CCD/CMOS detector arrays.",
        "steps": [
            "Estimate per-detector gain and offset from flat-field or scene statistics.",
            "Apply the correction column-wise to flatten detector response.",
            "For residual stripes, use a low-rank or Fourier notch destriping pass.",
            "Verify no horizontal features were attenuated along the road.",
        ],
        "output": "Stripe-free image with uniform detector response.",
    },
    {
        "id": "satellite-bad-pixel-cosmic-ray-removal",
        "name": "Bad-Pixel & Cosmic-Ray Spike Removal",
        "desc": "Use when interpolating dead detector pixels or radiation hits that mimic tiny white dots on roads.",
        "steps": [
            "Detect outliers with a median filter residual and a saturation check.",
            "Distinguish cosmic rays (sharp single pixels) from real small targets by PSF width.",
            "Replace flagged pixels with a local median or inpainting interpolation.",
            "Re-run detection to confirm no real target was removed.",
        ],
        "output": "Clean image without false point targets.",
    },
    {
        "id": "satellite-nighttime-low-light-enhancement",
        "name": "Nighttime Low-Light Enhancement (LLIE)",
        "desc": "Use when boosting signal-to-noise ratio under streetlamps using zero-reference deep curves.",
        "steps": [
            "Estimate the illumination curve without a reference (zero-reference deep LLIE).",
            "Enhance brightness while suppressing the noise it reveals.",
            "Preserve color so sodium streetlight casts do not skew band ratios.",
            "Check that dark road edges and figures remain resolvable.",
        ],
        "output": "Night scene with usable contrast and controlled noise.",
    },
    {
        "id": "satellite-true-false-color-synthesis",
        "name": "True-Color & False-Color Band Synthesis",
        "desc": "Use when combining Red-Edge and Near-Infrared (NIR) bands to separate organic skin/clothing from mineral asphalt.",
        "steps": [
            "Pick the band combination for the goal - NIR false color for vegetation/skin, red-edge for stress.",
            "Normalize each band before compositing to avoid channel dominance.",
            "Render as RGB and check class separability on labeled crops.",
            "Document the band mapping so results are interpretable.",
        ],
        "output": "Band composite that separates targets from asphalt background.",
    },
    {
        "id": "satellite-homomorphic-filtering",
        "name": "Homomorphic Filtering",
        "desc": "Use when simultaneously normalizing uneven road illumination and boosting high-frequency edge contrast.",
        "steps": [
            "Take the log of the image to separate illumination and reflectance multiplicatively.",
            "Apply a high-pass filter in the frequency domain to attenuate low-frequency lighting.",
            "Exponentiate back and clamp to the valid range.",
            "Confirm shadows were flattened without ringing along curbs.",
        ],
        "output": "Evenly lit image with boosted edge contrast.",
    },
    # -------------------------------- 4. Denoising & Compression Artifacts
    {
        "id": "satellite-raw-shot-read-noise-denoising",
        "name": "Raw Sensor Shot & Read Noise Modeling",
        "desc": "Use when denoising linear raw imagery before demosaicing or gamma compression destroys faint signals.",
        "steps": [
            "Model shot noise as Poisson (signal-dependent) and read noise as Gaussian.",
            "Fit noise parameters from flat frames or per-pixel variance sweeps.",
            "Denoise in linear space with a noise-aware loss or filter.",
            "Only then apply demosaicing, gamma, and resampling.",
        ],
        "output": "Clean linear raw data with faint signals preserved.",
    },
    {
        "id": "satellite-bm33-block-matching-denoising",
        "name": "BM3D (Block-Matching and 3D Filtering)",
        "desc": "Use when grouping similar road patches to strip Gaussian noise while preserving isolated tiny targets.",
        "steps": [
            "Group similar 2D patches into 3D stacks via block matching.",
            "Collaboratively filter in the transform domain and aggregate back.",
            "Tune patch size and group size so single-pixel targets are not matched away.",
            "Inspect tiny figures after filtering for erasure.",
        ],
        "output": "Denoised image with fine targets intact.",
    },
    {
        "id": "satellite-non-local-means-denoising",
        "name": "Non-Local Means (NLM) Denoising",
        "desc": "Use when averaging repetitive pavement textures without smearing non-repeating pedestrian pixels.",
        "steps": [
            "Search a large window for patches similar to each reference patch.",
            "Weight similar patches by exponential similarity of their neighborhoods.",
            "Use a search window large enough to find true matches in uniform asphalt.",
            "Verify non-repeating silhouettes are not blurred by wrong matches.",
        ],
        "output": "Noise reduced with texture and unique targets preserved.",
    },
    {
        "id": "satellite-noise2void-self-supervised",
        "name": "Noise2Void / Self-Supervised Denoising",
        "desc": "Use when training denoisers directly on noisy orbital imagery without clean ground truth.",
        "steps": [
            "Hide the center pixel of each patch so the network cannot copy noise.",
            "Train to predict the hidden pixel from its blind-spot context.",
            "Validate with SURE or noisy-to-noisy consistency, not PSNR against clean data.",
            "Confirm real structures were not smoothed out of existence.",
        ],
        "output": "Self-supervised denoiser trained on noisy-only data.",
    },
    {
        "id": "satellite-jpeg2000-ccsds-artifact-removal",
        "name": "JPEG2000 & CCSDS Downlink Artifact Removal",
        "desc": "Use when eliminating ringing and blocking artifacts caused by onboard satellite data compression.",
        "steps": [
            "Identify compression parameters (quality, wavelet levels) from headers if available.",
            "Apply artifact suppression with a compression-artifact-trained network.",
            "Deblock block boundaries and dering around high-contrast road markings.",
            "Compare against an uncompressed reference strip when one exists.",
        ],
        "output": "Image restored from downlink compression artifacts.",
    },
    {
        "id": "satellite-demosaicing-artifact-suppression",
        "name": "Demosaicing Artifact Suppression",
        "desc": "Use when preventing zippering and false-color moire patterns on high-frequency road markings.",
        "steps": [
            "Detect moire and zipper artifacts with high-frequency color residual analysis.",
            "Re-demosaic with an adaptive or learning-based demosaicer.",
            "Apply a targeted color-aliasing removal pass if artifacts remain.",
            "Check lane lines and crosswalks for false color fringes.",
        ],
        "output": "Artifact-free color image without zippering or moire.",
    },
    {
        "id": "satellite-anscombe-variance-stabilization",
        "name": "Poisson-Gaussian Variance Stabilization (Anscombe Transform)",
        "desc": "Use when converting signal-dependent photon noise into uniform additive noise for standard denoisers.",
        "steps": [
            "Apply the generalized Anscombe transform to the raw counts.",
            "Run the denoiser in the stabilized domain where noise is approximately Gaussian.",
            "Apply the exact unbiased inverse transform to return to counts.",
            "Confirm brightness is unbiased after the round trip.",
        ],
        "output": "Denoised data with photon noise handled correctly.",
    },
    {
        "id": "satellite-scunet-blind-denoising",
        "name": "Swin-Conv-UNet (SCUNet) Blind Denoising",
        "desc": "Use when handling mixed sensor noise levels across varying illumination zones.",
        "steps": [
            "Feed the image to a blind-denoising network without specifying the noise level.",
            "Tile large scenes with overlap and blend tile borders.",
            "Let the model adapt to per-region noise differences (sunlit vs shadow).",
            "Check that texture on asphalt was not over-smoothed.",
        ],
        "output": "Uniformly denoised scene despite mixed noise levels.",
    },
    {
        "id": "satellite-temporal-video-denoising",
        "name": "Temporal Denoising for Video Satellites",
        "desc": "Use when filtering frame-to-frame sensor grain while locking onto moving objects.",
        "steps": [
            "Align frames with motion compensation before temporal filtering.",
            "Weight a temporal window by photometric and geometric similarity.",
            "Exclude pixels where motion indicates a real moving target.",
            "Confirm moving pedestrians stay sharp while static noise averages out.",
        ],
        "output": "Temporally denoised frames with moving targets intact.",
    },
    {
        "id": "satellite-adaptive-median-impulse-filter",
        "name": "Impulse & Salt-and-Pepper Median Filtering (Adaptive)",
        "desc": "Use when removing transmission bit-errors without eroding 1-pixel targets.",
        "steps": [
            "Detect impulse pixels by comparing to the local median and variance.",
            "Replace only flagged pixels, leaving all others untouched.",
            "Use an adaptive window size so small real targets survive.",
            "Verify no isolated real point targets were classified as noise.",
        ],
        "output": "Image with bit-error impulses removed, targets preserved.",
    },
    {
        "id": "satellite-bilateral-gradient-preserving",
        "name": "Gradient-Preserving Bilateral Filtering",
        "steps": [
            "Filter with range weights so pixels across strong edges are not averaged.",
            "Keep the spatial sigma small enough to retain silhouette boundaries.",
            "Apply on flat road regions to suppress sensor grain.",
            "Check pedestrian edges stay crisp after smoothing.",
        ],
        "desc": "Use when smoothing flat asphalt noise while respecting sharp luminance jumps.",
        "output": "Smoothed noise with gradients and edges preserved.",
    },
    {
        "id": "satellite-spectral-spatial-total-variation",
        "name": "Spectral-Spatial Total Variation Denoising",
        "desc": "Use when exploiting correlations across RGB and NIR bands to isolate true physical objects from noise.",
        "steps": [
            "Jointly denoise all bands with a shared spatial gradient map.",
            "Add a spectral consistency term so band ratios stay physically valid.",
            "Sweep the TV weight against small-target retention.",
            "Confirm NIR vegetation and skin signatures remain intact.",
        ],
        "output": "Jointly denoised bands with spectral relationships preserved.",
    },
    {
        "id": "satellite-aliasing-moire-removal",
        "name": "Aliasing & Moire Pattern Removal",
        "desc": "Use when suppressing Nyquist aliasing artifacts along dashed lane lines and crosswalks.",
        "steps": [
            "Identify aliasing as periodic energy near the Nyquist frequency.",
            "Apply an anti-aliasing notch filter or re-sample above Nyquist when possible.",
            "For color moire, desaturate only the aliased high-frequency color channel.",
            "Verify lane dash geometry looks continuous, not scalloped.",
        ],
        "output": "Anti-aliased image without moire on periodic road features.",
    },
    # ------------------------- 5. Geometric Orthorectification & 3D Context
    {
        "id": "satellite-rpc-orthorectification",
        "name": "Rational Polynomial Coefficient (RPC) Orthorectification",
        "desc": "Use when removing terrain tilt and camera perspective distortion so roads align true to scale.",
        "steps": [
            "Load the RPCs supplied with the image and a coarse DEM.",
            "Resample to a uniform ground grid using the RPC forward model.",
            "Refine RPCs with ground control points if bias remains.",
            "Check road widths match their true map dimensions.",
        ],
        "output": "Orthorectified image geometrically true to the ground grid.",
    },
    {
        "id": "satellite-dsm-true-ortho",
        "name": "Digital Surface Model (DSM) True-Ortho Projection",
        "desc": "Use when eliminating building lean so tall structures do not occlude adjacent sidewalks and roads.",
        "steps": [
            "Build or load a DSM covering the scene.",
            "Reproject each pixel using its DSM height to remove occlusions.",
            "Fill occluded areas from other passes or inpainting.",
            "Confirm sidewalks next to buildings are visible and not hidden.",
        ],
        "output": "True-ortho image with building lean removed.",
    },
    {
        "id": "satellite-mvs-3d-reconstruction",
        "name": "Multi-View Stereo (MVS) 3D Reconstruction",
        "desc": "Use when rebuilding sub-meter elevation profiles from stereo satellite pairs to detect vertical relief.",
        "steps": [
            "Rectify the stereo pair and match features across views.",
            "Compute a dense depth or point cloud with an MVS method.",
            "Filter depth by photometric consistency and DEM sanity checks.",
            "Use the elevation output to identify objects standing above the road plane.",
        ],
        "output": "Sub-meter 3D reconstruction of the road scene.",
    },
    {
        "id": "satellite-shadow-length-height-estimation",
        "name": "Shadow-Length Height Estimation",
        "desc": "Use when calculating the exact height of a tiny road object from sun azimuth, elevation angle, and cast shadow length.",
        "steps": [
            "Get sun elevation and azimuth for the acquisition timestamp.",
            "Measure the cast shadow length from the object base to its tip.",
            "Compute height = shadow length x tan(sun elevation), correcting for slope.",
            "Sanity-check against known object heights (poles, cars, people).",
        ],
        "output": "Estimated object heights from sun geometry and shadows.",
    },
    {
        "id": "satellite-vector-road-co-registration",
        "name": "Sub-Pixel Co-Registration with Vector Road Maps",
        "desc": "Use when aligning OpenStreetMap/HD road vectors to pinpoint exact lanes and crosswalks.",
        "steps": [
            "Extract road centerlines from the image and from the vector map.",
            "Align them with sub-pixel registration using mutual information.",
            "Apply a smooth warp field, not a global shift alone.",
            "Report residual alignment error per segment.",
        ],
        "output": "Image registered to road vectors at sub-pixel accuracy.",
    },
    {
        "id": "satellite-off-nadir-compensation",
        "name": "Off-Nadir Angle Compensation",
        "desc": "Use when correcting foreshortening distortion when a satellite captures a road at a 20-35 degree slant angle.",
        "steps": [
            "Read the off-nadir angle and look direction from the metadata.",
            "Project the image to nadir using the RPC model and DEM.",
            "Resample with a PSF-aware kernel to avoid extra blur.",
            "Confirm road widths and lengths are restored to true scale.",
        ],
        "output": "Nadir-equivalent view with foreshortening removed.",
    },
    {
        "id": "satellite-dem-slope-correction",
        "name": "DEM-Guided Terrain Slope Correction",
        "desc": "Use when accounting for steep road inclines that warp pixel ground footprint dimensions.",
        "steps": [
            "Compute local slope from the DEM at each pixel.",
            "Adjust the effective pixel footprint for the slope-induced scale change.",
            "Resample to a constant ground-resolution grid.",
            "Verify gradient roads no longer appear compressed or stretched.",
        ],
        "output": "Slope-corrected imagery with uniform ground sampling.",
    },
    {
        "id": "satellite-gcp-bundle-adjustment",
        "name": "Geo-Referencing & Ground Control Point (GCP) Bundle Adjustment",
        "desc": "Use when locking image coordinates to sub-decimeter geographic accuracy.",
        "steps": [
            "Collect well-spread GCPs with known coordinates.",
            "Run bundle adjustment to solve camera and ground parameters jointly.",
            "Check residuals - reject outliers and re-solve.",
            "Report RMSE in the horizontal and vertical directions.",
        ],
        "output": "Geo-referenced image with sub-decimeter positional accuracy.",
    },
    {
        "id": "satellite-mosaic-seamline-blending",
        "name": "Image Mosaicking & Seamline Blending",
        "desc": "Use when merging adjacent satellite strips seamlessly without cutting across moving road targets.",
        "steps": [
            "Co-register strips to sub-pixel accuracy before mosaicking.",
            "Choose seamlines that avoid roads and dynamic objects where possible.",
            "Blend across seams with radiometric normalization and feathering.",
            "Check seams never split a vehicle or pedestrian across two tones.",
        ],
        "output": "Seamless radiometrically consistent mosaic.",
    },
    {
        "id": "satellite-perspective-homography-rectification",
        "name": "Perspective & Homography Rectification",
        "desc": "Use when warping oblique aerial/satellite views into top-down nadir geometry.",
        "steps": [
            "Identify four or more correspondences on the ground plane.",
            "Solve the homography and warp with a high-quality resampler.",
            "Mask areas outside the valid warped footprint.",
            "Verify straight roads remain straight after the warp.",
        ],
        "output": "Rectified top-down view of oblique imagery.",
    },
    {
        "id": "satellite-epipolar-rectification",
        "name": "Epipolar Geometry Alignment",
        "desc": "Use when rectifying stereo pairs so parallax shifts directly reveal tiny objects standing above the road plane.",
        "steps": [
            "Estimate the fundamental matrix from stereo correspondences.",
            "Rectify both images so epipolar lines are horizontal.",
            "Compute disparity and convert to height above the road plane.",
            "Flag objects whose disparity indicates vertical relief.",
        ],
        "output": "Rectified stereo pair with clean vertical parallax.",
    },
    {
        "id": "satellite-road-centerline-mask-extraction",
        "name": "Road Centerline & Mask Extraction",
        "desc": "Use when isolating road surfaces to constrain search areas and eliminate background clutter.",
        "steps": [
            "Segment road surface with a semantic model or spectral rule set.",
            "Extract centerlines and lane boundaries from the mask.",
            "Grow or shrink the mask to include curbs and sidewalks.",
            "Use the mask to bound detection and change-analysis regions.",
        ],
        "output": "Road mask and centerlines constraining downstream analysis.",
    },
    {
        "id": "satellite-temporal-change-detection",
        "name": "Temporal Change Detection (Background Subtraction)",
        "desc": "Use when comparing a current pass against a clear historical reference of the exact same road to isolate newly appeared pedestrians.",
        "steps": [
            "Co-register the current and reference images to sub-pixel accuracy.",
            "Normalize radiometry so illumination differences do not read as change.",
            "Compute a change mask with a threshold tuned on known-static regions.",
            "Classify compact change blobs above the road plane as candidate targets.",
        ],
        "output": "Change mask isolating newly appeared objects on the road.",
    },
    # ------------- 6. Tiny-Object & Pedestrian Detection in Remote Sensing
    {
        "id": "satellite-sahi-tiled-inference",
        "name": "SAHI (Slicing Aided Hyper Inference)",
        "desc": "Use when splitting massive gigapixel satellite scenes into overlapping high-res patches so tiny targets are not downscaled away.",
        "steps": [
            "Slice the scene into overlapping patches sized for the detector input.",
            "Run inference on each patch at full resolution.",
            "Merge predictions across slices with non-maximum suppression.",
            "Confirm a person-sized target is not lost between slice borders.",
        ],
        "output": "Detections over the full scene without resolution loss.",
    },
    {
        "id": "satellite-oriented-bbox-detection",
        "name": "Oriented Bounding Box (OBB) Detection",
        "desc": "Use when predicting rotated bounding boxes aligned with road direction and shadow orientation.",
        "steps": [
            "Annotate or fit rotated boxes (angle + dimensions) for targets.",
            "Train an OBB detector with rotated IoU or KLD loss.",
            "Rotate boxes to road heading for consistent downstream reporting.",
            "Check long thin silhouettes are tightly enclosed, not axis-aligned and bloated.",
        ],
        "output": "Rotated detections aligned with target and road orientation.",
    },
    {
        "id": "satellite-nwd-loss-tiny-targets",
        "name": "Normalized Wasserstein Distance (NWD) Loss",
        "desc": "Use when replacing IoU loss, which fails on 2x2 pixel targets, with distribution-based similarity metrics.",
        "steps": [
            "Represent each box as a 2D Gaussian distribution.",
            "Compute NWD between prediction and ground-truth distributions.",
            "Use NWD as the classification-matching or regression loss for tiny boxes.",
            "Compare recall on sub-10-pixel targets against IoU-trained baseline.",
        ],
        "output": "Detector trained with a loss that stays stable at tiny scales.",
    },
    {
        "id": "satellite-fpn-bifpn-feature-pyramid",
        "name": "Feature Pyramid Networks (FPN / PANet / BiFPN)",
        "desc": "Use when fusing shallow, high-resolution P2 feature layers where single-pixel spatial details still survive.",
        "steps": [
            "Enable a P2 output level so tiny targets are not downsampled away.",
            "Fuse top-down and bottom-up paths (BiFPN for weighted fusion).",
            "Attach detection heads at P2 and P3 for scale coverage.",
            "Check that single-pixel candidates still activate at P2.",
        ],
        "output": "Multi-scale features retaining tiny-target signal.",
    },
    {
        "id": "satellite-shadow-target-pairing-context",
        "name": "Context-Aware Shadow-Target Pairing",
        "desc": "Use when training detectors to recognize a pedestrian and their elongated cast shadow as a single joint signature.",
        "steps": [
            "Annotate the target together with its cast shadow as one region.",
            "Add shadow-context features or a shadow channel as detector input.",
            "Balance training so shadowless targets (overcast) still detect.",
            "Verify paired detections merge target and shadow into one box.",
        ],
        "output": "Detector using joint target-shadow signatures for recall.",
    },
    {
        "id": "satellite-deformable-convolution-detection",
        "name": "Deformable Convolutional Networks (DCN)",
        "desc": "Use when adapting receptive fields to elongated human silhouettes and irregular cast shadows.",
        "steps": [
            "Replace fixed-kernel convolutions with offset-learned deformable ones.",
            "Train on varied silhouette poses and shadow shapes.",
            "Inspect learned offsets to confirm they follow target geometry.",
            "Fall back to standard convs if offsets become unstable on small data.",
        ],
        "output": "Detector whose receptive fields conform to target shapes.",
    },
    {
        "id": "satellite-dino-rtdetr-query-detection",
        "name": "Query-Based Tiny Object Detection (DINO / RT-DETR)",
        "desc": "Use when transformer cross-attention must locate sub-10-pixel targets without anchor-box mismatches.",
        "steps": [
            "Set up a query-based detector with multi-scale feature attention.",
            "Tune the number of queries to cover expected target density.",
            "Train with denoising queries to stabilize small-box learning.",
            "Check borderline 3-5 pixel targets against anchor-based baseline recall.",
        ],
        "output": "Anchor-free detections of sub-10-pixel targets.",
    },
    {
        "id": "satellite-joint-sr-detection",
        "name": "Super-Resolution Assisted Detection (Joint SR + Detection)",
        "desc": "Use when backpropagating object detection loss directly into the super-resolution generator.",
        "steps": [
            "Chain the SR generator into the detector as one network.",
            "Backpropagate detection loss through the SR stage.",
            "Add a fidelity term so SR cannot invent target-like texture.",
            "Compare end-to-end mAP against detect-on-raw and SR-then-detect pipelines.",
        ],
        "output": "Joint model where SR is optimized for detection recall.",
    },
    {
        "id": "satellite-test-time-augmentation-multiscale",
        "name": "Multi-Scale Test-Time Augmentation (TTA)",
        "desc": "Use when running inference across rotated and zoomed crops to boost recall on borderline-visible figures.",
        "steps": [
            "Generate rotated and scaled variants of each crop.",
            "Run the detector on every variant.",
            "Merge results with weighted box fusion.",
            "Keep the variant set small enough that latency stays acceptable.",
        ],
        "output": "Higher-recall detections from multi-view aggregation.",
    },
    {
        "id": "satellite-focal-loss-hard-negative-mining",
        "name": "Focal Loss & Hard Negative Mining",
        "desc": "Use when suppressing false positives from manhole covers, fire hydrants, road markings, and trash bins.",
        "steps": [
            "Apply focal loss to down-weight easy background examples.",
            "Mine hard negatives - confident false positives - and add them to training.",
            "Keep a curated hard-negative set of road furniture lookalikes.",
            "Track false-positive rate per category across training rounds.",
        ],
        "output": "Detector with fewer road-furniture false alarms.",
    },
    {
        "id": "satellite-motion-assisted-detection",
        "name": "Motion-Assisted Detection (Optical Flow / Frame Differencing)",
        "desc": "Use when detecting 1-2 pixel moving entities across sequential video satellite frames by velocity vectors.",
        "steps": [
            "Estimate optical flow or frame differences on co-registered frames.",
            "Cluster motion pixels into candidate moving objects.",
            "Filter by velocity range consistent with road traffic and pedestrians.",
            "Confirm detections track consistently across at least 3 frames.",
        ],
        "output": "Motion-based candidate list of tiny moving targets.",
    },
    {
        "id": "satellite-context-prior-road-filtering",
        "name": "Context Prior Filtering (Road/Sidewalk Constraints)",
        "desc": "Use when weighting detection confidence higher along crosswalks, bus stops, and sidewalks.",
        "steps": [
            "Load road, sidewalk, and crosswalk masks from vector data.",
            "Boost or gate detector scores inside high-probability zones.",
            "Suppress detections in impossible zones (building roofs, water).",
            "Report which prior changed each accepted detection.",
        ],
        "output": "Context-gated detections concentrated on walkable areas.",
    },
    {
        "id": "satellite-georsclip-remoteclip-zero-shot",
        "name": "Zero-Shot / Open-Vocabulary Remote Sensing (GeoRSCLIP / RemoteCLIP)",
        "desc": "Use when querying ultra-high-res crops using vision-language models fine-tuned on overhead imagery.",
        "steps": [
            "Crop the region of interest at native resolution.",
            "Encode the crop and text prompts with the remote-sensing VLM.",
            "Rank by similarity and threshold on a validated cut-off.",
            "Escalate borderline scores to human review rather than auto-accept.",
        ],
        "output": "Open-vocabulary semantic hits on high-res crops.",
    },
    {
        "id": "satellite-subpixel-centroid-localization",
        "name": "Sub-Pixel Centroid Localization",
        "desc": "Use when computing intensity-weighted centers of mass to track pedestrian positions with sub-pixel precision.",
        "steps": [
            "Isolate the target blob from the local background.",
            "Compute the intensity-weighted centroid within a small window.",
            "Correct for background bias with a local mean subtraction.",
            "Report coordinates with a stated sub-pixel uncertainty.",
        ],
        "output": "Sub-pixel target coordinates with uncertainty.",
    },
    {
        "id": "satellite-bytestrack-strongsort-overhead-tracking",
        "name": "Multi-Object Tracking (ByteTrack / StrongSORT for Overhead Video)",
        "desc": "Use when linking faint detections across frames to maintain identity even when a target briefly fades into noise.",
        "steps": [
            "Run per-frame detection and compute motion-constant predictions.",
            "Associate by IoU plus appearance or motion features across gaps.",
            "Keep low-confidence detections in a second association stage (ByteTrack).",
            "Report identity switches and track fragmentation rates.",
        ],
        "output": "Stable tracks with persistent IDs across frames.",
    },
    {
        "id": "satellite-density-map-counting",
        "name": "Density-Map Counting (CSRNet / DM-Count)",
        "desc": "Use when estimating pedestrian presence and crowd density on busy roads even when individual limbs cannot be resolved.",
        "steps": [
            "Generate density maps by convolving point annotations with Gaussian kernels.",
            "Train a regression network to predict the density map from the crop.",
            "Integrate the map to get counts and threshold for presence detection.",
            "Validate count error against manual tallies on held-out scenes.",
        ],
        "output": "Crowd density maps and counts for unresolved targets.",
    },
    # ------------------ 7. Multi-Modal, Spectral & Next-Gen Sensor Fusion
    {
        "id": "satellite-vnir-swir-spectral-fusion",
        "name": "VNIR + SWIR Spectral Fusion",
        "desc": "Use when Short-Wave Infrared (1.2-2.5 um) must penetrate smoke/haze and distinguish synthetic fabrics from asphalt.",
        "steps": [
            "Co-register VNIR and SWIR bands to a common grid.",
            "Fuse with a pansharpening-style injection or a learned fusion network.",
            "Use SWIR absorption features to separate fabric from mineral surfaces.",
            "Check fusion did not distort diagnostic spectral features.",
        ],
        "output": "Fused VNIR-SWIR product with haze-penetrating material contrast.",
    },
    {
        "id": "satellite-thermal-lwir-anomaly-fusion",
        "name": "Thermal Infrared (LWIR) Anomaly Fusion",
        "desc": "Use when pairing thermal contrast with optical imagery to spot warm human signatures against cool pavement.",
        "steps": [
            "Co-register thermal and optical bands geometrically.",
            "Detect thermal anomalies against local pavement temperature statistics.",
            "Fuse thermal anomaly maps with optical detections as an extra channel.",
            "Validate against time-of-day thermal drift (night vs noon).",
        ],
        "output": "Fused thermal-optical detection of warm human signatures.",
    },
    {
        "id": "satellite-sar-optical-cross-modal",
        "name": "SAR-Optical Cross-Modal Translation",
        "desc": "Use when fusing Synthetic Aperture Radar backscatter with optical tiles during partial cloud cover.",
        "steps": [
            "Geometrically align SAR and optical acquisitions.",
            "Translate SAR to optical appearance or fuse features with a cross-modal network.",
            "Mask remaining cloud and use SAR-only confidence where optical is unusable.",
            "Check specular road surfaces and target scattering behave as expected.",
        ],
        "output": "All-weather fused product covering cloudy acquisitions.",
    },
    {
        "id": "satellite-lidar-depth-super-resolution",
        "name": "LiDAR-Guided Depth Super-Resolution",
        "desc": "Use when airborne LiDAR point clouds serve as geometric priors to sharpen orbital imagery.",
        "steps": [
            "Interpolate sparse LiDAR points into a dense depth map.",
            "Condition the SR or restoration network on that depth map.",
            "Let depth edges guide upscaling so structures stay crisp.",
            "Verify depth-conditioned output against held-out LiDAR points.",
        ],
        "output": "Depth-guided sharp imagery with correct geometry.",
    },
    {
        "id": "satellite-hyperspectral-unmixing-subpixel",
        "name": "Hyperspectral Unmixing (Sub-Pixel Target Detection)",
        "desc": "Use when decomposing a single mixed pixel's spectrum to detect fractional presence of human clothing/skin materials.",
        "steps": [
            "Extract endmembers for asphalt, skin, common fabrics, and background.",
            "Solve linear or non-linear unmixing to get fractional abundances.",
            "Flag pixels where a target endmember exceeds an abundance threshold.",
            "Validate fractions against known-material reference spectra.",
        ],
        "output": "Sub-pixel material abundance maps flagging human presence.",
    },
    {
        "id": "satellite-matched-filter-ace",
        "name": "Matched Filtering & ACE (Adaptive Cosine Estimator)",
        "desc": "Use when detecting sub-pixel spectral anomalies against local asphalt background statistics.",
        "steps": [
            "Estimate the background mean and covariance from the local region.",
            "Project each pixel spectrum onto the target signature (matched filter) or compute ACE.",
            "Normalize so the statistic has a constant false-alarm rate.",
            "Threshold at a validated CFAR level and cluster the hits.",
        ],
        "output": "CFAR-controlled anomaly hits for sub-pixel targets.",
    },
    {
        "id": "satellite-polarimetric-filtering",
        "name": "Polarimetric Filtering",
        "desc": "Use when filtering polarized sunlight reflected off flat asphalt to reveal non-flat vertical objects.",
        "steps": [
            "Acquire or synthesize polarization channels (Stokes parameters).",
            "Suppress the strongly polarized specular road component.",
            "Keep depolarized returns that indicate vertical structures.",
            "Feed the filtered contrast into detection as an additional cue.",
        ],
        "output": "Polarization-filtered contrast isolating upright objects.",
    },
    {
        "id": "satellite-multi-constellation-temporal-fusion",
        "name": "Multi-Constellation Temporal Fusion",
        "desc": "Use when combining morning, midday, and afternoon passes from different constellations to capture optimal sun-shadow angles.",
        "steps": [
            "Co-register passes from each constellation to a common grid.",
            "Normalize radiometry across sensors and illumination conditions.",
            "Fuse temporally, keeping the pass with the best sun-shadow geometry per region.",
            "Preserve per-pass provenance so results stay auditable.",
        ],
        "output": "Fused multi-pass product with optimal shadow geometry.",
    },
    {
        "id": "satellite-3d-gaussian-nerf-multiview",
        "name": "3D Gaussian Splatting / NeRF for Satellite Multi-View",
        "desc": "Use when reconstructing photorealistic, arbitrary-angle 3D road scenes from multiple orbital captures.",
        "steps": [
            "Collect multi-view captures with known or estimated camera poses.",
            "Train a 3D Gaussian or NeRF reconstruction of the scene.",
            "Render novel viewpoints to disambiguate occluded road areas.",
            "Flag hallucinated regions that lack multi-view support.",
        ],
        "output": "Arbitrary-angle renders of the road scene from multi-view data.",
    },
    {
        "id": "satellite-event-neuromorphic-processing",
        "name": "Event-Based / Neuromorphic Sensor Processing",
        "desc": "Use when high-temporal-resolution change detection is needed for future orbital motion tracking.",
        "steps": [
            "Stream event-train data as sparse brightness-change events.",
            "Accumulate events into short frames or voxel grids.",
            "Cluster events by velocity to segment moving objects.",
            "Fuse event-based detections with conventional frame detections.",
        ],
        "output": "High-temporal-resolution motion detections from event data.",
    },
    # --------------------- 8. Evaluation, Deployment & Edge-Case Rigor
    {
        "id": "satellite-no-reference-iqa",
        "name": "No-Reference Image Quality Assessment (NIQE / BRISQUE / MUSIQ)",
        "desc": "Use when automatically scoring sharpness and clarity when no ground-truth image exists.",
        "steps": [
            "Run NIQE/BRISQUE for natural-scene quality or MUSIQ for learned quality.",
            "Score per-tile and map the worst regions for review.",
            "Track scores across pipeline versions as a regression gate.",
            "Correlate scores with human clarity ratings before trusting them.",
        ],
        "output": "Per-image clarity scores ranking results without ground truth.",
    },
    {
        "id": "satellite-mtf-edge-spread",
        "name": "Modulation Transfer Function (MTF) & Edge Spread Measurement",
        "desc": "Use when measuring true spatial sharpness using painted road crosswalks as natural slanted-edge targets.",
        "steps": [
            "Locate a slanted high-contrast edge (crosswalk stripe, curb line).",
            "Extract the edge spread function and differentiate to the line spread function.",
            "FFT to get the MTF curve and read MTF50.",
            "Compare MTF50 across passes and processing versions.",
        ],
        "output": "MTF curve quantifying true spatial sharpness.",
    },
    {
        "id": "satellite-hallucination-uncertainty",
        "name": "Hallucination Detection & Uncertainty Quantification",
        "desc": "Use when flagging pixels generated purely by AI priors versus grounded in physical sensor photons.",
        "steps": [
            "Keep a provenance mask through every generative step (SR, diffusion, inpainting).",
            "Estimate per-pixel uncertainty with ensembles or diffusion variance.",
            "Flag any detection resting mostly on generated pixels.",
            "Require photon-grounded evidence before accepting a forensic claim.",
        ],
        "output": "Provenance and uncertainty maps separating real from generated detail.",
    },
    {
        "id": "satellite-tiled-streaming-gdal",
        "name": "Tiled Streaming & Memory-Efficient Inference (GDAL / Rasterio)",
        "desc": "Use when processing multi-gigabyte GeoTIFF scenes without losing geospatial metadata or CRS projections.",
        "steps": [
            "Open the raster with windowed reads instead of loading it whole.",
            "Process in tiles sized to memory with overlap for seamless blending.",
            "Write output with the source CRS, transform, and nodata preserved.",
            "Validate the output opens correctly in a GIS viewer.",
        ],
        "output": "Processed huge rasters with geospatial metadata intact.",
    },
    {
        "id": "satellite-adversarial-weather-robustness",
        "name": "Adversarial & Weather-Robustness Testing",
        "desc": "Use when benchmarking clarity pipelines across rain-slicked roads, snow glare, and dusk lighting.",
        "steps": [
            "Assemble a test set spanning rain, snow, glare, dusk, and haze.",
            "Run the full pipeline on each condition and score with IQA and detection metrics.",
            "Compare against a clear-weather baseline to find condition-specific gaps.",
            "Add failing conditions to the training or tuning loop.",
        ],
        "output": "Robustness report per weather and lighting condition.",
    },
    {
        "id": "satellite-human-in-the-loop-forensics",
        "name": "Human-in-the-Loop Forensic Verification Workflows",
        "desc": "Use when presenting side-by-side raw, sharpened, and temporal-reference crops to prevent false identification.",
        "steps": [
            "Assemble a triptych per candidate - raw, enhanced, and independent reference.",
            "Annotate which pixels are sensor-grounded versus AI-generated.",
            "Require an analyst to confirm identity with a stated confidence level.",
            "Log every decision with the evidence shown for later audit.",
        ],
        "output": "Auditable human-verified identification with full evidence trail.",
    },
]

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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ids = set()
    for i, s in enumerate(SKILLS, 1):
        if s["id"] in ids:
            raise SystemExit(f"duplicate id: {s['id']}")
        ids.add(s["id"])
        workflow = "\n".join(f"{n}. {step}" for n, step in enumerate(s["steps"], 1))
        body = TEMPLATE.format(
            name=s["name"], desc=s["desc"], pillar=PILLAR,
            workflow=workflow, output=s["output"])
        d = OUT / s["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(body, encoding="utf-8")
    print(f"wrote {len(SKILLS)} skills to {OUT}")
    if len(SKILLS) != 100:
        raise SystemExit(f"expected 100 skills, got {len(SKILLS)}")


if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------
# Write each skill to disk in OpenCode SKILL.md format.
OUT.mkdir(parents=True, exist_ok=True)
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
        f"{PILLAR}\n\n"
        f"{s['desc']}\n\n"
        "## Workflow\n\n"
        f"{steps}\n\n"
        "## Output\n\n"
        f"{s['output']}\n"
    )
    target.write_text(content, encoding="utf-8")
    written += 1
print(f"Wrote {written} satellite skills to {OUT}")
