// artifact-aware-deblocking.glsl
// Step 1-4: Smooth 8x8 macroblock boundaries on heavily compressed
// municipal H.264 streams while preserving true edges.
// 1. Detect macroblock boundaries (8x8 grid).
// 2. Apply deblocking (boundary-aware low-pass).
// 3. Preserve edges (reduce strength on high gradients).
// 4. Validate (clamp, no NaN/black frames).

precision highp float;

uniform sampler2D u_colorTex;
uniform vec2 u_resolution;     // texture size in pixels
uniform float u_strength;       // deblock strength 0..1 (default 0.6)
uniform float u_edgeThreshold;  // edge preservation threshold (default 0.12)

varying vec2 v_uv;

float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

void main() {
    vec2 px = v_uv * u_resolution;
    vec2 inBlock = mod(px, 8.0);
    // distance (in px) to nearest 8x8 macroblock boundary
    vec2 distToBoundary = min(inBlock, 8.0 - inBlock);
    float dist = min(distToBoundary.x, distToBoundary.y);
    // highest weight exactly on the boundary, decaying over ~2 px
    float nearBoundary = 1.0 - smoothstep(0.0, 2.0, dist);

    vec2 texel = 1.0 / u_resolution;
    vec3 c     = texture2D(u_colorTex, v_uv).rgb;
    vec3 left  = texture2D(u_colorTex, v_uv - vec2(texel.x, 0.0)).rgb;
    vec3 right = texture2D(u_colorTex, v_uv + vec2(texel.x, 0.0)).rgb;
    vec3 up    = texture2D(u_colorTex, v_uv - vec2(0.0, texel.y)).rgb;
    vec3 down  = texture2D(u_colorTex, v_uv + vec2(0.0, texel.y)).rgb;

    // Step 3: edge strength -> preserve true edges
    float gx = abs(luma(right) - luma(left));
    float gy = abs(luma(down)  - luma(up));
    float edge = max(gx, gy);
    float preserve = smoothstep(u_edgeThreshold * 0.5, u_edgeThreshold, edge);

    // Step 2: deblock only near boundaries and on flat (artifact) regions
    float w = nearBoundary * u_strength * (1.0 - preserve);

    // boundary-aware average across the 8x8 grid line
    vec3 avg = (left + right + up + down + c) * 0.2;
    vec3 outc = mix(c, avg, w);

    // Step 4: validation - clamp, guard NaN/Inf
    outc = clamp(outc, 0.0, 1.0);
    if (any(isnan(outc)) || any(isinf(outc))) outc = c;

    gl_FragColor = vec4(outc, 1.0);
}