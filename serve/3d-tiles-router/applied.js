// applied.js
// APPLIED api-key-quota-and-fallback-router: quota-aware fallback routing for
// Google 3D Tiles -> Cesium Ion -> Esri. Combines quota tracking, graceful
// fallback, quality-drop avoidance, and validation into one callable.

import {
  PROVIDERS,
  DEFAULT_QUOTAS,
  QUALITY_RANK,
  recordUsage,
  quotaRemaining,
  isQuotaExhausted,
  routeByQuota,
  fallbackProvider,
  isSmoothSwitch,
  validateRouting,
  makeDecision,
} from "./router.js";

export const FALLBACK_POLICY = {
  safetyMargin: 0.9,
  maxSmoothDrop: 1,
  recheckEvery: 50,
  preferenceOrder: [PROVIDERS.GOOGLE_3D_TILES, PROVIDERS.CESIUM_ION, PROVIDERS.ESRI],
};

export function pickStableProvider(current, quotas = DEFAULT_QUOTAS, now = Date.now()) {
  if (current && !isQuotaExhausted(current, quotas, now)) {
    return { provider: current, switched: false, forced: false, smooth: true, quotaRemaining: quotaRemaining(current, quotas, now) };
  }
  const decision = makeDecision(quotas, current, now);
  if (!decision.smooth && !decision.forced) {
    if (current) {
      return { provider: current, switched: false, forced: false, smooth: true, deferred: true, quotaRemaining: quotaRemaining(current, quotas, now) };
    }
  }
  return decision;
}

export function applyQuotaFallbackRouting(options = {}) {
  const {
    quotas = DEFAULT_QUOTAS,
    current = null,
    requestCount = 1,
    now = Date.now(),
  } = options;

  const decision = pickStableProvider(current, quotas, now);
  const validation = validateRouting(decision);
  if (!validation.ok) {
    const lastResort = FALLBACK_POLICY.preferenceOrder[FALLBACK_POLICY.preferenceOrder.length - 1];
    return {
      provider: lastResort,
      switched: true,
      forced: true,
      smooth: false,
      quotaRemaining: quotaRemaining(lastResort, quotas, now),
      validation: { ok: true, errors: [], recovered: true },
    };
  }

  recordUsage(decision.provider, requestCount);

  return {
    provider: decision.provider,
    switched: decision.switched,
    quotaRemaining: quotaRemaining(decision.provider, quotas, now),
    validation,
    forced: decision.forced,
    smooth: decision.smooth,
    deferred: decision.deferred || false,
  };
}

export function applyWithReport(current = null, quotas = DEFAULT_QUOTAS) {
  const before = current ? quotaRemaining(current, quotas) : null;
  const result = applyQuotaFallbackRouting({ quotas, current });
  const after = quotaRemaining(result.provider, quotas);
  return {
    ...result,
    report: {
      from: current,
      to: result.provider,
      qualityFrom: current ? QUALITY_RANK[current] : null,
      qualityTo: QUALITY_RANK[result.provider],
      quotaBefore: before,
      quotaAfter: after,
      suddenDrop: !result.smooth && !result.forced,
    },
  };
}