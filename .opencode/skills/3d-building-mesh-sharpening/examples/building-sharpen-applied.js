// building-mesh-sharpen-applied.js
// APPLIED 3d-building-mesh-sharpening: full pipeline for extruded OSM /
// photorealistic building meshes. Combines normal recompute, edge lighting
// tuning, over-bright cap, and crispness validation into one callable.

import { recomputeSmoothNormals, validateCrispness } from './sharpen-normals.js';

// Step 2: lighting tuned for edge definition without over-brightening.
export const SHARPEN_LIGHTING = {
  ambient: 0.18,        // low ambient preserves edges
  specular: 0.12,       // subtle specular on crisp corners
  shininess: 48.0,      // 32-64 range for buildings
  overBrightCap: 0.85,  // clamp combined luminance
  rimStrength: 0.25,
};

// Step 3 helper: clamp a luminance value to the configured cap.
export function clampLuminance(lum, cap = SHARPEN_LIGHTING.overBrightCap) {
  return Math.min(lum, cap);
}

// Full apply: recompute normals -> tune lighting -> validate crispness.
export function applyBuildingSharpening(geometry, lighting = SHARPEN_LIGHTING) {
  recomputeSmoothNormals(geometry);
  const validation = validateCrispness(geometry, 0.98);
  if (!validation.ok) {
    // Re-normalize any drifted vertices once more.
    recomputeSmoothNormals(geometry);
  }
  return { geometry, lighting, validation: validateCrispness(geometry, 0.98) };
}

// Cesium/Three.js usage:
//   const result = applyBuildingSharpening(osmBuildingGeometry);
//   mesh.material.uniforms.u_lightDir.value = sunDirection;
//   mesh.material.uniforms.u_ambient.value = result.lighting.ambient;
//   mesh.material.uniforms.u_specular.value = result.lighting.specular;
//   mesh.material.uniforms.u_shininess.value = result.lighting.shininess;
//   mesh.material.uniforms.u_overBrightCap.value = result.lighting.overBrightCap;
