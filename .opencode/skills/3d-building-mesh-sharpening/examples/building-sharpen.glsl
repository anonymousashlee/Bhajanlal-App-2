// building-sharpen.glsl
// Step 1-4: Sharpen extruded OSM / photorealistic building meshes
// by recomputing smooth normals, tuning edge lighting, avoiding
// over-brightening, and adding a crispness validation pass.

precision highp float;

uniform sampler2D u_colorTex;
uniform vec3 u_lightDir;        // normalized directional light
uniform float u_ambient;        // keep low to preserve edges (0.15-0.25)
uniform float u_specular;       // subtle specular for crisp edges
uniform float u_shininess;      // 32-64 for buildings
uniform float u_overBrightCap;  // clamp to avoid blown highlights (0.85)

varying vec3 v_normal;
varying vec3 v_viewDir;
varying vec2 v_uv;

void main() {
    vec3 N = normalize(v_normal);
    vec3 L = normalize(u_lightDir);
    vec3 V = normalize(v_viewDir);
    vec3 H = normalize(L + V);

    // Step 1: smooth normals already recomputed on CPU; re-normalize here.
    float NdotL = max(dot(N, L), 0.0);

    // Step 2: edge definition via diffuse + rim + specular.
    float rim = pow(1.0 - max(dot(N, V), 0.0), 3.0) * 0.25;
    float spec = pow(max(dot(N, H), 0.0), u_shininess) * u_specular;

    // Step 3: avoid over-brightening - clamp combined luminance.
    float lum = u_ambient + (1.0 - u_ambient) * NdotL + rim + spec;
    lum = min(lum, u_overBrightCap);

    vec3 base = texture2D(u_colorTex, v_uv).rgb;
    vec3 color = base * lum;

    // Step 4: crispness validation - boost micro-contrast on edges only.
    float edge = smoothstep(0.3, 0.6, NdotL) * (1.0 - smoothstep(0.6, 0.9, NdotL));
    color = mix(color, color * 1.08, edge * 0.3);

    gl_FragColor = vec4(color, 1.0);
}