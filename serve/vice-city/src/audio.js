let ctx = null;
function C() { if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)(); return ctx; }

export const sfx = {
  resume() { try { C().resume(); } catch (e) {} },
  mute(m) {},
  denied() { beep(220, 0.15, 'sawtooth'); },
  punch() { beep(180, 0.08, 'square'); },
  thud() { beep(120, 0.1, 'triangle'); },
  crash() { beep(90, 0.25, 'sawtooth'); },
  boom() { beep(60, 0.4, 'sawtooth'); },
  chime() { beep(660, 0.12, 'sine'); setTimeout(() => beep(880, 0.12, 'sine'), 100); },
  cash() { beep(520, 0.1, 'sine'); },
  horn() { beep(415, 0.5, 'square'); },
  wasted() { beep(110, 0.6, 'sawtooth'); },
  stopEngine() {},
  startEngine() {},
  setEngine() {},
};
function beep(freq, dur, type) {
  try {
    const c = C(); const o = c.createOscillator(); const g = c.createGain();
    o.type = type; o.frequency.value = freq;
    g.gain.value = 0.08;
    o.connect(g); g.connect(c.destination);
    o.start(); o.stop(c.currentTime + dur);
  } catch (e) {}
}