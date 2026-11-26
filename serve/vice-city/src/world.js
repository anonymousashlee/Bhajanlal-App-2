import * as THREE from 'three';
import { rand, randInt, pick, makeCanvas, glowTexture, clamp } from './utils.js';

export const S = 64;
export const GRID = 10;
export const HALF = (GRID * S) / 2;
export const ROAD = 18;

const MIAMI = [0xffb3c6, 0x9be7ff, 0xfff1d0, 0xa7f3d0, 0xfde68a, 0xe9b8f0, 0xf8bbd0, 0xb2ebf2];
const NEON_SIGNS = ['HOTEL', 'MALIBU', 'PAWN', 'OCEAN', 'VICE', 'CLUB', 'DINER', 'NEON', 'TATTOO', 'SUNSET', 'RADIO', 'BEACH'];

function facadeTexture() {
  const w = 128, h = 256;
  const c = makeCanvas(w, h);
  const g = c.getContext('2d');
  const base = '#' + new THREE.Color(pick(MIAMI)).getHexString();
  g.fillStyle = base; g.fillRect(0, 0, w, h);
  g.fillStyle = 'rgba(0,0,0,.1)';
  for (let y = 0; y < h; y += 32) g.fillRect(0, y, w, 3);
  const cols = 6, rows = 14;
  const cw = w / cols, ch = h / rows;
  const litColors = ['#ffd98a', '#9ff4ff', '#ffb3d9'];
  for (let r = 0; r < rows; r++) {
    for (let cx = 0; cx < cols; cx++) {
      const x = cx * cw + cw * 0.2, y = r * ch + ch * 0.22;
      const ww = cw * 0.6, wh = ch * 0.5;
      const lit = Math.random() < 0.4;
      g.fillStyle = lit ? 'rgba(255,255,255,.3)' : 'rgba(20,24,40,.75)';
      g.fillRect(x, y, ww, wh);
      g.strokeStyle = 'rgba(255,255,255,.35)'; g.lineWidth = 1;
      g.strokeRect(x, y, ww, wh);
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function makeNeonSign(text, color, width) {
  const g = new THREE.Group();
  const c = makeCanvas(256, 96);
  const ctx = c.getContext('2d');
  ctx.fillStyle = 'rgba(6,4,16,.92)'; ctx.fillRect(0, 0, 256, 96);
  ctx.strokeStyle = '#' + new THREE.Color(color).getHexString(); ctx.lineWidth = 5;
  ctx.strokeRect(7, 7, 242, 82);
  ctx.font = 'bold 52px Impact, sans-serif';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.shadowColor = '#' + new THREE.Color(color).getHexString(); ctx.shadowBlur = 26;
  ctx.fillStyle = '#fff';
  ctx.fillText(text, 128, 48);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(width, width * 0.375), mat);
  g.add(mesh);
  g.userData.flicker = { mat, base: 1.6, phase: rand(0, 10) };
  return g;
}

function makeSky() {
  const g = new THREE.Group();
  // gradient sky sphere
  const skyGeo = new THREE.SphereGeometry(1000, 32, 16);
  const skyMat = new THREE.ShaderMaterial({
    uniforms: { topColor: { value: new THREE.Color(0xff5f6d) }, bottomColor: { value: new THREE.Color(0x1a0033) } },
    vertexShader: `varying vec3 vPos; void main(){ vPos = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 topColor; uniform vec3 bottomColor; varying vec3 vPos; void main(){ float h = normalize(vPos).y * 0.5 + 0.5; gl_FragColor = vec4(mix(bottomColor, topColor, h), 1.0); }`,
    side: THREE.BackSide,
  });
  g.add(new THREE.Mesh(skyGeo, skyMat));
  return g;
}

export function buildWorld(scene) {
  const colliders = [];
  const circles = [];
  const swayers = [];
  const flickers = [];
  const blocks = [];
  const neonSigns = [];

  scene.fog = new THREE.FogExp2(0xf08a5a, 0.0034);
  scene.add(makeSky());

  const hemi = new THREE.HemisphereLight(0xff9ec4, 0x3b1f5e, 0.85);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xffb37a, 2.6);
  sun.position.set(-160, 90, 60);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  const d = 140;
  sun.shadow.camera.left = -d; sun.shadow.camera.right = d;
  sun.shadow.camera.top = d; sun.shadow.camera.bottom = -d;
  sun.shadow.camera.far = 520;
  sun.shadow.bias = -0.0008;
  scene.add(sun);
  const rim = new THREE.DirectionalLight(0x6fd8ff, 0.55);
  rim.position.set(120, 60, -140);
  scene.add(rim);

  // sun disc
  const sunGlow = new THREE.Sprite(new THREE.SpriteMaterial({
    map: glowTexture('rgba(255,240,190,1)', 'rgba(255,240,190,0)'), color: 0xffd9a0,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  }));
  sunGlow.position.set(-620, 62, 240);
  sunGlow.scale.setScalar(240);
  scene.add(sunGlow);

  // ground
  const land = new THREE.Mesh(
    new THREE.PlaneGeometry(GRID * S, GRID * S),
    new THREE.MeshStandardMaterial({ color: 0x3a3550, roughness: 1 })
  );
  land.rotation.x = -Math.PI / 2;
  land.receiveShadow = true;
  scene.add(land);

  // roads
  const roadMat = new THREE.MeshStandardMaterial({ color: 0x22222c, roughness: 0.92 });
  for (let i = 0; i <= GRID; i++) {
    const line = -HALF + i * S;
    // vertical road
    const rv = new THREE.Mesh(new THREE.PlaneGeometry(ROAD, GRID * S), roadMat);
    rv.rotation.x = -Math.PI / 2;
    rv.position.set(line, 0.01, 0);
    rv.receiveShadow = true;
    scene.add(rv);
    // horizontal road
    const rh = new THREE.Mesh(new THREE.PlaneGeometry(GRID * S, ROAD), roadMat);
    rh.rotation.x = -Math.PI / 2;
    rh.position.set(0, 0.01, line);
    rh.receiveShadow = true;
    scene.add(rh);
  }

  // buildings
  const facadeCache = {};
  function getFacade() {
    const k = Math.floor(Math.random() * 8);
    if (!facadeCache[k]) facadeCache[k] = facadeTexture();
    return facadeCache[k];
  }

  for (let gx = 0; gx < GRID; gx++) {
    for (let gz = 0; gz < GRID; gz++) {
      const cx = -HALF + gx * S + S / 2;
      const cz = -HALF + gz * S + S / 2;
      const inner = S - ROAD;
      // sometimes a park/plaza
      const type = Math.random() < 0.12 ? 'park' : Math.random() < 0.08 ? 'plaza' : 'block';
      blocks.push({ cx, cz, type });
      if (type === 'park') {
        const p = new THREE.Mesh(new THREE.PlaneGeometry(inner * 0.9, inner * 0.9),
          new THREE.MeshStandardMaterial({ color: 0x1f4d33, roughness: 1 }));
        p.rotation.x = -Math.PI / 2;
        p.position.set(cx, 0.02, cz);
        scene.add(p);
        // a few palms
        for (let i = 0; i < 4; i++) {
          const px = cx + rand(-inner / 3, inner / 3);
          const pz = cz + rand(-inner / 3, inner / 3);
          const palm = makePalm(px, pz);
          scene.add(palm);
          circles.push({ x: px, z: pz, r: 0.6 });
        }
        continue;
      }
      if (type === 'plaza') {
        const p = new THREE.Mesh(new THREE.PlaneGeometry(inner * 0.9, inner * 0.9),
          new THREE.MeshStandardMaterial({ color: 0x4a4468, roughness: 0.9 }));
        p.rotation.x = -Math.PI / 2;
        p.position.set(cx, 0.02, cz);
        scene.add(p);
        continue;
      }
      // building block
      const w = rand(inner * 0.7, inner * 0.95);
      const dp = rand(inner * 0.7, inner * 0.95);
      const h = rand(8, 36);
      const tex = getFacade();
      const mat = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.85 });
      const bld = new THREE.Mesh(new THREE.BoxGeometry(w, h, dp), mat);
      bld.position.set(cx, h / 2, cz);
      bld.castShadow = true;
      bld.receiveShadow = true;
      scene.add(bld);
      colliders.push({ minX: cx - w / 2, maxX: cx + w / 2, minZ: cz - dp / 2, maxZ: cz + dp / 2, h });
      // neon sign sometimes
      if (Math.random() < 0.5) {
        const color = pick([0xff2e88, 0x2ee6ff, 0xffd166, 0x8b5cf6, 0x39ff88, 0xff7a1a]);
        const sign = makeNeonSign(pick(NEON_SIGNS), color, clamp(w * 0.5, 3, 8));
        const face = pick(['n', 's', 'e', 'w']);
        const y = clamp(h * rand(0.3, 0.7), 3, h - 2);
        if (face === 'n') { sign.position.set(cx, y, cz - dp / 2 - 0.1); sign.rotation.y = Math.PI; }
        if (face === 's') { sign.position.set(cx, y, cz + dp / 2 + 0.1); }
        if (face === 'e') { sign.position.set(cx + w / 2 + 0.1, y, cz); sign.rotation.y = Math.PI / 2; }
        if (face === 'w') { sign.position.set(cx - w / 2 - 0.1, y, cz); sign.rotation.y = -Math.PI / 2; }
        scene.add(sign);
        flickers.push(sign.userData.flicker);
        neonSigns.push({ pos: sign.position.clone(), color });
      }
    }
  }

  // beach + ocean on east
  const beach = new THREE.Mesh(new THREE.PlaneGeometry(46, GRID * S),
    new THREE.MeshStandardMaterial({ color: 0xc9b183, roughness: 1 }));
  beach.rotation.x = -Math.PI / 2;
  beach.position.set(HALF + 23, 0.02, 0);
  scene.add(beach);
  const oceanGeo = new THREE.PlaneGeometry(200, GRID * S, 40, 10);
  const oceanBase = oceanGeo.attributes.position.array.slice();
  const ocean = new THREE.Mesh(oceanGeo, new THREE.MeshStandardMaterial({ color: 0x0b3a63, roughness: 0.3, metalness: 0.4 }));
  ocean.rotation.x = -Math.PI / 2;
  ocean.position.set(HALF + 146, -0.2, 0);
  scene.add(ocean);

  // landmark hotel
  {
    const hotel = new THREE.Mesh(new THREE.BoxGeometry(40, 46, 34),
      new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.8 }));
    hotel.position.set(HALF + 22, 23, -HALF * 0.55);
    hotel.castShadow = true;
    scene.add(hotel);
    colliders.push({ minX: HALF + 2, maxX: HALF + 42, minZ: -HALF * 0.55 - 17, maxZ: -HALF * 0.55 + 17, h: 46 });
    const sign = makeNeonSign('MALIBU', 0xff2e88, 22);
    sign.position.set(HALF + 2, 34, -HALF * 0.55);
    sign.rotation.y = -Math.PI / 2;
    scene.add(sign);
    flickers.push(sign.userData.flicker);
    neonSigns.push({ pos: sign.position.clone(), color: 0xff2e88 });
  }

  // palm trees along beach
  for (let i = 0; i < 14; i++) {
    const z = -HALF + (i + 0.5) * (GRID * S / 14);
    const px = HALF + 8;
    const palm = makePalm(px, z);
    scene.add(palm);
    circles.push({ x: px, z, r: 0.6 });
  }

  function makePalm(x, z) {
    const g = new THREE.Group();
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.3, 6, 8), new THREE.MeshStandardMaterial({ color: 0x6b4f3a, roughness: 0.9 }));
    trunk.position.set(x, 3, z);
    g.add(trunk);
    const top = new THREE.Group();
    top.position.set(x, 6, z);
    for (let i = 0; i < 6; i++) {
      const leaf = new THREE.Mesh(new THREE.ConeGeometry(1.6, 0.3, 6), new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.7 }));
      leaf.position.set(Math.cos(i / 6 * Math.PI * 2) * 1.2, 0, Math.sin(i / 6 * Math.PI * 2) * 1.2);
      leaf.rotation.x = 0.6;
      leaf.rotation.z = (i / 6) * Math.PI * 2;
      top.add(leaf);
    }
    g.add(top);
    swayers.push({ top, phase: rand(0, 10), amp: 0.05 });
    return g;
  }

  // helpers exposed
  function resolve(pos, radius) {
    for (const c of colliders) {
      const nx = clamp(pos.x, c.minX, c.maxX);
      const nz = clamp(pos.z, c.minZ, c.maxZ);
      const dx = pos.x - nx, dz = pos.z - nz;
      if (dx * dx + dz * dz < radius * radius) {
        const d = Math.sqrt(dx * dx + dz * dz) || 0.001;
        pos.x = nx + (dx / d) * radius;
        pos.z = nz + (dz / d) * radius;
      }
    }
    for (const c of circles) {
      const dx = pos.x - c.x, dz = pos.z - c.z;
      const d = Math.hypot(dx, dz);
      if (d < radius + c.r && d > 0.001) {
        pos.x = c.x + (dx / d) * (radius + c.r);
        pos.z = c.z + (dz / d) * (radius + c.r);
      }
    }
  }

  function hitsBuilding(pos, radius) {
    for (const c of colliders) {
      const nx = clamp(pos.x, c.minX, c.maxX);
      const nz = clamp(pos.z, c.minZ, c.maxZ);
      const dx = pos.x - nx, dz = pos.z - nz;
      if (dx * dx + dz * dz < radius * radius) return true;
    }
    return false;
  }

  let time = 0;
  function update(dt) {
    time += dt;
    // ocean waves
    const arr = oceanGeo.attributes.position.array;
    for (let i = 0; i < arr.length; i += 3) {
      const x = oceanBase[i], y = oceanBase[i + 1];
      arr[i + 2] = Math.sin(x * 0.045 + time * 1.1) * 0.55 + Math.cos(y * 0.037 + time * 0.8) * 0.45;
    }
    oceanGeo.attributes.position.needsUpdate = true;
    // palm sway
    for (const s of swayers) {
      s.top.rotation.z = Math.sin(time * 0.9 + s.phase) * s.amp;
      s.top.rotation.x = Math.cos(time * 0.7 + s.phase) * s.amp;
    }
    // neon flicker
    for (const f of flickers) {
      const n = Math.sin(time * 9 + f.phase) * Math.sin(time * 3.3 + f.phase * 2);
      const glitch = (Math.sin(time * 31 + f.phase) > 0.985) ? 0.15 : 1;
      f.mat.emissiveIntensity = (f.base * (0.92 + n * 0.08)) * glitch;
      // emissiveIntensity only works if material has emissive; MeshBasicMaterial ignores but harmless
    }
  }

  return { resolve, hitsBuilding, update, colliders, circles, blocks, sun, hemi, neonSigns };
}