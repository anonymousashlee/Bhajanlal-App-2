// router.js
// api-key-quota-and-fallback-router (applied): quota-aware fallback routing
// for Google 3D Tiles -> Cesium Ion -> Esri.
// Tracks per-provider request counts against daily quotas and routes tile
// requests to the highest-fidelity available provider, falling back
// gracefully without sudden quality drops.

export const PROVIDERS = Object.freeze({
  GOOGLE_3D_TILES: "google-3d-tiles",
  CESIUM_ION: "cesium-ion",
  ESRI: "esri",
});

export const DEFAULT_QUOTAS = Object.freeze({
  [PROVIDERS.GOOGLE_3D_TILES]: 25000,
  [PROVIDERS.CESIUM_ION]: 100000,
  [PROVIDERS.ESRI]: 1000000,
});

export const QUALITY_RANK = Object.freeze({
  [PROVIDERS.GOOGLE_3D_TILES]: 3,
  [PROVIDERS.CESIUM_ION]: 2,
  [PROVIDERS.ESRI]: 1,
});

const QUOTA_SAFETY_MARGIN = 0.9;
const usage = new Map();
const windowStart = new Map();

function windowKey(provider, now = Date.now()) {
  const d = new Date(now);
  return `${provider}:${d.getUTCFullYear()}-${d.getUTCMonth() + 1}-${d.getUTCDate()}`;
}

function currentUsage(provider, now = Date.now()) {
  const key = windowKey(provider, now);
  if (windowStart.get(provider) !== key) {
    windowStart.set(provider, key);
    usage.set(provider, 0);
  }
  return usage.get(provider) || 0;
}

export function recordUsage(provider, n = 1) {
  currentUsage(provider);
  const key = windowKey(provider);
  usage.set(provider, (usage.get(provider) || 0) + n);
}

export function quotaRemaining(provider, quotas = DEFAULT_QUOTAS, now = Date.now()) {
  const limit = (quotas[provider] || 0) * QUOTA_SAFETY_MARGIN;
  const used = currentUsage(provider, now);
  return Math.max(0, limit - used);
}

export function isQuotaExhausted(provider, quotas = DEFAULT_QUOTAS, now = Date.now()) {
  return quotaRemaining(provider, quotas, now) <= 0;
}

export function routeByQuota(quotas = DEFAULT_QUOTAS, now = Date.now()) {
  const candidates = Object.values(PROVIDERS)
    .filter((p) => !isQuotaExhausted(p, quotas, now))
    .sort((a, b) => QUALITY_RANK[b] - QUALITY_RANK[a]);
  return candidates.length ? candidates[0] : null;
}

export function fallbackProvider(current, quotas = DEFAULT_QUOTAS, now = Date.now()) {
  const currentRank = QUALITY_RANK[current] ?? 0;
  const available = Object.values(PROVIDERS)
    .filter((p) => p !== current && !isQuotaExhausted(p, quotas, now))
    .sort((a, b) => Math.abs(QUALITY_RANK[a] - currentRank) - Math.abs(QUALITY_RANK[b] - currentRank)
      || QUALITY_RANK[b] - QUALITY_RANK[a]);
  return available.length ? available[0] : null;
}

export function isSmoothSwitch(from, to, forced = false) {
  if (from === to) return true;
  if (forced) return true;
  const delta = Math.abs((QUALITY_RANK[from] ?? 0) - (QUALITY_RANK[to] ?? 0));
  return delta <= 1;
}

export function validateRouting(decision) {
  const errors = [];
  if (!decision) errors.push("no provider available");
  else {
    if (!Object.values(PROVIDERS).includes(decision.provider))
      errors.push("unknown provider: " + decision.provider);
    if (typeof decision.quotaRemaining !== "number")
      errors.push("missing quotaRemaining");
    if (decision.quotaRemaining < 0) errors.push("negative quotaRemaining");
  }
  return { ok: errors.length === 0, errors };
}

export function makeDecision(quotas = DEFAULT_QUOTAS, current = null, now = Date.now()) {
  if (current && !isQuotaExhausted(current, quotas, now)) {
    return { provider: current, quotaRemaining: quotaRemaining(current, quotas, now), switched: false, forced: false };
  }
  const forced = current !== null && isQuotaExhausted(current, quotas, now);
  let next = forced && current ? fallbackProvider(current, quotas, now) : routeByQuota(quotas, now);
  if (!next) next = routeByQuota(quotas, now);
  const smooth = current ? isSmoothSwitch(current, next, forced) : true;
  return { provider: next, quotaRemaining: next ? quotaRemaining(next, quotas, now) : 0, switched: next !== current, forced, smooth };
}