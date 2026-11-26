import * as THREE from 'three';
import { rand, pick, dampAngle, clamp } from './utils.js';

const M = (c, opts = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.72, metalness: 0.05, ...opts });

function capsule(r, len, mat) {
  const m = new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 6, 14), mat);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
function box(w, h, d, mat) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
function sphere(r, mat, w = 16, h = 12) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(r, w, h), mat);
  m.castShadow = true;
  return m;
}

function makeFace(skinMat, mood) {
  const head = new THREE.Group();
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.132, 24, 20), skinMat);
  skull.scale.set(1.0, 1.14, 0.97);
  skull.castShadow = true;
  head.add(skull);
  const jaw = new THREE.Mesh(new THREE.SphereGeometry(0.105, 18, 14), skinMat);
  jaw.position.set(0, -0.055, 0.015);
  jaw.scale.set(0.92, 0.62, 0.86);
  head.add(jaw);
  for (const sx of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.026, 10, 8), skinMat);
    ear.position.set(sx * 0.132, -0.005, -0.01);
    ear.scale.set(0.55, 1.05, 0.7);
    head.add(ear);
  }
  const eyeW = new THREE.MeshStandardMaterial({ color: 0xf6f3ee, roughness: 0.25 });
  const irisColor = pick([0x3b2314, 0x1e3a5f, 0x2d5a27, 0x6b4423]);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x0a0a12, roughness: 0.2 });
  for (const sx of [-1, 1]) {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.031, 14, 12), eyeW);
    e.position.set(sx * 0.052, 0.02, 0.116);
    e.scale.set(1, 1.12, 0.62);
    head.add(e);
    const iris = new THREE.Mesh(new THREE.SphereGeometry(0.017, 10, 8), new THREE.MeshStandardMaterial({ color: irisColor, roughness: 0.35 }));
    iris.position.set(sx * 0.054, 0.019, 0.134);
    iris.scale.set(1, 1, 0.5);
    head.add(iris);
    const p = new THREE.Mesh(new THREE.SphereGeometry(0.009, 8, 6), pupilMat);
    p.position.set(sx * 0.055, 0.019, 0.138);
    p.scale.set(1, 1, 0.5);
    head.add(p);
    const hl = new THREE.Mesh(new THREE.SphereGeometry(0.004, 6, 4), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    hl.position.set(sx * 0.05, 0.026, 0.14);
    head.add(hl);
    const browMat = new THREE.MeshStandardMaterial({ color: 0x2a1a12, roughness: 0.8 });
    const b = new THREE.Mesh(new THREE.BoxGeometry(0.052, 0.016, 0.022), browMat);
    b.position.set(sx * 0.055, 0.078, 0.118);
    b.rotation.z = mood === 'angry' ? sx * -0.42 : mood === 'cool' ? sx * 0.15 : sx * 0.06;
    head.add(b);
  }
  const nose = new THREE.Mesh(new THREE.ConeGeometry(0.022, 0.06, 8), skinMat);
  nose.position.set(0, -0.012, 0.13);
  nose.rotation.x = Math.PI / 2;
  head.add(nose);
  const noseTip = sphere(0.018, skinMat);
  noseTip.position.set(0, -0.022, 0.152);
  head.add(noseTip);
  const mouthColor = mood === 'angry' ? 0x6b1525 : 0x8a2f3a;
  const mouth = new THREE.Mesh(new THREE.BoxGeometry(0.058, 0.016, 0.02),
    new THREE.MeshStandardMaterial({ color: mouthColor, roughness: 0.55 }));
  mouth.position.set(0, -0.068, 0.116);
  mouth.rotation.z = mood === 'angry' ? 0.12 : (mood === 'cool' ? -0.06 : 0);
  head.add(mouth);
  const lip = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.01, 0.018),
    new THREE.MeshStandardMaterial({ color: mouthColor, roughness: 0.5 }));
  lip.position.set(0, -0.076, 0.116);
  head.add(lip);
  for (const sx of [-1, 1]) {
    const blush = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 6),
      new THREE.MeshStandardMaterial({ color: 0xff9bb5, roughness: 0.9, transparent: true, opacity: 0.18 }));
    blush.position.set(sx * 0.095, -0.025, 0.095);
    head.add(blush);
  }
  return head;
}

function makeHair(style, color) {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.82 });
  const cap = (r, sy = 1, offY = 0) => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 18, 14, 0, Math.PI * 2, 0, Math.PI * 0.62), mat);
    m.scale.set(1, sy, 1); m.position.y = offY; m.castShadow = true;
    return m;
  };
  if (style === 'short') { g.add(cap(0.145, 1.06, 0.025)); }
  else if (style === 'bun') { g.add(cap(0.148, 1.02, 0.03)); const b = sphere(0.072, mat); b.position.set(0, 0.105, -0.115); g.add(b); }
  else if (style === 'ponytail') { g.add(cap(0.15, 1.03, 0.025)); const p = new THREE.Mesh(new THREE.CapsuleGeometry(0.042, 0.18, 5, 10), mat); p.position.set(0, -0.03, -0.15); p.rotation.x = 0.55; g.add(p); }
  else if (style === 'afro') { const a = sphere(0.19, mat); a.position.y = 0.05; a.scale.set(1.06, 0.96, 1.03); g.add(a); }
  else if (style === 'mohawk') { const m = box(0.04, 0.15, 0.28, mat); m.position.y = 0.135; g.add(m); }
  else if (style === 'cap') {
    const c = cap(0.155, 0.92, 0.045); c.material = new THREE.MeshStandardMaterial({ color: 0x1b1b26, roughness: 0.7 }); g.add(c);
    const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.155, 0.155, 0.022, 16, 1, false, 0, Math.PI), new THREE.MeshStandardMaterial({ color: 0x1b1b26, roughness: 0.7 }));
    brim.rotation.z = -Math.PI / 2; brim.rotation.y = Math.PI / 2; brim.position.set(0, 0.032, 0.095); brim.scale.set(1, 1, 0.85); g.add(brim);
  }
  else if (style === 'long') { g.add(cap(0.152, 1.02, 0.025)); const back = new THREE.Mesh(new THREE.CapsuleGeometry(0.12, 0.2, 5, 10), mat); back.position.set(0, -0.09, -0.1); back.scale.set(1.12, 1, 0.62); g.add(back); }
  else { /* bald */ }
  return g;
}

export function makeHuman(opts = {}) {
  const o = Object.assign({
    skin: 0xd9a074, hair: 0x2a1a12, hairStyle: 'short',
    shirt: 0xff2e88, pants: 0x2a2f4a, shoes: 0x15151d,
    accessory: null, mood: 'chill', scale: 1,
  }, opts);

  const skinMat = M(o.skin, { roughness: 0.6 });
  const group = new THREE.Group();
  const root = new THREE.Group();
  group.add(root);
  const hips = new THREE.Group();
  hips.position.y = 0.86;
  root.add(hips);

  const shirtMat = M(o.shirt, { roughness: 0.7 });
  const pantsMat = M(o.pants, { roughness: 0.78 });
  const shoeMat = M(o.shoes, { roughness: 0.5 });
  const accentMat = M(0xffffff, { roughness: 0.6 });

  const torso = capsule(0.16, 0.32, shirtMat);
  torso.position.y = 0.24; torso.scale.set(1.14, 1, 0.8);
  hips.add(torso);
  for (let i = 0; i < 3; i++) {
    const btn = sphere(0.012, accentMat);
    btn.position.set(0, 0.32 - i * 0.09, 0.135);
    hips.add(btn);
  }
  const collar = new THREE.Mesh(new THREE.TorusGeometry(0.115, 0.022, 8, 16, Math.PI), M(0xffffff, { roughness: 0.6 }));
  collar.position.set(0, 0.42, 0.02); collar.rotation.x = Math.PI / 2;
  hips.add(collar);

  const pelvis = capsule(0.145, 0.07, o.accessory === 'dress' ? shirtMat : pantsMat);
  pelvis.position.y = -0.005; pelvis.scale.set(1.12, 1, 0.82);
  hips.add(pelvis);

  const neck = capsule(0.052, 0.06, skinMat);
  neck.position.y = 0.47;
  hips.add(neck);

  const headGroup = new THREE.Group();
  headGroup.position.y = 0.61;
  hips.add(headGroup);
  const face = makeFace(skinMat, o.mood);
  headGroup.add(face);
  const hair = makeHair(o.hairStyle, o.hair);
  hair.position.y = 0.04;
  headGroup.add(hair);
  if (o.accessory === 'sunglasses') {
    const gl = box(0.15, 0.038, 0.022, new THREE.MeshStandardMaterial({ color: 0x0a0a12, roughness: 0.12, metalness: 0.6 }));
    gl.position.set(0, 0.02, 0.132);
    headGroup.add(gl);
  }
  if (o.accessory === 'cap') { const c = makeHair('cap', 0); c.position.y = 0.05; headGroup.add(c); }

  const mkArm = (side) => {
    const shoulder = new THREE.Group();
    shoulder.position.set(side * 0.225, 0.39, 0);
    hips.add(shoulder);
    const upper = capsule(0.058, 0.17, shirtMat);
    upper.position.y = -0.14; shoulder.add(upper);
    const cuff = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.03, 10), shirtMat);
    cuff.position.y = -0.24; shoulder.add(cuff);
    const forePivot = new THREE.Group();
    forePivot.position.y = -0.29; shoulder.add(forePivot);
    const fore = capsule(0.05, 0.16, o.sleeves === 'long' ? shirtMat : skinMat);
    fore.position.y = -0.13; forePivot.add(fore);
    const hand = sphere(0.05, skinMat, 10, 8);
    hand.position.y = -0.25; forePivot.add(hand);
    for (let f = 0; f < 4; f++) {
      const finger = new THREE.Mesh(new THREE.CapsuleGeometry(0.011, 0.04, 4, 6), skinMat);
      finger.position.set(side * (f - 1.5) * 0.012, -0.29, 0.025);
      finger.rotation.x = 0.3; forePivot.add(finger);
    }
    return { shoulder, forePivot };
  };
  const armL = mkArm(-1), armR = mkArm(1);

  const mkLeg = (side) => {
    const hip = new THREE.Group();
    hip.position.set(side * 0.095, -0.02, 0);
    hips.add(hip);
    const thigh = capsule(0.08, 0.21, o.accessory === 'dress' ? skinMat : pantsMat);
    thigh.position.y = -0.18; hip.add(thigh);
    const knee = new THREE.Group();
    knee.position.y = -0.4; hip.add(knee);
    const shin = capsule(0.065, 0.21, o.accessory === 'dress' ? skinMat : pantsMat);
    shin.position.y = -0.17; knee.add(shin);
    const foot = box(0.105, 0.075, 0.23, shoeMat);
    foot.position.set(0, -0.31, 0.05); knee.add(foot);
    const sole = box(0.11, 0.02, 0.24, M(0x0a0a0e, { roughness: 0.4 }));
    sole.position.set(0, -0.34, 0.05); knee.add(sole);
    return { hip, knee };
  };
  const legL = mkLeg(-1), legR = mkLeg(1);

  if (o.accessory === 'dress') {
    const skirt = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.46, 20, 1, true), shirtMat);
    skirt.material.side = THREE.DoubleSide; skirt.position.y = -0.16; hips.add(skirt);
  }
  if (o.accessory === 'suit') {
    const jacket = box(0.095, 0.32, 0.035, M(0x0e0e18, { roughness: 0.5 }));
    jacket.position.set(0, 0.23, 0.12); hips.add(jacket);
    const tie = box(0.042, 0.18, 0.022, M(0xc41e4a, { roughness: 0.4 }));
    tie.position.set(0, 0.27, 0.14); hips.add(tie);
  }
  if (o.accessory === 'bag') {
    const bag = box(0.18, 0.22, 0.08, M(0x3a2a1a, { roughness: 0.6 }));
    bag.position.set(0.28, 0.18, -0.05); hips.add(bag);
  }

  group.scale.setScalar(o.scale);

  const char = {
    group, root, hips, headGroup, torso, armL, armR, legL, legR,
    t: rand(0, 10), mode: 'idle', speed01: 0, punchT: 0, punchCD: 0,
    steer: 0, blinkT: rand(2, 5), blink: 0,
    yaw: 0, targetYaw: 0, baseY: 0, dead: false, talkT: 0,
    startPunch() { if (this.punchCD <= 0) { this.punchT = 1; this.punchCD = 0.55; } },
    update(dt, { mode = 'idle', speed = 0, moving = false } = {}) {
      this.t += dt * (1 + speed * 0.6);
      this.punchCD = Math.max(0, this.punchCD - dt);
      if (this.punchT > 0) this.punchT = Math.max(0, this.punchT - dt * 2.6);
      this.mode = mode;
      this.speed01 = speed;

      this.blinkT -= dt;
      if (this.blinkT <= 0) { this.blink = 0.18; this.blinkT = rand(2.5, 5.5); }
      if (this.blink > 0) this.blink = Math.max(0, this.blink - dt * 4);

      const walk = clamp(speed, 0, 1);
      const swing = Math.sin(this.t * 7.5) * (0.38 + walk * 0.58);
      const swing2 = Math.sin(this.t * 7.5 + Math.PI) * (0.38 + walk * 0.58);

      if (this.dead) {
        this.root.rotation.x = dampAngle(this.root.rotation.x, -Math.PI / 2, 7, dt);
        this.hips.position.y = dampAngle(this.hips.position.y, 0.32, 7, dt);
        this.armL.shoulder.rotation.x = dampAngle(this.armL.shoulder.rotation.x, -1.1, 6, dt);
        this.armR.shoulder.rotation.x = dampAngle(this.armR.shoulder.rotation.x, -1.4, 6, dt);
        this.legL.hip.rotation.x = dampAngle(this.legL.hip.rotation.x, -0.3, 6, dt);
        this.legR.hip.rotation.x = dampAngle(this.legR.hip.rotation.x, 0.1, 6, dt);
        return;
      }
      if (mode === 'sit') {
        this.hips.position.y = dampAngle(this.hips.position.y, 0.62, 10, dt);
        this.legL.hip.rotation.x = dampAngle(this.legL.hip.rotation.x, -1.35, 10, dt);
        this.legR.hip.rotation.x = dampAngle(this.legR.hip.rotation.x, -1.35, 10, dt);
        this.legL.knee.rotation.x = dampAngle(this.legL.knee.rotation.x, 1.3, 10, dt);
        this.legR.knee.rotation.x = dampAngle(this.legR.knee.rotation.x, 1.3, 10, dt);
        const steer = this.steer || 0;
        this.armL.shoulder.rotation.x = dampAngle(this.armL.shoulder.rotation.x, -1.18, 10, dt);
        this.armR.shoulder.rotation.x = dampAngle(this.armR.shoulder.rotation.x, -1.18, 10, dt);
        this.armL.shoulder.rotation.z = dampAngle(this.armL.shoulder.rotation.z, -0.32 + steer * 0.45, 8, dt);
        this.armR.shoulder.rotation.z = dampAngle(this.armR.shoulder.rotation.z, 0.32 + steer * 0.45, 8, dt);
        this.armL.forePivot.rotation.x = dampAngle(this.armL.forePivot.rotation.x, -0.92, 10, dt);
        this.armR.forePivot.rotation.x = dampAngle(this.armR.forePivot.rotation.x, -0.92, 10, dt);
        this.hips.rotation.y = dampAngle(this.hips.rotation.y, 0, 8, dt);
        this.hips.rotation.x = dampAngle(this.hips.rotation.x, 0.05, 8, dt);
        return;
      }
      const p = this.punchT > 0 ? Math.sin((1 - this.punchT) * Math.PI) : 0;
      const idleBreath = Math.sin(this.t * 1.6) * 0.05;
      this.armL.shoulder.rotation.x = dampAngle(this.armL.shoulder.rotation.x, moving ? swing : -0.1 + idleBreath, 14, dt);
      this.armR.shoulder.rotation.x = moving ? swing2 : 0.1 - idleBreath;
      if (this.punchT > 0) {
        this.armR.shoulder.rotation.x = -0.45 - p * 2.2;
        this.armR.forePivot.rotation.x = -0.55 + p * 0.6;
        this.hips.rotation.y = -p * 0.55;
      } else {
        this.armR.forePivot.rotation.x = dampAngle(this.armR.forePivot.rotation.x, -0.2, 12, dt);
        this.hips.rotation.y = dampAngle(this.hips.rotation.y, 0, 8, dt);
      }
      this.armL.forePivot.rotation.x = dampAngle(this.armL.forePivot.rotation.x, moving ? -0.28 - walk * 0.42 : -0.2, 12, dt);
      this.armL.shoulder.rotation.z = dampAngle(this.armL.shoulder.rotation.z, 0.07, 8, dt);
      this.armR.shoulder.rotation.z = dampAngle(this.armR.shoulder.rotation.z, -0.07, 8, dt);

      if (moving) {
        this.legL.hip.rotation.x = swing;
        this.legR.hip.rotation.x = swing2;
        this.legL.knee.rotation.x = Math.max(0, -swing) * 0.95;
        this.legR.knee.rotation.x = Math.max(0, -swing2) * 0.95;
      } else {
        this.legL.hip.rotation.x = dampAngle(this.legL.hip.rotation.x, 0, 12, dt);
        this.legR.hip.rotation.x = dampAngle(this.legR.hip.rotation.x, 0, 12, dt);
        this.legL.knee.rotation.x = dampAngle(this.legL.knee.rotation.x, 0, 12, dt);
        this.legR.knee.rotation.x = dampAngle(this.legR.knee.rotation.x, 0, 12, dt);
      }

      const bob = moving ? Math.abs(Math.sin(this.t * 7.5)) * 0.055 * (0.4 + walk) : Math.sin(this.t * 1.6) * 0.014;
      this.hips.position.y = 0.86 + bob;
      this.hips.rotation.x = dampAngle(this.hips.rotation.x, moving ? walk * 0.14 : 0, 8, dt);
      this.headGroup.rotation.x = dampAngle(this.headGroup.rotation.x, moving ? -walk * 0.1 : 0, 8, dt);
      this.headGroup.rotation.y = dampAngle(this.headGroup.rotation.y, Math.sin(this.t * 0.7) * 0.06, 4, dt);
    },
    setYaw(y) { this.root.rotation.y = dampAngle(this.root.rotation.y, y, 12, 1 / 60); },
  };
  return char;
}

export const SKINS = [0xf1c9a5, 0xe0ac69, 0xc68642, 0x8d5524, 0x6b4226, 0xffdbac, 0xa86a3d, 0xf8d5c4, 0xd4a574];
export const HAIRS = [0x1b1210, 0x3b2314, 0x6b4423, 0xc9a227, 0x111111, 0x7a7a7a, 0xd94f6a, 0x2ee6ff, 0xff2e88, 0x8b5cf6, 0x22c55e];
export const SHIRTS = [0xff2e88, 0x2ee6ff, 0xffd166, 0x8b5cf6, 0x22c55e, 0xffffff, 0x1f2937, 0xff7a1a, 0xf472b6, 0x0ea5e9, 0xf97316, 0x14b8a6];
export const PANTS = [0x2a2f4a, 0x1f2937, 0x6b4f3a, 0xe5e7eb, 0x374151, 0x9a3412, 0x111827, 0x475569];
export const HAIR_STYLES = ['short', 'ponytail', 'bun', 'afro', 'long', 'mohawk', 'bald', 'short', 'long', 'ponytail', 'cap'];

export function randomHuman(preset = {}) {
  const fem = Math.random() < 0.48;
  return makeHuman(Object.assign({
    skin: pick(SKINS), hair: pick(HAIRS),
    hairStyle: preset.hairStyle ?? (fem ? pick(['ponytail', 'bun', 'long', 'long', 'short']) : pick(['short', 'short', 'afro', 'mohawk', 'bald', 'short'])),
    shirt: pick(SHIRTS), pants: pick(PANTS),
    accessory: Math.random() < 0.28 ? pick(['sunglasses', 'cap', 'suit', 'dress', 'bag']) : null,
    sleeves: Math.random() < 0.35 ? 'long' : 'short',
    mood: pick(['chill', 'chill', 'cool', 'angry', 'cool']),
    scale: rand(0.93, 1.08),
  }, preset));
}