import * as THREE from 'three';
import { makeCanvas, glowTexture, rand, pick } from './utils.js';

const VERT = `attribute float aSize; attribute float aAlpha; attribute vec3 aColor; varying float vAlpha; varying vec3 vColor;
void main(){ vAlpha=aAlpha; vColor=aColor; vec4 mv=modelViewMatrix*vec4(position,1.0); gl_PointSize=aSize*(400.0/max(1.0,-mv.z)); gl_Position=projectionMatrix*mv; }`;
const FRAG = `uniform sampler2D uMap; varying float vAlpha; varying vec3 vColor;
void main(){ vec4 tx=texture2D(uMap,gl_PointCoord); if(tx.a*vAlpha<0.01) discard; gl_FragColor=vec4(vColor,tx.a*vAlpha); }`;

function softDot() {
  const c = makeCanvas(64, 64);
  const g = c.getContext('2d');
  const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)');
  gr.addColorStop(0.45, 'rgba(255,255,255,.55)');
  gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

const MAX = 1600;
export class VFX {
  constructor(scene) {
    this.scene = scene;
    const geo = new THREE.BufferGeometry();
    this.pos = new Float32Array(MAX * 3);
    this.col = new Float32Array(MAX * 3);
    this.size = new Float32Array(MAX);
    this.alpha = new Float32Array(MAX);
    geo.setAttribute('position', new THREE.BufferAttribute(this.pos, 3));
    geo.setAttribute('aColor', new THREE.BufferAttribute(this.col, 3));
    geo.setAttribute('aSize', new THREE.BufferAttribute(this.size, 1));
    geo.setAttribute('aAlpha', new THREE.BufferAttribute(this.alpha, 1));
    this.geo = geo;
    this.mat = new THREE.ShaderMaterial({
      uniforms: { uMap: { value: softDot() } },
      vertexShader: VERT, fragmentShader: FRAG,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    });
    this.points = new THREE.Points(geo, this.mat);
    this.points.frustumCulled = false;
    scene.add(this.points);
    this.parts = [];
    for (let i = 0; i < MAX; i++) this.parts.push({
      life: 0, max: 1, vx: 0, vy: 0, vz: 0, grav: 0, drag: 1, size0: 1, size1: 1,
      a0: 1, a1: 0, r0: 1, g0: 1, b0: 1, r1: 1, g1: 1, b1: 1, i, x: 0, y: 0, z: 0,
    });
    this.cursor = 0;
    this.glowTex = glowTexture('rgba(255,255,255,1)', 'rgba(255,255,255,0)');
    this.decals = [];
    this.rainOn = false;
    this.rainTimer = 0;
    this.shockwaves = [];
    this.neonGlows = [];
  }
  emit(p) { const s = this.parts[this.cursor]; this.cursor = (this.cursor + 1) % MAX; Object.assign(s, p); return s; }
  update(dt) {
    const a = this.geo.attributes;
    for (const s of this.parts) {
      if (s.life <= 0) { this.alpha[s.i] = 0; continue; }
      s.life -= dt;
      const t = 1 - Math.max(0, s.life) / s.max;
      s.vy += s.grav * dt;
      s.vx *= s.drag ** (dt * 60); s.vy *= s.drag ** (dt * 60); s.vz *= s.drag ** (dt * 60);
      s.x += s.vx * dt; s.y += s.vy * dt; s.z += s.vz * dt;
      const i3 = s.i * 3;
      this.pos[i3] = s.x; this.pos[i3 + 1] = s.y; this.pos[i3 + 2] = s.z;
      this.size[s.i] = s.size0 + (s.size1 - s.size0) * t;
      this.alpha[s.i] = (s.a0 + (s.a1 - s.a0) * t);
      this.col[i3] = s.r0 + (s.r1 - s.r0) * t;
      this.col[i3 + 1] = s.g0 + (s.g1 - s.g0) * t;
      this.col[i3 + 2] = s.b0 + (s.b1 - s.b0) * t;
    }
    a.position.needsUpdate = true; a.aSize.needsUpdate = true;
    a.aAlpha.needsUpdate = true; a.aColor.needsUpdate = true;
    this.updateNeonGlows(dt);
    // rain
    if (this.rainOn) {
      this.rainTimer -= dt;
      if (this.rainTimer <= 0) {
        this.rainTimer = 0.015;
        const x = (Math.random() - 0.5) * 120;
        const z = (Math.random() - 0.5) * 120;
        const y = 30 + Math.random() * 10;
        this.emit(this.base({ x, y, z, vx: -1 + (Math.random()-0.5)*0.6, vy: -22 - Math.random()*6, vz: (Math.random()-0.5)*0.6, grav: 0, drag: 0.999, life: 1.1, max: 1.1, size0: 0.6, size1: 0.4, r0: 0.7, g0: 0.8, b0: 1.0, r1: 0.5, g1: 0.65, b1: 0.9, a0: 0.5, a1: 0 }));
      }
    }
  }
  base(o) { return Object.assign({ x:0,y:0,z:0,vx:0,vy:0,vz:0,grav:0,drag:1,life:0.6,max:0.6,size0:1,size1:0.2,a0:1,a1:0,r0:1,g0:1,b0:1,r1:1,g1:1,b1:1 }, o); }
  sparks(pos, n = 12, color = [1, 0.85, 0.35]) {
    for (let i = 0; i < n; i++) {
      const a = rand(0, Math.PI * 2), sp = rand(2, 9);
      this.emit(this.base({ x: pos.x, y: pos.y, z: pos.z, vx: Math.cos(a)*sp, vz: Math.sin(a)*sp, vy: rand(1,7), grav: -16, drag: 0.94, life: rand(0.25,0.6), max: 0.6, size0: rand(0.5,1.1), size1: 0.1, r0: color[0], g0: color[1], b0: color[2], r1: 1, g1: 0.5, b1: 0.2 }));
    }
  }
  bloodMist(pos, n = 10) {
    for (let i = 0; i < n; i++) {
      const a = rand(0, Math.PI * 2), sp = rand(0.6, 3);
      this.emit(this.base({ x: pos.x, y: pos.y, z: pos.z, vx: Math.cos(a)*sp, vz: Math.sin(a)*sp, vy: rand(0.5,2.4), grav: -4, drag: 0.9, life: rand(0.3,0.7), max: 0.7, size0: rand(0.7,1.6), size1: 2.4, r0: 1, g0: 0.12, b0: 0.2, r1: 0.5, g1: 0.02, b1: 0.06, a0: 0.9, a1: 0 }));
    }
  }
  tireSmoke(pos, strength = 1) {
    this.emit(this.base({ x: pos.x + rand(-0.4,0.4), y: pos.y + 0.1, z: pos.z + rand(-0.4,0.4), vx: rand(-0.8,0.8), vz: rand(-0.8,0.8), vy: rand(0.4,1.3), drag: 0.96, life: rand(0.7,1.5), max: 1.5, size0: rand(0.8,1.4)*strength, size1: rand(3.4,5)*strength, r0: 0.9, g0: 0.9, b0: 0.95, r1: 0.55, g1: 0.5, b1: 0.62, a0: 0.4, a1: 0 }));
  }
  exhaust(pos, dir) {
    this.emit(this.base({ x: pos.x, y: pos.y, z: pos.z, vx: -dir.x*1.4 + rand(-0.3,0.3), vz: -dir.z*1.4 + rand(-0.3,0.3), vy: rand(0.4,1), drag: 0.95, life: rand(0.4,0.8), max: 0.8, size0: 0.5, size1: 2, r0: 0.7, g0: 0.7, b0: 0.75, r1: 0.3, g1: 0.3, b1: 0.36, a0: 0.32, a1: 0 }));
  }
  explosion(pos, big = false) {
    const n = big ? 70 : 40;
    for (let i = 0; i < n; i++) {
      const a = rand(0, Math.PI * 2), el = rand(-0.2, 1), sp = rand(3, big ? 16 : 11);
      this.emit(this.base({ x: pos.x, y: pos.y, z: pos.z, vx: Math.cos(a)*sp*(1-el*0.5), vz: Math.sin(a)*sp*(1-el*0.5), vy: Math.abs(el)*sp, grav: -6, drag: 0.93, life: rand(0.5,1.3), max: 1.3, size0: rand(1.6,3.4), size1: rand(0.4,1.2), r0: 1, g0: 0.85, b0: 0.3, r1: 0.9, g1: 0.15, b1: 0.02, a0: 1, a1: 0 }));
    }
    for (let i = 0; i < 26; i++) {
      const a = rand(0, Math.PI * 2), sp = rand(1, 6);
      this.emit(this.base({ x: pos.x, y: pos.y + 0.5, z: pos.z, vx: Math.cos(a)*sp, vz: Math.sin(a)*sp, vy: rand(2,7), grav: 1.6, drag: 0.97, life: rand(1,2.2), max: 2.2, size0: 2.5, size1: 7, r0: 0.3, g0: 0.28, b0: 0.3, r1: 0.1, g1: 0.08, b1: 0.12, a0: 0.75, a1: 0 }));
    }
    this.flash(pos, big ? 22 : 14, [1, 0.7, 0.25], 0.35);
    this.shockwave(pos, [1, 0.5, 0.15], 0.6);
    this.debris(pos, big ? 30 : 16);
  }
  flash(pos, size, color, life = 0.25) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.glowTex, color: new THREE.Color(color[0], color[1], color[2]), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 1 }));
    s.position.copy(pos); s.scale.setScalar(size * 0.4);
    this.scene.add(s);
    let t = 0;
    this.decals.push({ s, t, life, size, update: (d, dt) => { d.t += dt; const k = d.t / d.life; d.s.scale.setScalar(d.size * (0.4 + k * 0.8)); d.s.material.opacity = Math.max(0, 1 - k); return d.t < d.life; } });
  }
  makeBeam(color = 0x2ee6ff) {
    const g = new THREE.Group();
    const cyl = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.6, 26, 24, 1, true), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.22, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }));
    cyl.position.y = 13; g.add(cyl);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1.9, 0.09, 8, 40), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9, depthWrite: false }));
    ring.rotation.x = Math.PI / 2; ring.position.y = 0.3; g.add(ring);
    const ring2 = ring.clone(); ring2.position.y = 6; g.add(ring2);
    g.visible = false; this.scene.add(g);
    return g;
  }
  updateDecals(dt) {
    for (let i = this.decals.length - 1; i >= 0; i--) {
      if (!this.decals[i].update(this.decals[i], dt)) {
        this.scene.remove(this.decals[i].s); this.decals[i].s.material.dispose(); this.decals.splice(i, 1);
      }
    }
    for (let i = this.shockwaves.length - 1; i >= 0; i--) {
      const sw = this.shockwaves[i];
      sw.t += dt;
      const k = sw.t / sw.life;
      const r = sw.r0 + (sw.r1 - sw.r0) * k;
      sw.mesh.scale.set(r, 1, r);
      sw.mesh.material.opacity = Math.max(0, (1 - k) * 0.7);
      if (sw.t >= sw.life) { this.scene.remove(sw.mesh); sw.mesh.geometry.dispose(); sw.mesh.material.dispose(); this.shockwaves.splice(i, 1); }
    }
  }
  shockwave(pos, color = [1, 0.6, 0.2], life = 0.55) {
    const geo = new THREE.RingGeometry(0.4, 0.9, 48);
    const mat = new THREE.MeshBasicMaterial({ color: new THREE.Color(color[0], color[1], color[2]), transparent: true, opacity: 0.7, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.rotation.x = -Math.PI / 2;
    mesh.position.copy(pos); mesh.position.y = 0.12;
    this.scene.add(mesh);
    this.shockwaves.push({ mesh, t: 0, life, r0: 0.6, r1: 18 });
  }
  debris(pos, n = 16) {
    for (let i = 0; i < n; i++) {
      const a = Math.random() * Math.PI * 2, sp = 2 + Math.random() * 6;
      this.emit(this.base({ x: pos.x, y: pos.y, z: pos.z, vx: Math.cos(a)*sp, vz: Math.sin(a)*sp, vy: 2 + Math.random()*6, grav: -14, drag: 0.96, life: 0.9 + Math.random()*0.6, max: 1.5, size0: 0.6, size1: 0.15, r0: 0.55, g0: 0.45, b0: 0.35, r1: 0.3, g1: 0.25, b1: 0.2, a0: 1, a1: 0 }));
    }
  }
  neonGlow(pos, color = 0xff2e88, size = 6) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.glowTex, color: new THREE.Color(color), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0.85 }));
    s.position.copy(pos); s.scale.setScalar(size);
    this.scene.add(s);
    this.neonGlows.push({ s, baseSize: size, phase: Math.random() * Math.PI * 2 });
    return s;
  }
  updateNeonGlows(dt) {
    for (const g of this.neonGlows) {
      g.phase += dt * (1.2 + Math.random() * 0.3);
      const f = 0.85 + Math.sin(g.phase) * 0.15;
      g.s.scale.setScalar(g.baseSize * f);
      g.s.material.opacity = 0.7 + Math.sin(g.phase * 1.3) * 0.15;
    }
  }
  setWeather(rain) { this.rainOn = rain; }
  flash(pos, size, color, life = 0.25) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.glowTex, color: new THREE.Color(color[0], color[1], color[2]), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 1 }));
    s.position.copy(pos); s.scale.setScalar(size * 0.4);
    this.scene.add(s);
    let t = 0;
    this.decals.push({ s, t, life, size, update: (d, dt) => { d.t += dt; const k = d.t / d.life; d.s.scale.setScalar(d.size * (0.4 + k * 0.8)); d.s.material.opacity = Math.max(0, 1 - k); return d.t < d.life; } });
  }
}