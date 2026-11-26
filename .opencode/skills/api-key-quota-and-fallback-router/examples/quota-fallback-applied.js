// quota-fallback-applied.js
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
} from "./quota-fallback-router.js";

// Step 2: fallback policy config. Tune thresholds per deployment.
export const FALLBACK_POLICY = {
  // Stop using a provider at this fraction of its quota (safety margin).
  safetyMargin: 0.9,
  // Max quality-tier drop allowed in a single switch without forcing.
  maxSmoothDrop: 1,
  // Number of tile requests to batch before re-evaluating quota.
  recheckEvery: 50,
  // Providers ordered by preference (highest quality first).
  preferenceOrder: [PROVIDERS.GOOGLE_3D_TILES, PROVIDERS.CESIUM_ION, PROVIDERS.ESRI],
};

// Step 3 helper: pick a provider that avoids a sudden quality drop when the
// current provider is healthy but we want to pre-emptively shed load.
export function pickStableProvider(current, quotas = DEFAULT_QUOTAS, now = Date.now()) {
  if (current && !isQuotaExhausted(current, quotas, now)) {
    return { provider: current, switched: false, forced: false, smooth: true, quotaRemaining: quotaRemaining(current, quotas, now) };
  }
  const decision = makeDecision(quotas, current, now);
  if (!decision.smooth && !decision.forced) {
    // Keep current lower-tier provider rather than a jarring jump.
    if (current) {
      return { provider: current, switched: false, forced: false, smooth: true, deferred: true, quotaRemaining: quotaRemaining(current, quotas, now) };
    }
  }
  return decision;
}

// Track requests and auto-route. Returns the provider to use for the next
// batch of tile requests.
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
    // Fall back to the lowest-quality (always-available) provider.
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

  // Record usage against the chosen provider.
  recordUsage(decision.provider, requestCount);

  return {
    provider: decision.provider,
    switched: decision.switched,
    forced: decision.forced,
    smooth: decision.smooth,
    deferred: decision.deferred || false,
    quotaRemaining: quotaRemaining(decision.provider, quotas, now),
    validation,
  };
}

// Convenience: full apply with a simulated "before/after" report for demos.
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

// Cesium usage:
//   import { applyQuotaFallbackRouting, PROVIDERS } from './quota-fallback-applied.js';
//   let currentProvider = PROVIDERS.GOOGLE_3D_TILES;
//   function loadTiles(count) {
//     const r = applyQuotaFallbackRouting({ current: currentProvider, requestCount: count });
//     currentProvider = r.provider;
//     switch (r.provider) {
//       case PROVIDERS.GOOGLE_3D_TILES:
//         viewer.terrainProvider = Cesium.createGooglePhotorealistic3DTileset({ key });
//         break;
//       case PROVIDERS.CESIUM_ION:
//         viewer.terrainProvider = await Cesium.createWorldTerrainAsync();
//         break;
//       case PROVIDERS.ESRI:
//         viewer.imageryLayers.addImageryProvider(new Cesium.ArcGisMapServerImageryProvider({...}));
//         break;
//     }
//     console.log('routed to', r.provider, 'remaining', r.quotaRemaining, 'smooth', r.smooth);
//   }
