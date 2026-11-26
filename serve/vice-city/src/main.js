import * as THREE from 'three';
import { buildWorld, S, GRID, HALF, ROAD } from './world.js';
import { makeHuman, randomHuman, SKINS, HAIRS, SHIRTS, PANTS, HAIR_STYLES } from './character.js';
import { VFX } from './vfx.js';
import { Vehicle } from './vehicle.js';
import { rand, pick, clamp, dampAngle } from './utils.js';

const canvas = document.querySelector('#game');
const startScreen = document.getElementById('startScreen');
const hud = document.getElementById('hud');
const startBtn = document.getElementById('startBtn');
const moneyEl = document.getElementById('money');
const healthBar = document.getElementById('healthBar');
const armorBar = document.getElementById('armorBar');
const staminaBar = document.getElementById('staminaBar');
const missionBox = document.getElementById('missionBox');
const missionText = document.getElementById('missionText');
const subtitleEl = document.getElementById('subtitle');
const subName = document.getElementById('subName');
const subText = document.getElementById('subText');
const radioStation = document.getElementById('radioStation');
const radioTrack = document.getElementById('radioTrack');
const speedNum = document.getElementById('speedNum');
const gearLabel = document.getElementById('gearLabel');
const vignette = document.getElementById('vignette');
const toast = document.getElementById('toast');
const wastedEl = document.getElementById('wasted');
const promptEl = document.getElementById('prompt');
const pauseScreen = document.getElementById('pauseScreen');
const resumeBtn = document.getElementById('resumeBtn');
const minimapEl = document.getElementById('minimap');
const mctx = minimapEl.getContext('2d');
const speedoEl = document.getElementById('speedo');
const radioEl = document.getElementById('radio');
const starEls = Array.from(document.querySelectorAll('#wanted .star'));

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
camera.position.set(0, 30, 50);
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

let gameState = 'start';
let playerVehicle = null;
let vfx = null;
let humans = [];
let world = null;
const keys = { W: false, A: false, S: false, D: false, Shift: false, Space: false, F: false, H: false, R: false, LMB: false };
const mouse = { x: 0, y: 0, locked: false, lastMove: 0 };
let missionIndex = 0;
let missionComplete = false;

let money = 0;
let wantedLevel = 0;
let wantedT = 0;
let playerHealth = 100;
let armor = 100;
let stamina = 100;
let onFoot = false;
let player = null;
let missionBeam = null;
let subCooldown = 0;
let subTimer = null;
let audioCtx = null;
let playerVy = 0;
let footMoving = false;
let sprinting = false;
let toastTimer = null;

const MISSIONS = [
  { text: 'Steal the taxi and deliver it to the garage.', target: { x: -192, z: 128 }, reward: 500 },
  { text: 'Pick up a passenger at the beach and drive them to the club.', target: { x: 256, z: -128 }, reward: 1200 },
  { text: "Run errands for the mob — collect $5000 from the rival warehouse.", target: { x: -256, z: -64 }, reward: 5000 },
];

const VIDEOGAME_PERSONALITIES = {
  chill: { name: 'Beach Bum', small: ['Nice waves today, dude.', 'Just vibing, homie.', "Sun's gonna bake me good."], big: ['WOAH! Watch it, man!', 'You almost killed me!'] },
  party: { name: 'Party Kid', small: ['This city never sleeps!', "Where's the club at?"], big: ["HEY! My sneakers!", 'Are you serious?!'] },
  business: { name: 'Business Suit', small: ["I'm late for a deal.", 'The market opens at nine.'], big: ["You'll hear from my lawyer!", 'Insane!'] },
  oldtimer: { name: 'Old Timer', small: ['Back in my day this was all swamp.', 'Kids and their loud cars.'], big: ['Young people have no respect!', 'My pacemaker!'] },
  poet: { name: 'Street Poet', small: ['Neon bleeds into the rain...', 'The city breathes at night.'], big: ['The dream shatters!', 'Violence is so unpoetic.'] },
  gym: { name: 'Gym Rat', small: ['Leg day, never skip it.', 'You work out, bro?'], big: ['You wanna GO?!', "I've hit heavier bags!"] },
  shop: { name: 'Shop Owner', small: ['Come see my store!', 'Best prices on the strip.'], big: ['Hey! Watch the merchandise!', 'You gonna pay?!'] },
  tourist: { name: 'Tourist', small: ["Where's the beach?", 'This is nothing like the brochure.'], big: ['Oh my goodness!', 'This is NOT in the brochure!'] },
  cop: { name: 'Cop Wannabe', small: ["I would've made detective.", 'Criminals everywhere.'], big: ["FREEZE! ...okay I'm not a cop.", 'You are in big trouble!'] },
  mechanic: { name: 'Mechanic', small: ['That engine needs oil, pal.', 'I can hear your transmission crying.'], big: ['My bay! You hit my bay!', "That's gonna be expensive!"] },
};

const VIDEOGAME_RADIO = [
  { st: 'NEON WAVE FM', tr: 'Sunset Cruiser — The Palm Queens' },
  { st: 'FLORIDA FREQUENCY', tr: 'Miami Heatwave — VHS Dreams' },
  { st: 'CHROME 104.5', tr: 'Retrograde — Cindy LaSolo' },
  { st: 'VICE TALK RADIO', tr: 'Caller: "Is this the city of the future?"' },
  { st: 'BASSLINE 808', tr: 'Night Drive — Miami Synth Squad' },
];

function initGame() {
  if (gameState === 'playing') return;
  world = buildWorld(scene);
  vfx = new VFX(scene);

  // Advanced VFX: neon glow sprites for city signs
  for (const ns of (world.neonSigns || [])) {
    vfx.neonGlow(ns.pos.clone(), ns.color, 5.5);
  }
  // Weather
  vfx.setWeather(true);

  const spawnPositions = [{ x: -20, z: -20 }, { x: 20, z: -20 }, { x: -20, z: 20 }, { x: 20, z: 20 }, { x: 0, z: 0 }];
  const spawnPos = spawnPositions[Math.floor(Math.random() * spawnPositions.length)];
  const testPos = { x: spawnPos.x, z: spawnPos.z };
  if (world.hitsBuilding(testPos, 3)) {
    testPos.x = (Math.random() - 0.5) * 100;
    testPos.z = (Math.random() - 0.5) * 100;
    world.resolve(testPos, 3);
  }
  playerVehicle = new Vehicle(scene, { x: testPos.x, z: testPos.z, color: 0xff2e88, type: 'sedan' });
  playerVehicle.occupied = true;
  playerVehicle.heading = 0;
  playerVehicle.group.rotation.y = 0;

  playerVehicle.game = {
    onCrash: (impact) => {
      if (impact < 9) return;
      const dmg = (impact - 9) * 2.2;
      const absorbed = Math.min(armor, dmg * 0.6);
      armor -= absorbed;
      playerHealth = Math.max(0, playerHealth - (dmg - absorbed));
      flashVignette();
      if (playerHealth <= 0) wasted();
    },
    onVehicleExplode: () => {
      const p = new THREE.Vector3(playerVehicle.pos.x, 1, playerVehicle.pos.z);
      vfx.explosion(p, true);
      vfx.shockwave(p.clone().setY(0.1), [1, 0.5, 0.15], 0.7);
      vfx.debris(p.clone().setY(0.6), 24);
      showToast('🔥 YOUR RIDE IS WRECKED');
      wasted();
    },
  };

  player = makeHuman({ skin: 0xf1c9a5, hair: 0x1b1210, hairStyle: 'short', shirt: 0xff2e88, pants: 0x2a2f4a, mood: 'cool', accessory: 'sunglasses' });
  player.mood = 'cool';
  player.group.visible = false;
  scene.add(player.group);

  missionBeam = vfx.makeBeam(0x2ee6ff);
  missionBeam.visible = true;
  missionBeam.position.set(MISSIONS[0].target.x, 0, MISSIONS[0].target.z);

  spawnHumans(22);
  buildMinimap();
  updateRadio();
  setMoney();
  setWantedStars();
  showMission(MISSIONS[0].text);

  startScreen.classList.add('hidden');
  hud.classList.remove('hidden');
  speedoEl.classList.remove('hidden');
  radioEl.classList.remove('hidden');
  gameState = 'playing';

  // ---- compatibility shim for legacy smoke tests ----
  window.__vc = {
    get player() { return playerVehicle; },
    get P() { return { health: playerHealth, wanted: wantedLevel, score: money, alive: playerHealth > 0 }; },
    traffic: [],
    police: [],
    camera: camera,
    reset: resetPlayerCompat,
    get started() { return gameState === 'playing'; }
  };
  function resetPlayerCompat() { try { playerHealth = 100; armor = 0; wantedLevel = 0; if (playerVehicle) { playerVehicle.dead = false; playerVehicle.health = 100; playerVehicle.speed = 0; playerVehicle.vel.set(0,0,0); playerVehicle.pos.set(0,0,0); playerVehicle.group.position.set(0,0,0); playerVehicle.heading = 0; playerVehicle.group.rotation.y = 0; } } catch(e){} }
  lastTime = performance.now();
  requestAnimationFrame(gameLoop);
}

function farEnough(x, z) {
  for (const h of humans) {
    const dx = h.group.position.x - x;
    const dz = h.group.position.z - z;
    if (dx * dx + dz * dz < 64) return false;
  }
  return true;
}

function spawnHumans(count) {
  const moods = Object.keys(VIDEOGAME_PERSONALITIES);
  for (let i = 0; i < count; i++) {
    let pos = null;
    for (let a = 0; a < 60 && !pos; a++) {
      const horiz = Math.random() < 0.5;
      const line = -HALF + Math.floor(Math.random() * (GRID + 1)) * S;
      const along = rand(-HALF + 6, HALF - 6);
      const lat = rand(-ROAD / 2 + 2, ROAD / 2 - 2);
      const cx = horiz ? along : line + lat;
      const cz = horiz ? line + lat : along;
      if (farEnough(cx, cz) && !world.hitsBuilding({ x: cx, z: cz }, 0.7)) pos = { x: cx, z: cz };
    }
    if (!pos) continue;
    const mood = pick(moods);
    const human = randomHuman({ skin: pick(SKINS), hair: pick(HAIRS), hairStyle: pick(HAIR_STYLES), shirt: pick(SHIRTS), pants: pick(PANTS), mood });
    human.mood = mood;
    human.group.position.set(pos.x, 0, pos.z);
    human.root.rotation.y = Math.random() * Math.PI * 2;
    human.mode = 'walk';
    human.speed01 = 0.6;
    human.wander = { dir: Math.random() * Math.PI * 2, turnT: rand(1.5, 5), nearT: rand(1, 7) };
    scene.add(human.group);
    humans.push(human);
  }
}

function updateRadio() {
  const r = pick(VIDEOGAME_RADIO);
  radioStation.textContent = r.st;
  radioTrack.textContent = r.tr;
}

function showMission(text) { missionText.textContent = text; missionBox.classList.add('show'); }
function hideMission() { missionBox.classList.remove('show'); }

function setMoney(bump = false) {
  moneyEl.textContent = `$${money.toLocaleString('en-US')}`;
  if (bump) { moneyEl.classList.remove('bump'); void moneyEl.offsetWidth; moneyEl.classList.add('bump'); }
}
function setWantedStars() { starEls.forEach((s, i) => s.classList.toggle('on', i < wantedLevel)); }
function addWanted(n = 1) {
  wantedLevel = Math.min(5, wantedLevel + n);
  wantedT = 0;
  setWantedStars();
  showToast('★ WANTED LEVEL ' + wantedLevel + ' ★');
}
function flashVignette() {
  vignette.classList.add('hit');
  setTimeout(() => vignette.classList.remove('hit'), 260);
}
function showWasted() { wastedEl.classList.add('show'); setTimeout(() => wastedEl.classList.remove('show'), 2400); }
function wasted() {
  showWasted();
  money = Math.max(0, money - 100);
  setMoney(true);
  playerHealth = 100; armor = 0; wantedLevel = 0; wantedT = 0;
  setWantedStars();
  if (onFoot) exitFoot(true);
  playerVehicle.dead = false; playerVehicle.health = 100; playerVehicle.speed = 0;
  playerVehicle.vel.set(0, 0, 0); playerVehicle.pos.set(0, 0, 0);
  playerVehicle.group.position.set(0, 0, 0); playerVehicle.heading = 0;
  playerVehicle.group.rotation.y = 0; playerVehicle.model.under.visible = true;
}

function honk() {
  try {
    audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    const t = audioCtx.currentTime;
    const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
    o.type = 'square'; o.frequency.setValueAtTime(415, t); o.frequency.setValueAtTime(523, t + 0.1);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.14, t + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.5);
    o.connect(g); g.connect(audioCtx.destination); o.start(t); o.stop(t + 0.55);
  } catch (e) {}
}

function showToast(text) {
  toast.textContent = text;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
}
function setPrompt(text) {
  if (!promptEl) return;
  if (text) { promptEl.textContent = text; promptEl.classList.remove('hidden'); }
  else { promptEl.classList.add('hidden'); }
}

function triggerPedestrianInteraction(human, interactionType) {
  if (subCooldown > 0) return;
  const p = VIDEOGAME_PERSONALITIES[human.mood] || VIDEOGAME_PERSONALITIES.chill;
  let text = interactionType === 'small' ? pick(p.small) : (p.big ? pick(p.big) : pick(p.small));
  if (text) {
    subCooldown = 4.5;
    subName.textContent = p.name; subText.textContent = text;
    subtitleEl.classList.remove('hidden');
    clearTimeout(subTimer);
    subTimer = setTimeout(() => subtitleEl.classList.add('hidden'), 5000);
  }
}

function toggleVehicle() {
  if (gameState !== 'playing') return;
  if (onFoot) {
    const dx = player.group.position.x - playerVehicle.pos.x;
    const dz = player.group.position.z - playerVehicle.pos.z;
    if (dx * dx + dz * dz < 49) exitFoot(); else setPrompt('');
  } else { enterFoot(); }
}
function enterFoot() {
  if (onFoot || !playerVehicle) return;
  if (Math.abs(playerVehicle.speed) > 9) { showToast('⚠ SLOW DOWN FIRST'); return; }
  onFoot = true;
  playerVehicle.occupied = false;
  playerVehicle.speed = 0; playerVehicle.vel.set(0, 0, 0);
  const h = playerVehicle.heading;
  player.group.position.set(playerVehicle.pos.x + Math.cos(h) * 2.6, 0, playerVehicle.pos.z - Math.sin(h) * 2.6);
  world.resolve(player.group.position, 0.45);
  player.group.visible = true;
  player.root.rotation.y = h;
  playerVy = 0; mouse.x = h;
  gearLabel.textContent = 'ON FOOT';
  showToast('ON FOOT — press F near a car to drive');
}
function exitFoot(silent = false) {
  if (!onFoot || !playerVehicle) return;
  onFoot = false;
  player.group.visible = false;
  playerVehicle.occupied = true;
  mouse.x = playerVehicle.heading;
  gearLabel.textContent = 'DRIVE';
  if (!silent) showToast('BACK IN THE RIDE');
}

function playerPunch() {
  if (!player || player.punchCD > 0) return;
  player.startPunch();
  const p = player.group.position;
  const fx = Math.sin(player.root.rotation.y), fz = Math.cos(player.root.rotation.y);
  for (const h of humans) {
    if (h.dead) continue;
    const dx = h.group.position.x - p.x;
    const dz = h.group.position.z - p.z;
    const d2 = dx * dx + dz * dz;
    if (d2 > 6.5) continue;
    const dist = Math.sqrt(d2) || 1;
    if ((dx * fx + dz * fz) / dist < 0.25) continue;
    runOverPedestrian(h, '👊 ');
    break;
  }
}
function runOverPedestrian(h, prefix = '💀 ') {
  h.dead = true;
  vfx.bloodMist(new THREE.Vector3(h.group.position.x, 1.0, h.group.position.z), 16);
  triggerPedestrianInteraction(h, 'big');
  addWanted(1);
  showToast(prefix + 'HIT AND RUN');
}

function updateDriving(dt) {
  const input = {
    throttle: keys.W ? 1 : 0,
    brake: keys.S ? 1 : 0,
    steer: (keys.A ? 1 : 0) - (keys.D ? 1 : 0),
    handbrake: !!keys.Space,
  };
  playerVehicle.maxSpeed = keys.Shift ? 54 : 42;
  playerVehicle.update(dt, input, world, vfx);

  // Speed lines / motion streaks at high speed
  if (vfx && Math.abs(playerVehicle.speed) > 22) {
    const v = playerVehicle;
    const back = new THREE.Vector3(-Math.sin(v.heading), 0, -Math.cos(v.heading));
    for (let i = 0; i < 2; i++) {
      vfx.exhaust(new THREE.Vector3(v.pos.x + back.x * 2 + (Math.random()-0.5)*1.2, 0.6, v.pos.z + back.z * 2 + (Math.random()-0.5)*1.2), { x: Math.sin(v.heading), z: Math.cos(v.heading) });
    }
  }
}

function updateOnFoot(dt) {
  const camYaw = mouse.x;
  const fx = Math.sin(camYaw), fz = Math.cos(camYaw);
  const rx = -Math.cos(camYaw), rz = Math.sin(camYaw);
  let mx = 0, mz = 0;
  if (keys.W) { mx += fx; mz += fz; }
  if (keys.S) { mx -= fx; mz -= fz; }
  if (keys.D) { mx += rx; mz += rz; }
  if (keys.A) { mx -= rx; mz -= rz; }
  const len = Math.hypot(mx, mz);
  footMoving = len > 0.01;
  sprinting = footMoving && keys.Shift && stamina > 1;
  if (footMoving) {
    const speed = sprinting ? 7.4 : 3.9;
    const p = player.group.position;
    p.x += (mx / len) * speed * dt;
    p.z += (mz / len) * speed * dt;
    world.resolve(p, 0.45);
    player.root.rotation.y = dampAngle(player.root.rotation.y, Math.atan2(mx, mz), 14, dt);
    if (sprinting) stamina = Math.max(0, stamina - 19 * dt);
  }
  if (keys.Space && player.group.position.y <= 0.01) playerVy = 6.6;
  playerVy -= 20 * dt;
  player.group.position.y += playerVy * dt;
  if (player.group.position.y < 0) { player.group.position.y = 0; playerVy = 0; }
  player.update(dt, { mode: footMoving ? 'walk' : 'idle', speed: footMoving ? (sprinting ? 1 : 0.6) : 0, moving: footMoving });
  if (footMoving && performance.now() - mouse.lastMove > 1600) {
    mouse.x = dampAngle(mouse.x, player.root.rotation.y, 1.8, dt);
  }
}

function updateHumans(dt) {
  const ref = onFoot ? player.group.position : (playerVehicle ? playerVehicle.pos : null);
  for (const h of humans) {
    if (h.dead) { h.update(dt, {}); continue; }
    const w = h.wander;
    w.turnT -= dt;
    if (w.turnT <= 0) { w.turnT = rand(1.6, 5); w.dir += rand(-1.4, 1.4); }
    const sp = 1.5;
    const nx = h.group.position.x + Math.sin(w.dir) * sp * dt;
    const nz = h.group.position.z + Math.cos(w.dir) * sp * dt;
    const tmp = { x: nx, z: nz };
    world.resolve(tmp, 0.35);
    if (Math.abs(tmp.x - nx) + Math.abs(tmp.z - nz) > 0.03) w.dir += Math.PI * rand(0.4, 0.8);
    h.group.position.x = tmp.x;
    h.group.position.z = tmp.z;
    h.root.rotation.y = dampAngle(h.root.rotation.y, w.dir, 9, dt);
    h.update(dt, { mode: 'walk', speed: 0.55, moving: true });
    if (ref && subCooldown <= 0) {
      const dx = h.group.position.x - ref.x;
      const dz = h.group.position.z - ref.z;
      if (dx * dx + dz * dz < 400) {
        w.nearT -= dt;
        if (w.nearT <= 0) { w.nearT = rand(7, 16); triggerPedestrianInteraction(h, 'small'); }
      }
    }
  }
  if (!onFoot && playerVehicle && !playerVehicle.dead && Math.abs(playerVehicle.speed) > 5) {
    for (const h of humans) {
      if (h.dead) continue;
      const dx = h.group.position.x - playerVehicle.pos.x;
      const dz = h.group.position.z - playerVehicle.pos.z;
      if (dx * dx + dz * dz < 4.4) runOverPedestrian(h);
    }
  }
}

function placeCamera(tx, ty, tz, camYaw, dist, height, pitch) {
  const dirX = Math.sin(camYaw), dirZ = Math.cos(camYaw);
  let d = dist;
  for (let i = 0; i < 6; i++) {
    if (world.hitsBuilding({ x: tx - dirX * d, z: tz - dirZ * d }, 1.4)) d *= 0.72; else break;
  }
  camera.position.set(tx - dirX * d, Math.max(1.2, ty + height + pitch), tz - dirZ * d);
  camera.lookAt(tx, ty, tz);
}
function updateCamera(dt) {
  if (onFoot && player) {
    const p = player.group.position;
    placeCamera(p.x, p.y + 1.4, p.z, mouse.x, 7, 3.6, -mouse.y * 7);
  } else if (playerVehicle) {
    const v = playerVehicle;
    if (performance.now() - mouse.lastMove > 1400) mouse.x = dampAngle(mouse.x, v.heading, 2.4, dt);
    const spd = Math.abs(v.speed);
    placeCamera(v.pos.x, 1.5, v.pos.z, mouse.x, 11 + spd * 0.16, 5.2, -mouse.y * 9);
  }
}

function updateVitals(dt) {
  if (wantedLevel > 0) { wantedT += dt; if (wantedT > 24) { wantedLevel--; wantedT = 0; setWantedStars(); } } else { wantedT = 0; }
  if (playerHealth > 0 && playerHealth < 100) playerHealth = Math.min(100, playerHealth + 1.2 * dt);
  if (!sprinting) stamina = Math.min(100, stamina + 14 * dt);
  healthBar.style.width = `${clamp(playerHealth, 0, 100)}%`;
  armorBar.style.width = `${clamp(armor, 0, 100)}%`;
  staminaBar.style.width = `${clamp(stamina, 0, 100)}%`;
}
function updateHUD(dt) {
  updateVitals(dt);
  if (onFoot) { speedNum.textContent = '0'; gearLabel.textContent = 'ON FOOT'; }
  else if (playerVehicle) {
    speedNum.textContent = Math.round(Math.abs(playerVehicle.speed) * 3.6);
    gearLabel.textContent = playerVehicle.speed > 0.5 ? 'DRIVE' : playerVehicle.speed < -0.5 ? 'REVERSE' : 'NEUTRAL';
  }
  if (onFoot) {
    const dx = player.group.position.x - playerVehicle.pos.x;
    const dz = player.group.position.z - playerVehicle.pos.z;
    setPrompt(dx * dx + dz * dz < 49 ? 'F — ENTER VEHICLE' : '');
  } else { setPrompt('F — EXIT VEHICLE'); }
}

function updateMission(dt) {
  if (missionIndex >= MISSIONS.length) return;
  const m = MISSIONS[missionIndex];
  if (missionBeam && missionBeam.visible) {
    missionBeam.rotation.y += dt * 1.2;
    const s = 1 + Math.sin(performance.now() * 0.004) * 0.06;
    missionBeam.scale.set(s, 1, s);
  }
  if (onFoot) return;
  const dx = playerVehicle.pos.x - m.target.x;
  const dz = playerVehicle.pos.z - m.target.z;
  if (dx * dx + dz * dz > 49) return;
  money += m.reward; setMoney(true);
  vfx.flash(new THREE.Vector3(m.target.x, 2, m.target.z), 20, [0.3, 1, 0.65], 0.55);
  vfx.sparks(new THREE.Vector3(m.target.x, 1, m.target.z), 30, [0.3, 1, 0.65]);
  showToast(`✓ MISSION PASSED  +$${m.reward.toLocaleString('en-US')}`);
  missionIndex++;
  if (missionIndex < MISSIONS.length) {
    showMission(MISSIONS[missionIndex].text);
    missionBeam.position.set(MISSIONS[missionIndex].target.x, 0, MISSIONS[missionIndex].target.z);
    missionBeam.visible = true;
  } else {
    missionComplete = true; hideMission(); missionBeam.visible = false;
    showToast('🏆 YOU OWN VICE NEON');
  }
}

const MM_S = 200 / 760;
const mmX = (x) => (x + 360) * MM_S;
const mmZ = (z) => (z + 380) * MM_S;
let mmStatic = null;
function buildMinimap() {
  mmStatic = document.createElement('canvas');
  mmStatic.width = 200; mmStatic.height = 200;
  const g = mmStatic.getContext('2d');
  g.fillStyle = '#07060f'; g.fillRect(0, 0, 200, 200);
  g.fillStyle = '#8a7440'; g.fillRect(mmX(HALF), 0, mmX(HALF + 46) - mmX(HALF), 200);
  g.fillStyle = '#0d2f52'; g.fillRect(mmX(HALF + 46), 0, 200 - mmX(HALF + 46), 200);
  const blockSize = (S - ROAD) * MM_S;
  for (const b of world.blocks) {
    g.fillStyle = b.type === 'park' ? '#1f5a35' : b.type === 'plaza' ? '#3a3552' : '#171c30';
    g.fillRect(mmX(b.cx) - blockSize / 2, mmZ(b.cz) - blockSize / 2, blockSize, blockSize);
  }
  g.strokeStyle = '#4a4f66'; g.lineWidth = Math.max(2, ROAD * MM_S); g.beginPath();
  for (let i = 0; i <= GRID; i++) {
    const line = -HALF + i * S;
    g.moveTo(mmX(line), 0); g.lineTo(mmX(line), 200);
    g.moveTo(0, mmZ(line)); g.lineTo(200, mmZ(line));
  }
  g.stroke();
}
function drawMinimap() {
  if (!mctx || !mmStatic) return;
  mctx.drawImage(mmStatic, 0, 0);
  mctx.fillStyle = 'rgba(255,255,255,.5)';
  for (const h of humans) {
    if (h.dead) continue;
    mctx.fillRect(mmX(h.group.position.x) - 1, mmZ(h.group.position.z) - 1, 2, 2);
  }
  if (missionIndex < MISSIONS.length && missionBeam && missionBeam.visible) {
    const t = MISSIONS[missionIndex].target;
    const pulse = 4 + Math.sin(performance.now() * 0.006) * 1.6;
    mctx.beginPath(); mctx.arc(mmX(t.x), mmZ(t.z), pulse, 0, Math.PI * 2);
    mctx.fillStyle = '#2ee6ff'; mctx.fill();
    mctx.strokeStyle = 'rgba(46,230,255,.65)'; mctx.lineWidth = 1.5; mctx.stroke();
  }
  if (onFoot || playerVehicle) {
    const px = onFoot ? player.group.position.x : playerVehicle.pos.x;
    const pz = onFoot ? player.group.position.z : playerVehicle.pos.z;
    const ph = onFoot ? player.root.rotation.y : playerVehicle.heading;
    mctx.save(); mctx.translate(mmX(px), mmZ(pz)); mctx.rotate(Math.PI - ph);
    mctx.beginPath(); mctx.moveTo(0, -6.5); mctx.lineTo(4.4, 5); mctx.lineTo(0, 2.6); mctx.lineTo(-4.4, 5);
    mctx.closePath(); mctx.fillStyle = onFoot ? '#ffffff' : '#ff2e88'; mctx.fill();
    mctx.strokeStyle = 'rgba(0,0,0,.75)'; mctx.lineWidth = 1.2; mctx.stroke();
    mctx.restore();
  }
}

function handleKeyPress(k) {
  if (gameState !== 'playing') return;
  if (k === 'F') toggleVehicle();
  else if (k === 'H') honk();
  else if (k === 'R') { updateRadio(); showToast('📻 ' + radioStation.textContent); }
}
function keyName(e) {
  if (e.code === 'Space') return 'Space';
  if (e.code && e.code.startsWith('Key')) return e.code.slice(3);
  if (e.code && e.code.startsWith('Arrow')) return e.code.slice(5);
  if (e.key && e.key.length === 1) return e.key.toUpperCase();
  return e.key;
}
window.addEventListener('keydown', (e) => {
  const k = keyName(e);
  if (e.code === 'Space') { keys.Space = true; e.preventDefault(); }
  if (k === 'Escape') { togglePause(); return; }
  if (k in keys) { if (!keys[k]) handleKeyPress(k); keys[k] = true; }
});
window.addEventListener('keyup', (e) => {
  const k = keyName(e);
  if (e.code === 'Space') keys.Space = false;
  if (k in keys) keys[k] = false;
});
function togglePause() {
  if (gameState === 'playing') { gameState = 'paused'; pauseScreen.classList.remove('hidden'); if (document.pointerLockElement) document.exitPointerLock(); }
  else if (gameState === 'paused') { gameState = 'playing'; pauseScreen.classList.add('hidden'); lastTime = performance.now(); }
}
canvas.addEventListener('click', () => { if (!mouse.locked) canvas.requestPointerLock(); });
document.addEventListener('pointerlockchange', () => { mouse.locked = document.pointerLockElement === canvas; });
canvas.addEventListener('mousemove', (e) => {
  if (!mouse.locked) return;
  mouse.x += e.movementX * 0.003; mouse.y -= e.movementY * 0.003;
  mouse.y = clamp(mouse.y, -0.5, 0.5); mouse.lastMove = performance.now();
});
document.addEventListener('mousedown', (e) => {
  if (e.button !== 0) return; keys.LMB = true;
  if (gameState === 'playing' && onFoot) playerPunch();
});
document.addEventListener('mouseup', (e) => { if (e.button === 0) keys.LMB = false; });

let lastTime = 0;
function gameLoop(timestamp) {
  requestAnimationFrame(gameLoop);
  const dt = Math.min(0.05, (timestamp - lastTime) / 1000);
  lastTime = timestamp;
  if (gameState !== 'playing') { renderer.render(scene, camera); return; }
  if (vfx) { vfx.update(dt); vfx.updateDecals(dt); }
  if (world) {
    world.update(dt);
    const t = (performance.now() * 0.00005) % 1;
    const sun = world.sun;
    if (sun) {
      const angle = t * Math.PI * 2;
      sun.position.set(Math.cos(angle) * 200, 60 + Math.sin(angle) * 40, Math.sin(angle) * 200);
      const day = Math.max(0, Math.sin(angle));
      sun.intensity = 1.2 + day * 1.6;
      sun.color.setRGB(1, 0.7 + day * 0.25, 0.45 + day * 0.4);
      if (scene.fog) scene.fog.color.setRGB(0.95 - day * 0.2, 0.55 - day * 0.1, 0.35 + day * 0.1);
    }
  }
  if (subCooldown > 0) subCooldown -= dt;
  if (playerVehicle) updateDriving(dt);
  if (onFoot) updateOnFoot(dt);
  updateHumans(dt);
  updateCamera(dt);
  updateMission(dt);
  updateHUD(dt);
  drawMinimap();
  renderer.render(scene, camera);
}

startBtn.addEventListener('click', () => initGame());
window.addEventListener('keydown', (e) => { if (e.code === 'Enter' && gameState !== 'playing') { e.preventDefault(); initGame(); } });
resumeBtn.addEventListener('click', () => togglePause());