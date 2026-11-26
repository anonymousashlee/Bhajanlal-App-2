#!/usr/bin/env python3
"""Bhajanlal skill library - loads EVERY skill so the model can use them.

Reads every ``SKILL.md`` under ``~/.config/opencode/skills`` (the library
written by ``skill_build/build.py``: 488 skills across 40 pillars, 600/600
coverage) and exposes it to the runtime in four ways:

  1. ``prompt_block()``   - system-prompt section: the skills that are
     relevant to the current user message (full workflow text) plus a compact
     index of ALL skills, so no capability is ever invisible to the model.
  2. ``tool_result()``    - the ``skill`` builtin tool (load / search / list)
     so agent mode can pull any of the 488 skill bodies on demand.
  3. ``catalog()``        - JSON-ready list behind ``GET /v1/skills``.
  4. ``select()``         - relevance scoring reused for response metadata.

The directory is scanned once; afterwards it is re-scanned only when the
directory mtime changes (build.py rewrites skills/ atomically), so the
per-request cost is a few microseconds of token scoring.
"""
from __future__ import annotations

import os
import re
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_ROOT = Path.home() / ".config" / "opencode" / "skills"

# The SecOps pack intentionally uses lightweight SKILL.md files without a
# "Pillar:" line. Keep its catalog grouping here so it survives whichever
# skill root wins (global ~/.config/opencode/skills or a project-local root).
_SECOPS_GROUPING: Dict[str, tuple] = {
    'e164-format-normalizer': (121, 'Phone Number Validation & Carrier Intelligence'),
    'mcc-mnc-operator-lookup': (121, 'Phone Number Validation & Carrier Intelligence'),
    'hlr-lnp-porting-checker': (121, 'Phone Number Validation & Carrier Intelligence'),
    'voip-vs-mobile-classifier': (121, 'Phone Number Validation & Carrier Intelligence'),
    'nanp-npa-nxx-analyzer': (121, 'Phone Number Validation & Carrier Intelligence'),
    'indian-telecom-circle-mapper': (121, 'Phone Number Validation & Carrier Intelligence'),
    'toll-free-premium-rate-detector': (121, 'Phone Number Validation & Carrier Intelligence'),
    'disposable-sms-gateway-detector': (121, 'Phone Number Validation & Carrier Intelligence'),
    'roaming-status-verifier': (121, 'Phone Number Validation & Carrier Intelligence'),
    'imsi-msisdn-correlation-auditor': (121, 'Phone Number Validation & Carrier Intelligence'),
    'line-type-risk-scorer': (121, 'Phone Number Validation & Carrier Intelligence'),
    'international-dialing-plan-validator': (121, 'Phone Number Validation & Carrier Intelligence'),
    'ported-date-recency-alerter': (121, 'Phone Number Validation & Carrier Intelligence'),
    'inactive-disconnected-number-pruner': (121, 'Phone Number Validation & Carrier Intelligence'),
    'mvno-host-network-resolver': (121, 'Phone Number Validation & Carrier Intelligence'),
    'hibp-breach-exposure-checker': (122, 'Authorized OSINT & Reputation Lookup'),
    'spam-robocall-reputation-aggregator': (122, 'Authorized OSINT & Reputation Lookup'),
    'social-handle-discovery-auditor': (122, 'Authorized OSINT & Reputation Lookup'),
    'telegram-bot-osint-command-router': (122, 'Authorized OSINT & Reputation Lookup'),
    'slack-secops-enrichment-bot': (122, 'Authorized OSINT & Reputation Lookup'),
    'whatsapp-business-profile-inspector': (122, 'Authorized OSINT & Reputation Lookup'),
    'google-dork-public-mention-finder': (122, 'Authorized OSINT & Reputation Lookup'),
    'whois-domain-phone-correlator': (122, 'Authorized OSINT & Reputation Lookup'),
    'app-store-developer-phone-auditor': (122, 'Authorized OSINT & Reputation Lookup'),
    'caller-id-cnam-database-querier': (122, 'Authorized OSINT & Reputation Lookup'),
    'darkweb-paste-monitor-webhook': (122, 'Authorized OSINT & Reputation Lookup'),
    'truecaller-privacy-exposure-auditor': (122, 'Authorized OSINT & Reputation Lookup'),
    'linked-account-recovery-auditor': (122, 'Authorized OSINT & Reputation Lookup'),
    'osint-report-pdf-exporter': (122, 'Authorized OSINT & Reputation Lookup'),
    'audit-trail-analyst-logger': (122, 'Authorized OSINT & Reputation Lookup'),
    'smishing-url-extractor-detonator': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'sms-sender-id-spoof-detector': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'india-dlt-header-template-verifier': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'a2p-10dlc-campaign-auditor': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'stir-shaken-attestation-verifier': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'vishing-audio-deepfake-screener': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'otp-pumping-fraud-detector': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'smishing-keyword-nlp-classifier': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'unicode-homoglyph-sms-scanner': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'qr-quishing-mms-decoder': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'shortcode-impersonation-monitor': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'call-detail-record-cdr-anomaly-miner': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'wangiri-one-ring-scam-blocker': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'customer-callback-verification-bot': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'abuse-registrar-takedown-generator': (123, 'SMS Phishing (Smishing) & Voice Fraud Defense'),
    'sim-swap-carrier-event-webhook': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'imsi-change-silent-sms-monitor': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'mfa-downgrade-protection-enforcer': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'step-up-auth-trigger-bot': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'carrier-port-freeze-compliance-checker': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'ss7-diameter-firewall-rule-auditor': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'esim-profile-provisioning-auditor': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'account-recovery-cooldown-timer': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'voicemail-pin-entropy-auditor': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'session-revocation-on-number-change': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'geo-velocity-impossible-travel-correlator': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'device-fingerprint-vs-sim-country': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'automated-sim-swap-incident-playbook': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'sms-otp-rate-limiter': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'silent-network-auth-sna-integrator': (124, 'SIM-Swap & Account Takeover (ATO) Prevention'),
    'whatsapp-two-step-pin-auditor': (125, 'Mobile Device & Messaging App Hardening'),
    'telegram-active-session-auditor': (125, 'Mobile Device & Messaging App Hardening'),
    'signal-registration-lock-verifier': (125, 'Mobile Device & Messaging App Hardening'),
    'android-sms-permission-auditor': (125, 'Mobile Device & Messaging App Hardening'),
    'ios-lockdown-mode-readiness-checker': (125, 'Mobile Device & Messaging App Hardening'),
    'spyware-ioc-backup-scanner': (125, 'Mobile Device & Messaging App Hardening'),
    'malicious-apk-dropper-link-blocker': (125, 'Mobile Device & Messaging App Hardening'),
    'rcs-business-messaging-verifier': (125, 'Mobile Device & Messaging App Hardening'),
    'bluetooth-and-airdrop-hardening': (125, 'Mobile Device & Messaging App Hardening'),
    'public-wifi-vpn-always-on-enforcer': (125, 'Mobile Device & Messaging App Hardening'),
    'clipboard-otp-auto-clear-auditor': (125, 'Mobile Device & Messaging App Hardening'),
    'notification-lockscreen-redaction': (125, 'Mobile Device & Messaging App Hardening'),
    'usb-restricted-mode-enforcer': (125, 'Mobile Device & Messaging App Hardening'),
    'sim-card-pin-lock-auditor': (125, 'Mobile Device & Messaging App Hardening'),
    'phishing-resistant-passkey-migrator': (125, 'Mobile Device & Messaging App Hardening'),
    'bot-rbac-allowlist-middleware': (126, 'Bot Architecture, Security & Compliance'),
    'webhook-hmac-signature-verifier': (126, 'Bot Architecture, Security & Compliance'),
    'pii-redaction-log-sanitizer': (126, 'Bot Architecture, Security & Compliance'),
    'gdpr-dpdp-consent-gatekeeper': (126, 'Bot Architecture, Security & Compliance'),
    'redis-token-bucket-rate-limiter': (126, 'Bot Architecture, Security & Compliance'),
    'api-key-vault-secret-injector': (126, 'Bot Architecture, Security & Compliance'),
    'outbound-proxy-ssrf-guard': (126, 'Bot Architecture, Security & Compliance'),
    'sqlite-postgres-encrypted-case-db': (126, 'Bot Architecture, Security & Compliance'),
    'webhook-replay-nonce-protector': (126, 'Bot Architecture, Security & Compliance'),
    'docker-rootless-bot-hardener': (126, 'Bot Architecture, Security & Compliance'),
    'prometheus-bot-latency-exporter': (126, 'Bot Architecture, Security & Compliance'),
    'circuit-breaker-fallback-handler': (126, 'Bot Architecture, Security & Compliance'),
    'batch-csv-ioc-enrichment-worker': (126, 'Bot Architecture, Security & Compliance'),
    'stix-taxii-threat-feed-exporter': (126, 'Bot Architecture, Security & Compliance'),
    'splunk-sentinel-soar-connector': (126, 'Bot Architecture, Security & Compliance'),
    'interactive-inline-keyboard-triage': (126, 'Bot Architecture, Security & Compliance'),
    'automated-honeypot-sms-collector': (126, 'Bot Architecture, Security & Compliance'),
    'false-positive-whitelist-manager': (126, 'Bot Architecture, Security & Compliance'),
    'multi-language-smishing-translator': (126, 'Bot Architecture, Security & Compliance'),
    'regex-phone-extractor-from-dumps': (126, 'Bot Architecture, Security & Compliance'),
    'tls-13-mtls-webhook-enforcer': (126, 'Bot Architecture, Security & Compliance'),
    'unit-test-mock-carrier-responses': (126, 'Bot Architecture, Security & Compliance'),
    'ci-cd-secret-scanning-gate': (126, 'Bot Architecture, Security & Compliance'),
    'executive-weekly-fraud-digest': (126, 'Bot Architecture, Security & Compliance'),
    'legal-compliance-disclaimer-banner': (126, 'Bot Architecture, Security & Compliance'),
}

_FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
# Two pillar spellings exist in the library:
#   "Pillar: 34. Product Strategy, Growth & AI Evals"
#   "Pillar: Game Development, 3D, Shaders & Graphics (100 skills)"
_PILLAR_RE = re.compile(r"Pillar:\s*(?:(\d+)\.\s*)?([^\n]+)")
_PILLAR_SUFFIX_RE = re.compile(r"\s*\(\d+\s+skills?\)\s*$", re.I)
_WORD_RE = re.compile(r"[a-z0-9]+")

# Words that carry no routing signal (kept small on purpose - a stray
# stopword removal is cheaper than a missed skill match).
_STOP = {
    "the", "and", "for", "you", "your", "with", "that", "this", "these",
    "those", "are", "was", "were", "have", "has", "had", "but", "not",
    "can", "could", "should", "would", "will", "shall", "may", "might",
    "from", "into", "onto", "than", "then", "them", "they", "their",
    "what", "which", "when", "where", "who", "whom", "how", "why",
    "please", "make", "give", "show", "tell", "want", "need", "like",
    "about", "some", "any", "all", "one", "two", "use", "using", "used",
    "write", "create", "build", "help", "just", "very", "more", "most",
    "out", "get", "got", "run", "runn", "its", "it's", "a", "an", "of",
    "in", "on", "to", "is", "it", "be", "do", "does", "did", "if", "or",
    "as", "at", "by", "we", "us", "our", "i", "me", "my", "he", "she",
}


def _tokens(text: str) -> set:
    return {w for w in _WORD_RE.findall((text or "").lower())
            if len(w) > 2 and w not in _STOP}


# ---------------------------------------------------------------- quadrants
# 4-quadrant balance (inference routing + retraining mix):
#   Q1 fast compressed reasoning     - base behavior, every turn
#   Q2 coding & verification         - loaded only when the task involves code
#   Q3 multimodal generation & vision - loaded only for image/video/audio/design
#   Q4 agentic orchestration         - base behavior, every turn
QUADRANTS = ("reasoning", "coding", "multimodal", "agentic")
BASE_QUADRANTS = ("reasoning", "agentic")   # active on EVERY turn

_Q_KEYWORDS = {
    "coding": {
        "code", "codes", "coding", "test", "tests", "testing", "debug",
        "debugging", "typecheck", "lint", "refactor", "function", "class",
        "variable", "python", "javascript", "typescript", "rust", "golang",
        "sql", "database", "api", "endpoint", "git", "commit", "compiler",
        "exception", "bug", "build", "deploy", "regex", "algorithm",
        "json", "yaml", "repository", "repo", "codebase", "coverage",
        "schema", "migration", "docker", "kubernetes", "shell", "bash",
        "stacktrace", "stack", "trace", "unittest", "pytest", "vitest",
        "refactoring", "syntax", "type", "types", "import", "module",
    },
    "multimodal": {
        "image", "images", "picture", "photo", "screenshot", "video",
        "audio", "music", "voice", "render", "shader", "color", "colour",
        "font", "typography", "svg", "png", "jpg", "ui", "ux", "design",
        "layout", "animation", "visual", "visualization", "chart", "diagram",
        "icon", "logo", "poster", "gif", "camera", "speech", "tts",
        "subtitle", "caption", "storyboard", "wireframe", "theme", "css",
        "html", "webgl", "threejs", "blender", "frames", "frame", "audio",
        "waveform", "palette", "mockup", "screenshot",
    },
    "agentic": {
        "tool", "tools", "agent", "agents", "subagent", "agentic",
        "workflow", "orchestration", "skill", "skills", "session",
        "parallel", "batch", "plan", "planning", "mode", "executor",
        "sandbox", "mcp", "calling", "pipeline", "automation", "autonomous",
        "spawn", "delegate", "delegation", "memory", "checkpoint",
        "recovery", "retry", "backoff", "harness", "loop", "executor",
    },
    "reasoning": {
        "reason", "reasoning", "logic", "logical", "think", "thinking",
        "hypothesis", "deduce", "deduction", "infer", "inference",
        "analyze", "analysis", "quick", "fast", "speed", "terse",
        "concise", "compress", "priority", "decision", "tradeoff",
        "ambiguity", "ambiguous", "estimate", "calculate", "math",
        "minimal", "simple", "simplify", "steps", "chain",
    },
}


def detect_quadrants(text: str) -> set:
    """Active quadrants for a user message: Q1+Q4 always, Q2/Q3 on demand."""
    active = set(BASE_QUADRANTS)
    toks = _tokens(text)
    for quad in ("coding", "multimodal"):
        if toks & _Q_KEYWORDS[quad]:
            active.add(quad)
    return active


def _quad_of(text: str) -> str:
    """Classify a skill (id + name + description) into its dominant quadrant."""
    toks = _tokens(text)
    best, best_n = "reasoning", 0
    for quad in ("coding", "multimodal", "agentic", "reasoning"):
        n = len(toks & _Q_KEYWORDS[quad])
        if n > best_n:
            best, best_n = quad, n
    return best


class SkillLibrary:
    """Thread-safe, mtime-refreshed view of the on-disk skill library."""

    def __init__(self, root: Optional[Path] = None,
                 extra_roots: Optional[List[Path]] = None):
        self.root = Path(root or DEFAULT_ROOT).expanduser()
        env_roots = os.environ.get("BHAJANLAL_SKILL_ROOTS", "")
        roots: List[Path] = [self.root]
        if extra_roots:
            roots.extend(Path(r).expanduser() for r in extra_roots)
        for r in env_roots.split(os.pathsep):
            r = r.strip()
            if r:
                roots.append(Path(r).expanduser())
        for base in (Path.cwd(), Path(os.environ.get("BHAIJANLAL_HOME", "") or ".")):
            for sub in (".opencode/skills", ".claude/skills", ".agents/skills"):
                cand = base / sub
                if cand.is_dir():
                    roots.append(cand)
        seen: set = set()
        self.roots: List[Path] = []
        for r in roots:
            key = str(r.resolve()) if r.exists() else str(r)
            if key in seen:
                continue
            seen.add(key)
            self.roots.append(r)
        self._lock = threading.Lock()
        self._skills: List[dict] = []
        self._by_id: Dict[str, dict] = {}
        self._dir_mtime: float = -1.0
        self._built_at: float = 0.0

    # ---------------------------------------------------------------- loading
    def _ensure(self) -> None:
        mtimes = []
        for r in self.roots:
            try:
                mtimes.append(r.stat().st_mtime)
            except OSError:
                mtimes.append(-1.0)
        mtime = sum(mtimes)
        with self._lock:
            if self._skills and mtime == self._dir_mtime:
                return
            self._scan()
            self._dir_mtime = mtime

    def _scan(self) -> None:
        skills: List[dict] = []
        seen_ids: set = set()
        for root in self.roots:
            if not root.is_dir():
                continue
            for path in sorted(root.iterdir()):
                body_file = path / "SKILL.md"
                if not body_file.is_file():
                    continue
                if path.name in seen_ids:
                    continue
                try:
                    raw = body_file.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                front = ""
                m = _FRONT_RE.match(raw)
                if m:
                    front = m.group(1)
                    body = raw[m.end():]
                else:
                    body = raw
                name = self._front_field(front, "name") or path.name
                desc = self._front_field(front, "description") or ""
                if not desc:
                    # First non-heading, non-empty line is a decent fallback.
                    for line in body.splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and not line.startswith("Part of"):
                            desc = line
                            break
                pm = _PILLAR_RE.search(body)
                pillar_n = int(pm.group(1)) if pm and pm.group(1) else 0
                pillar_t = _PILLAR_SUFFIX_RE.sub("", pm.group(2)).strip() if pm else ""
                override = _SECOPS_GROUPING.get(path.name)
                if override and (pillar_n == 0 or pillar_t in ("", "Ungrouped")):
                    pillar_n, pillar_t = override
                if not pillar_t:
                    pillar_t = "Ungrouped"
                seen_ids.add(path.name)
                skills.append({
                    "id": path.name,
                    "name": name.strip(),
                    "description": desc.strip(),
                    "pillar": pillar_n,
                    "pillar_title": pillar_t,
                    "pillar_key": str(pillar_n) if pillar_n else ("t:" + pillar_t),
                    "body": body.strip(),
                    "path": str(body_file),
                    # Pre-computed scoring surfaces (built once per scan).
                    "quadrant": _quad_of(path.name + " " + name + " " + desc),
                    "id_tokens": _tokens(path.name.replace("-", " ")),
                    "name_lower": name.lower(),
                    "desc_lower": desc.lower(),
                    "body_lower": body.lower(),
                    "body_len": len(body),
                })
        self._skills = skills
        self._by_id = {s["id"]: s for s in skills}
        self._built_at = time.time()

    @staticmethod
    def _front_field(front: str, key: str) -> str:
        m = re.search(r"^%s:\s*(.+)$" % re.escape(key), front, re.M)
        return m.group(1).strip() if m else ""

    # --------------------------------------------------------------- queries
    @property
    def count(self) -> int:
        self._ensure()
        return len(self._skills)

    @property
    def pillar_count(self) -> int:
        self._ensure()
        return len({s["pillar_key"] for s in self._skills})

    def catalog(self) -> List[dict]:
        self._ensure()
        return [{
            "id": s["id"],
            "name": s["name"],
            "description": s["description"],
            "pillar": s["pillar"],
            "pillar_title": s["pillar_title"],
            "quadrant": s.get("quadrant", "reasoning"),
        } for s in self._skills]

    def get(self, ident: str) -> Optional[dict]:
        """Exact id, exact name, then case-insensitive / substring match."""
        self._ensure()
        key = (ident or "").strip()
        if not key:
            return None
        hit = self._by_id.get(key) or self._by_id.get(key.lower())
        if hit:
            return hit
        low = key.lower()
        for s in self._skills:
            if s["name"].lower() == low:
                return s
        for s in self._skills:
            if low in s["id"] or low in s["name_lower"]:
                return s
        return None

    def _score(self, s: dict, qtokens: set, qlow: str) -> float:
        score = 0.0
        for t in qtokens:
            if t in s["id_tokens"]:
                score += 3.0
            elif t in s["name_lower"]:
                score += 2.2
            elif t in s["desc_lower"]:
                score += 1.6
            elif t in s["body_lower"]:
                score += 0.35
        if len(qlow) >= 14 and qlow in s["body_lower"]:
            score += 1.5
        return score

    def search(self, query: str, limit: int = 8) -> List[dict]:
        """Ranked skills for a free-text query (id/name/description/body)."""
        self._ensure()
        qlow = (query or "").strip().lower()
        qtokens = _tokens(qlow)
        if not qtokens and not qlow:
            return []
        ranked = []
        for s in self._skills:
            sc = self._score(s, qtokens, qlow)
            if sc > 0:
                ranked.append((sc, s))
        ranked.sort(key=lambda p: (-p[0], p[1]["id"]))
        return [self._public(s, score=round(sc, 2)) for sc, s in ranked[: max(1, limit)]]

    def select(self, text: str, limit: int = 5, min_score: float = 2.0) -> List[dict]:
        """Skills relevant to the current request (auto-applied to the prompt)."""
        self._ensure()
        low = (text or "").strip().lower()
        qtokens = _tokens(low)
        if not qtokens:
            return []
        ranked = []
        for s in self._skills:
            sc = self._score(s, qtokens, low)
            if sc >= min_score:
                ranked.append((sc, s))
        ranked.sort(key=lambda p: (-p[0], p[1]["id"]))
        return [self._public(s, score=round(sc, 2), with_body=True)
                for sc, s in ranked[: max(1, limit)]]

    @staticmethod
    def _public(s: dict, score: Optional[float] = None,
                with_body: bool = False) -> dict:
        out = {
            "id": s["id"],
            "name": s["name"],
            "description": s["description"],
            "pillar": s["pillar"],
            "pillar_title": s["pillar_title"],
        }
        if score is not None:
            out["score"] = score
        if with_body:
            out["workflow"] = s["body"]
        return out

    # ------------------------------------------------------- text rendering
    def index_text(self) -> str:
        """Dense 'id - name' index of every skill, grouped by pillar."""
        self._ensure()
        groups: Dict[str, List[str]] = {}
        heads: Dict[str, str] = {}
        for s in self._skills:
            key = s["pillar_key"]
            groups.setdefault(key, []).append("%s - %s" % (s["id"], s["name"]))
            if key not in heads:
                heads[key] = (
                    "%d. %s" % (s["pillar"], s["pillar_title"])
                    if s["pillar"] else s["pillar_title"]
                )

        def order(k: str) -> tuple:
            return (0, int(k), "") if k.isdigit() else (1, 0, heads[k].lower())

        lines: List[str] = []
        for key in sorted(groups, key=order):
            lines.append("%s: %s" % (heads[key], ", ".join(groups[key])))
        return "\n".join(lines)

    def prompt_block(self, user_text: str, mode: str = "full",
                     max_applied: int = 5) -> str:
        """System-prompt section wiring the whole library into the model.

        mode="full"     -> applied skills + full 488-skill index (default)
        mode="applied"  -> only the skills relevant to this message
        mode="off"      -> nothing
        """
        mode = (mode or "full").lower()
        if mode in ("off", "0", "false", "none"):
            return ""
        self._ensure()
        n = len(self._skills)
        if not n:
            return ""
        # 4-quadrant inference routing: Q1 (fast reasoning) + Q4 (agentic) are
        # base behavior on EVERY turn; Q2 (coding) and Q3 (multimodal) skills
        # are loaded dynamically only when the message involves code or
        # visual/audio assets.
        active = detect_quadrants(user_text)
        applied = self.select(user_text, limit=max_applied + 4)
        # Keep every base-quadrant match, then top up with on-demand skills.
        base = [s for s in applied if s.get("quadrant") in BASE_QUADRANTS]
        dyn = [s for s in applied if s.get("quadrant") in active
               and s.get("quadrant") not in BASE_QUADRANTS]
        applied = (base + dyn)[:max_applied]
        parts: List[str] = []
        head = (
            "BHAIJANLAL SKILL LIBRARY - %d skills across %d pillars are LOADED "
            "and active for you on every request." % (n, self.pillar_count)
        )
        parts.append(head)
        parts.append(
            "QUADRANT ROUTING (4-quadrant balance): base behavior every turn = "
            "Q1 fast compressed reasoning + Q4 agentic orchestration. Q2 coding "
            "& verification skills load only when the task involves code; Q3 "
            "multimodal generation & visual-inspection skills load only when the "
            "task involves images, video, audio, or design assets. Active now: "
            + ", ".join(sorted("Q" + str(QUADRANTS.index(q) + 1) + " " + q
                               for q in active)) + "."
        )
        parts.append(
            "Before answering: pick every skill below that applies to the user's "
            "request and follow its Workflow step by step, then deliver its "
            "documented Output. When a task matches a skill you were not given, "
            "load it with the `skill` tool (actions: load / search / list) or, "
            "in plain chat, use the full index to name the skill and follow it "
            "from memory of its description. Skills always win over improvisation."
        )
        if applied:
            parts.append("APPLIED FOR THIS REQUEST (follow exactly):")
            for i, s in enumerate(applied, 1):
                block = "[%d] %s  (id: %s)\n" % (i, s["name"], s["id"])
                block += "Pillar: %s\n" % self._pillar_head(s)
                block += s["description"] + "\n" + s["workflow"]
                parts.append(block)
        else:
            parts.append(
                "No skill matched this message exactly - consult the index "
                "below and follow the closest one when it fits."
            )
        if mode == "full":
            parts.append(
                "FULL INDEX (%d skills, id - name) - any of them can be loaded "
                "on demand:\n%s" % (n, self.index_text())
            )
        return "\n\n".join(parts)

    @staticmethod
    def _pillar_head(s: dict) -> str:
        if s["pillar"]:
            return "%d. %s" % (s["pillar"], s["pillar_title"])
        return s["pillar_title"] or "Ungrouped"

    def tool_result(self, action: str = "list", ident: str = "",
                    query: str = "", limit: int = 8) -> str:
        """Body text for the `skill` builtin tool."""
        self._ensure()
        action = (action or "list").strip().lower()
        if action == "load":
            s = self.get(ident or query)
            if not s:
                near = self.search(ident or query, limit=5)
                hint = ("\nClosest matches: " + ", ".join(x["id"] for x in near)) if near else ""
                return "error: no skill named %r%s" % (ident or query, hint)
            return ("SKILL: %s (id: %s)\nPillar: %s\nDescription: %s\n\n%s"
                    % (s["name"], s["id"], self._pillar_head(s),
                       s["description"], s["body"]))
        if action == "search":
            hits = self.search(query, limit=limit)
            if not hits:
                return "no skills match %r (try different keywords, or action=list)" % query
            return "\n".join(
                "%s | %s | %s" % (h["id"], h["name"], h["description"])
                for h in hits
            )
        if action in ("list", "all", "index"):
            return self.index_text()
        if action == "count":
            return "%d skills across %d pillars" % (self.count, self.pillar_count)
        return "error: unknown action %r (use load, search, list, count)" % action


# Process-wide singleton (backend.py + endpoint.py share one instance).
LIBRARY = SkillLibrary()


def library() -> SkillLibrary:
    return LIBRARY


def skill_mode(default: str = "off") -> str:
    """BHAJANLAL_SKILLS = full | applied | off  (defaults to off)."""
    return (os.environ.get("BHAJANLAL_SKILLS", default) or default).strip().lower()
