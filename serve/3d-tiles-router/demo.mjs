import { PROVIDERS, DEFAULT_QUOTAS } from "./router.js";
import { applyQuotaFallbackRouting, applyWithReport } from "./applied.js";

console.log("=== api-key-quota-and-fallback-router demo ===");
let current = PROVIDERS.GOOGLE_3D_TILES;
console.log("start provider:", current);

// Normal: plenty of quota -> stays on Google.
let r = applyQuotaFallbackRouting({ current, requestCount: 100 });
current = r.provider;
console.log("after 100 req:", r.provider, "remaining", r.quotaRemaining, "switched", r.switched, "smooth", r.smooth);

// Exhaust Google quota (25000 * 0.9 = 22500 effective). Record the rest.
const googleLimit = DEFAULT_QUOTAS[PROVIDERS.GOOGLE_3D_TILES] * 0.9;
// Simulate by recording usage up to limit via a fresh router state is not possible (module state).
// Instead, drive many batches until exhausted.
let batches = 0;
while (!r.quotaRemaining || r.provider === PROVIDERS.GOOGLE_3D_TILES) {
  r = applyQuotaFallbackRouting({ current, requestCount: 5000 });
  current = r.provider;
  batches++;
  console.log(`batch ${batches}:`, r.provider, "remaining", r.quotaRemaining, "switched", r.switched, "forced", r.forced, "smooth", r.smooth);
  if (batches > 10) break;
}

console.log("\nfinal provider:", current);
console.log("report:", JSON.stringify(applyWithReport(current), null, 2).slice(0, 400));