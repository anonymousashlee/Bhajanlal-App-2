// adsb-ais-dead-reckoning-applied.js
// APPLIED adsb-ais-dead-reckoning-smoother: full pipeline for ADS-B (aircraft)
// and AIS (vessel) tracks. Combines dead reckoning, position interpolation,
// movement smoothing, and validation into one callable module.
//
// Units (SI, internally):
//   lat/lon : degrees (WGS84)
//   alt     : meters
//   speed   : meters/second (helpers convert knots <-> m/s)
//   course  : degrees true (0..360)
//   ts      : milliseconds (epoch)
//
// Usage:
//   import { createTrackSmoother } from './adsb-ais-dead-reckoning-applied.js';
//   const smoother = createTrackSmoother({ alpha: 0.35, maxJumpM: 5000 });
//   smoother.ingest(ping);          // on every transponder ping
//   const pos = smoother.tick(id, now); // call on render frame (e.g. 60 Hz)

const EARTH_RADIUS_M = 6371000;
const KNOTS_TO_MS = 0.514444;
const DEG2RAD = Math.PI / 180;
const RAD2DEG = 180 / Math.PI;

function toRad(d) { return d * DEG2RAD; }
function toDeg(r) { return r * RAD2DEG; }
function normCourse(c) { return ((c % 360) + 360) % 360; }

// ---- Step 1: Dead reckoning ----
// Predict a new lat/lon given a starting point, speed (m/s), course (deg) and
// elapsed time (seconds). Uses the standard spherical great-circle formula.
export function deadReckon(start, speedMs, courseDeg, dtSec) {
  if (!start || !Number.isFinite(start.lat) || !Number.isFinite(start.lon)) {
    throw new Error('deadReckon: invalid start position');
  }
  const dist = speedMs * dtSec;                 // meters traveled
  const brng = toRad(normCourse(courseDeg));
  const lat1 = toRad(start.lat);
  const lon1 = toRad(start.lon);
  const angDist = dist / EARTH_RADIUS_M;

  const lat2 = Math.asin(
    Math.sin(lat1) * Math.cos(angDist) +
    Math.cos(lat1) * Math.sin(angDist) * Math.cos(brng)
  );
  const lon2 = lon1 + Math.atan2(
    Math.sin(brng) * Math.sin(angDist) * Math.cos(lat1),
    Math.cos(angDist) - Math.sin(lat1) * Math.sin(lat2)
  );

  return {
    lat: toDeg(lat2),
    lon: toDeg(lon2),
    alt: Number.isFinite(start.alt) ? start.alt : 0,
  };
}

// Great-circle distance in meters between two lat/lon points.
export function haversineM(a, b) {
  const lat1 = toRad(a.lat), lat2 = toRad(b.lat);
  const dLat = toRad(b.lat - a.lat);
  const dLon = toRad(b.lon - a.lon);
  const h = Math.sin(dLat / 2) ** 2 +
            Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
  return 2 * EARTH_RADIUS_M * Math.asin(Math.sqrt(h));
}

// ---- Step 2: Interpolation ----
// Smoothly move from `from` toward `to` over `durationMs`, returning the
// interpolated position at progress t in [0,1]. Uses ease-in-out cubic so
// transitions never snap.
export function interpolatePosition(from, to, t) {
  const tc = Math.max(0, Math.min(1, t));
  const ease = tc < 0.5 ? 4 * tc * tc * tc : 1 - Math.pow(-2 * tc + 2, 3) / 2;
  return {
    lat: from.lat + (to.lat - from.lat) * ease,
    lon: from.lon + (to.lon - from.lon) * ease,
    alt: from.alt + ((to.alt ?? from.alt) - from.alt) * ease,
  };
}

// ---- Step 3: Smoothing ----
// Exponential (low-pass) smoothing for scalar values such as speed/course.
export function smoothScalar(prev, next, alpha) {
  if (!Number.isFinite(prev)) return next;
  if (!Number.isFinite(next)) return prev;
  return prev + (next - prev) * alpha;
}

// Smooth a 2D course with proper wrap-around (shortest angular path).
export function smoothCourse(prev, next, alpha) {
  if (!Number.isFinite(prev)) return normCourse(next);
  let diff = normCourse(next) - normCourse(prev);
  if (diff > 180) diff -= 360;
  if (diff < -180) diff += 360;
  return normCourse(prev + diff * alpha);
}

// ---- Step 4: Validation ----
export function validatePing(ping) {
  const errors = [];
  if (!ping || typeof ping !== 'object') { errors.push('ping is not an object'); return { ok: false, errors }; }
  if (!Number.isFinite(ping.lat) || ping.lat < -90 || ping.lat > 90) errors.push('invalid lat');
  if (!Number.isFinite(ping.lon) || ping.lon < -180 || ping.lon > 180) errors.push('invalid lon');
  if (!Number.isFinite(ping.ts)) errors.push('invalid ts');
  if (ping.speed != null && !Number.isFinite(ping.speed)) errors.push('invalid speed');
  if (ping.course != null && !Number.isFinite(ping.course)) errors.push('invalid course');
  if (ping.alt != null && !Number.isFinite(ping.alt)) errors.push('invalid alt');
  return { ok: errors.length === 0, errors };
}

export function validateTrack(track) {
  const errors = [];
  if (!track) { errors.push('null track'); return { ok: false, errors }; }
  if (!Number.isFinite(track.lat) || !Number.isFinite(track.lon)) errors.push('non-finite position');
  if (!Number.isFinite(track.ts)) errors.push('non-finite ts');
  if (track.speed != null && (track.speed < 0 || track.speed > 400)) errors.push('speed out of range (m/s)');
  return { ok: errors.length === 0, errors };
}

// ---- Track smoother (stateful) ----
export function createTrackSmoother(opts = {}) {
  const {
    alpha = 0.3,            // position smoothing factor per tick
    speedAlpha = 0.25,      // speed smoothing factor
    courseAlpha = 0.2,      // course smoothing factor
    maxJumpM = 10000,       // reject pings that teleport beyond this
    catchupMs = 1500,       // ms to blend predicted->actual on new ping
    maxStaleMs = 120000,    // drop tracks stale longer than this
  } = opts;

  const tracks = new Map(); // id -> track state

  function ingest(ping) {
    const v = validatePing(ping);
    if (!v.ok) return { ok: false, errors: v.errors };

    const id = ping.id ?? ping.icao ?? ping.mmsi;
    if (id == null) return { ok: false, errors: ['missing id'] };

    const now = ping.ts;
    const speedMs = (ping.speedUnit === 'knots' || ping.speedKnots != null)
      ? (ping.speedKnots ?? ping.speed) * KNOTS_TO_MS
      : (ping.speed ?? 0); // assume m/s if no unit hint

    const existing = tracks.get(id);

    if (!existing) {
      const tr = {
        id,
        lat: ping.lat, lon: ping.lon, alt: ping.alt ?? 0,
        speed: speedMs, course: normCourse(ping.course ?? 0),
        ts: now,
        lastPingTs: now,
        target: null,        // blend target on new ping
        blendStart: null,
        blendFrom: null,
        stale: false,
      };
      tracks.set(id, tr);
      return { ok: true, track: tr, created: true };
    }

    // Reject teleport pings
    const predicted = deadReckon(existing, existing.speed, existing.course, (now - existing.ts) / 1000);
    const jump = haversineM(predicted, { lat: ping.lat, lon: ping.lon, alt: ping.alt ?? 0 });
    if (jump > maxJumpM) {
      // Soft reset: accept but flag
      existing.lat = ping.lat; existing.lon = ping.lon; existing.alt = ping.alt ?? existing.alt;
      existing.speed = speedMs; existing.course = normCourse(ping.course ?? existing.course);
      existing.ts = now; existing.lastPingTs = now;
      existing.target = null;
      return { ok: true, track: existing, reset: true, jumpM: jump };
    }

    // Set blend target: smoothly move from current predicted position to actual ping
    existing.blendFrom = { lat: existing.lat, lon: existing.lon, alt: existing.alt };
    existing.target = { lat: ping.lat, lon: ping.lon, alt: ping.alt ?? existing.alt };
    existing.blendStart = now;
    existing.blendDuration = catchupMs;
    // Smooth speed/course toward reported values
    existing.speed = smoothScalar(existing.speed, speedMs, speedAlpha);
    existing.course = smoothCourse(existing.course, ping.course ?? existing.course, courseAlpha);
    existing.lastPingTs = now;
    // ts stays as "last render time" updated in tick(); store ping ts
    existing.lastPingWall = now;
    return { ok: true, track: existing, updated: true, jumpM: jump };
  }

  function tick(id, now) {
    const tr = tracks.get(id);
    if (!tr) return null;

    // Drop stale
    if (now - tr.lastPingTs > maxStaleMs) {
      tr.stale = true;
    }

    // Dead-reckon forward from last render ts
    const dtSec = Math.max(0, (now - tr.ts) / 1000);
    // Base predicted position from speed/course
    let pos = deadReckon({ lat: tr.lat, lon: tr.lon, alt: tr.alt }, tr.speed, tr.course, dtSec);

    // Apply blend toward target if active
    if (tr.target && tr.blendStart != null) {
      const elapsed = now - tr.blendStart;
      const t = Math.min(1, elapsed / tr.blendDuration);
      pos = interpolatePosition(tr.blendFrom, tr.target, t);
      if (t >= 1) {
        tr.target = null;
        tr.blendStart = null;
      }
    }

    // Low-pass smooth position
    const newPos = {
      lat: smoothScalar(tr.lat, pos.lat, alpha),
      lon: smoothScalar(tr.lon, pos.lon, alpha),
      alt: smoothScalar(tr.alt, pos.alt, alpha),
    };

    tr.lat = newPos.lat; tr.lon = newPos.lon; tr.alt = newPos.alt;
    tr.ts = now;

    const out = { id: tr.id, lat: tr.lat, lon: tr.lon, alt: tr.alt,
                  speed: tr.speed, course: tr.course, ts: now, stale: tr.stale };
    const v = validateTrack(out);
    if (!v.ok) {
      // Roll back to last good by re-dead-reckoning without smoothing
      return { ...out, valid: false, errors: v.errors };
    }
    return { ...out, valid: true };
  }

  function tickAll(now) {
    const out = [];
    for (const id of tracks.keys()) out.push(tick(id, now));
    return out;
  }

  function remove(id) { tracks.delete(id); }
  function get(id) { return tracks.get(id) ?? null; }
  function size() { return tracks.size; }

  return { ingest, tick, tickAll, remove, get, size, deadReckon, haversineM };
}

// Convenience: convert knots to m/s
export function knotsToMs(k) { return k * KNOTS_TO_MS; }
export function msToKnots(m) { return m / KNOTS_TO_MS; }

// Self-test (run: node adsb-ais-dead-reckoning-applied.js)
if (typeof process !== 'undefined' && process.argv && process.argv[1] && process.argv[1].endsWith('adsb-ais-dead-reckoning-applied.js')) {
  const s = createTrackSmoother();
  const p0 = { id: 'ABC123', lat: 51.5, lon: -0.1, alt: 10000, speed: 250, speedUnit: 'knots', course: 90, ts: 1000 };
  console.log('ingest0', s.ingest(p0));
  // dead reckon 5s
  const r = s.tick('ABC123', 6000);
  console.log('tick', r);
  // new ping
  const p1 = { id: 'ABC123', lat: 51.501, lon: -0.095, alt: 10000, speed: 245, speedUnit: 'knots', course: 92, ts: 6000 };
  console.log('ingest1', s.ingest(p1));
  const r2 = s.tick('ABC123', 7500);
  console.log('tick2', r2);
  // validation tests
  console.log('validatePing bad', validatePing({ lat: 200, lon: 0, ts: 1 }));
  console.log('deadReckon', deadReckon({ lat: 0, lon: 0, alt: 0 }, 10, 90, 10));
  console.log('haversine', haversineM({ lat: 0, lon: 0 }, { lat: 0, lon: 1 }));
  console.log('OK');
}
