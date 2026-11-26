// building-sharpen.js
// Applied 3d-building-mesh-sharpening technique (reusable module).
// Step 1: recompute/smooth mesh normals for extruded OSM & photorealistic buildings.
// Step 4: crispness validation helper.

export function recomputeSmoothNormals(geometry) {
  const pos = geometry.attributes.position;
  const idx = geometry.index;
  const count = idx ? idx.count : pos.count;
  const normals = new Float32Array(pos.count * 3);
  const get = (i) => [pos.getX(i), pos.getY(i), pos.getZ(i)];
  const addFaceNormal = (a, b, c) => {
    const va = get(a), vb = get(b), vc = get(c);
    const e1 = [vb[0]-va[0], vb[1]-va[1], vb[2]-va[2]];
    const e2 = [vc[0]-va[0], vc[1]-va[1], vc[2]-va[2]];
    const n = [
      e1[1]*e2[2] - e1[2]*e2[1],
      e1[2]*e2[0] - e1[0]*e2[2],
      e1[0]*e2[1] - e1[1]*e2[0],
    ];
    const len = Math.hypot(...n) || 1;
    n[0]/=len; n[1]/=len; n[2]/=len;
    for (const v of [a,b,c]) {
      normals[v*3]+=n[0]; normals[v*3+1]+=n[1]; normals[v*3+2]+=n[2];
    }
  };
  if (idx) {
    for (let i = 0; i < count; i += 3) addFaceNormal(idx.getX(i), idx.getX(i+1), idx.getX(i+2));
  } else {
    for (let i = 0; i < count; i += 3) addFaceNormal(i, i+1, i+2);
  }
  for (let i = 0; i < pos.count; i++) {
    const x = normals[i*3], y = normals[i*3+1], z = normals[i*3+2];
    const len = Math.hypot(x,y,z) || 1;
    normals[i*3]=x/len; normals[i*3+1]=y/len; normals[i*3+2]=z/len;
  }
  if (geometry.attributes.normal) {
    geometry.attributes.normal.array.set(normals);
    geometry.attributes.normal.needsUpdate = true;
  } else {
    geometry.setAttribute('normal', new (geometry.attributes.position.constructor)(normals, 3));
  }
  return geometry;
}

export function validateCrispness(geometry, threshold = 0.98) {
  const n = geometry.attributes.normal;
  if (!n) return { ok: false, reason: 'no normals', normalizedRatio: 0, badCount: 0 };
  let bad = 0;
  for (let i = 0; i < n.count; i++) {
    const l = Math.hypot(n.getX(i), n.getY(i), n.getZ(i));
    if (Math.abs(l - 1) > 1e-3) bad++;
  }
  const ratio = 1 - bad / n.count;
  return { ok: ratio >= threshold, normalizedRatio: ratio, badCount: bad };
}

// GLSL sharpening fragment (Step 2-4) for reuse in materials.
export const BUILDING_SHARPEN_FRAGMENT = `
precision highp float;
uniform sampler2D u_colorTex;
uniform vec3 u_lightDir;
uniform float u_ambient;
uniform float u_specular;
uniform float u_shininess;
uniform float u_overBrightCap;
varying vec3 v_normal;
varying vec3 v_viewDir;
varying vec2 v_uv;
void main(){
  vec3 N = normalize(v_normal);
  vec3 L = normalize(u_lightDir);
  vec3 V = normalize(v_viewDir);
  vec3 H = normalize(L + V);
  float NdotL = max(dot(N, L), 0.0);
  float rim = pow(1.0 - max(dot(N, V), 0.0), 3.0) * 0.25;
  float spec = pow(max(dot(N, H), 0.0), u_shininess) * u_specular;
  float lum = u_ambient + (1.0 - u_ambient) * NdotL + rim + spec;
  lum = min(lum, u_overBrightCap);
  vec3 base = texture2D(u_colorTex, v_uv).rgb;
  vec3 color = base * lum;
  float edge = smoothstep(0.3, 0.6, NdotL) * (1.0 - smoothstep(0.6, 0.9, NdotL));
  color = mix(color, color * 1.08, edge * 0.3);
  gl_FragColor = vec4(color, 1.0);
}
`;
