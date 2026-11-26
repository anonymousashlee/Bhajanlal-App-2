---
name: free-upstream-limit-permanent-fix
description: Use when preventing 'free upstream limit reached' errors permanently by disabling free tier, preferring local model, and connecting paid providers.
---

# free-upstream-limit-permanent-fix

Part of the **Bhajanlal** model-building skill library. Pillar: 109. Reliability & Upstream Fallback (1 skill)

Use when preventing 'free upstream limit reached' errors permanently by disabling free tier, preferring local model, and connecting paid providers.

## Workflow

1. Set BHAJANLAL_DISABLE_FREE_UPSTREAM=1 to stop calling the exhausted free tier.
2. Set BHAJANLAL_PREFER_LOCAL=1 to route to the local Bhajanlal model first.
3. Optionally connect a paid provider via BHAJANLAL_MIMO_API_KEY / BHAJANLAL_MINIMAX_API_KEY.
4. Increase BHAJANLAL_CACHE_TTL and BHAJANLAL_CACHE_MAX to reduce upstream calls.
5. Restart the backend; verify /health and run a chat request.

## Output

Reliable, free-limit-free operation using local + paid providers.
