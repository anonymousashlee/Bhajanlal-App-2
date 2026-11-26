export function rand(a, b) { return a + Math.random() * (b - a); }
export function randInt(a, b) { return Math.floor(rand(a, b + 1)); }
export function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
export function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
export function dampAngle(a, b, speed, dt) {
  let d = b - a;
  while (d > Math.PI) d -= Math.PI * 2;
  while (d < -Math.PI) d += Math.PI * 2;
  return a + d * (1 - Math.exp(-speed * dt));
}
export function lerp(a, b, t) { return a + (b - a) * t; }

export function makeCanvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
}

export function glowTexture(inner, outer) {
  const c = makeCanvas(128, 128);
  const g = c.getContext('2d');
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, inner);
  gr.addColorStop(1, outer);
  g.fillStyle = gr;
  g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

import * as THREE from 'three';

export const VOCAB = {
  names: ['Rico', 'Lola', 'Avery', 'Mercedes', 'Tommy', 'Lance', 'Ken', 'Phil', 'Umberto', 'Auntie'],
  personalities: [
    { small: ['Nice day!', 'Lovely weather.', 'How are you?', 'Vice City rocks!'], big: ['HEY! Watch it!', 'Are you crazy?!', 'Somebody stop this lunatic!'] },
  ],
  radio: [
    { st: 'NEON WAVE FM', tr: 'Sunset Cruiser — The Palm Queens' },
    { st: 'FLORIDA FREQUENCY', tr: 'Miami Heatwave — VHS Dreams' },
    { st: 'CHROME 104.5', tr: 'Retrograde — Cindy LaSolo' },
  ],
};