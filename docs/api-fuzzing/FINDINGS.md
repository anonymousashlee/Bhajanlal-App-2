# API Fuzzing (Nuclei) - Findings

Target: Bhajanlal Serve Gateway (serve/backend.py v2.2.0), base http://127.0.0.1:8799

## Technique
1. Parse API surface (OpenAPI spec derived from aiohttp route table in serve/backend.py).
2. Generate Nuclei YAML templates per endpoint (docs/api-fuzzing/nuclei-templates/).
3. Run fuzzing against live backend.
4. Triage findings.

## Probe summary (29 probes)
- /v1/train/run: accepts arbitrary `stage` strings and returns 202 "started"; stage validated downstream by argparse choices in train/auto_train.py (invalid stage -> subprocess exits non-zero). No shell injection (subprocess_exec + argv). Risk: unauthenticated subprocess spawn / resource exhaustion (DoS). No rate limit.
- /v1/chat/completions: type confusion handled (messages non-list -> 400). model=null silently defaults to compiled model. Prompt-injection payloads echoed but no evidence of system-prompt leakage in response. Stream/non-stream both 200.
- /v1/skills: q/id/limit injection attempts return 404 or filtered results; no path traversal file read. limit not capped server-side but search bounds results.
- /v1/media/generations: requires media model; url field forwarded to upstream only after model validation; no SSRF reached in tested config (minimax disabled -> 503/400). Payload is forwarded verbatim to upstream (prompt injection risk upstream).

## Recommendations
- Add auth gate on /v1/train/run or restrict to localhost/admin.
- Add rate limiting on /v1/train/run and /v1/chat/completions.
- Validate/cap `limit` on /v1/skills.
- Sanitize forwarded media payload; validate url scheme/host allowlist if url is consumed upstream.
- Run full Nuclei suite in CI: `nuclei -t docs/api-fuzzing/nuclei-templates/ -u http://127.0.0.1:8799`.