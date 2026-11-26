// sharpen-normals.js
// Step 1: Recompute / smooth mesh normals for extruded OSM & photorealistic buildings.
// Works with Three.js BufferGeometry or Cesium primitive geometry.

export function recomputeSmoothNormals(geometry) {
    // Assumes indexed geometry with position attribute.
    const pos = geometry.attributes.position;
    const idx = geometry.index;
    const count = idx ? idx.count : pos.count;

    // Accumulate per-vertex normals.
    const normals = new Float32Array(pos.count * 3);
    const tmp = new Float32Array(3);

    const get = (i) => [pos.getX(i), pos.getY(i), pos.getZ(i)];

    const addFaceNormal = (a, b, c) => {
        const va = get(a), vb = get(b), vc = get(c);
        // edge vectors
        const e1 = [vb[0]-va[0], vb[1]-va[1], vb[2]-va[2]];
        const e2 = [vc[0]-va[0], vc[1]-va[1], vc[2]-va[2]];
        // cross e1 x e2
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
        for (let i = 0; i < count; i += 3) {
            addFaceNormal(idx.getX(i), idx.getX(i+1), idx.getX(i+2));
        }
    } else {
        for (let i = 0; i < count; i += 3) {
            addFaceNormal(i, i+1, i+2);
        }
    }

    // Normalize accumulated normals (smoothing).
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

// Step 4: crispness validation helper (CPU-side sanity check).
export function validateCrispness(geometry, threshold = 0.98) {
    const n = geometry.attributes.normal;
    if (!n) return { ok: false, reason: 'no normals' };
    let bad = 0;
    for (let i = 0; i < n.count; i++) {
        const l = Math.hypot(n.getX(i), n.getY(i), n.getZ(i));
        if (Math.abs(l - 1) > 1e-3) bad++;
    }
    const ratio = 1 - bad / n.count;
    return { ok: ratio >= threshold, normalizedRatio: ratio, badCount: bad };
}