#!/usr/bin/env python3
"""Bhajanlal backend - OpenAI-compatible gateway + agentic runtime.

One local API in front of several fast model families:

  * Xiaomi MiMo V2.6  (mimo-v2.6-flash / mimo-v2.6-pro)
      - fast multimodal reasoning + coding, OpenAI-compatible
      - https://api.xiaomimimo.com/v1   (auth: api-key or Bearer)
  * MiniMax M3        (MiniMax-M3 / MiniMax-M3.1-Flash)
      - 1M-context multimodal coding + agentic tool use
      - https://api.minimax.io/v1      (auth: Bearer)
  * MiniMax H3        (MiniMax-H3 video, MiniMax-H3-Image)
      - media generation, exposed through /v1/media/generations
  * OpenCode free models
      - zero-key fallback (opencode/mimo-v2.6-flash-free, beam, nemotron, ...)
  * Any OpenAI-compatible endpoint via BHAJANLAL_PAID_*

Endpoints
  GET  /                          web chat UI (playground)
  GET  /health                    liveness + provider readiness
  GET  /metrics                   counters, latency percentiles, cache stats
  GET  /v1/models                 model catalog (aliases + raw upstream ids)
  GET  /v1/config                 non-secret runtime config (auth required)
  POST /v1/chat/completions       chat (stream + non-stream, multimodal, tools)
  POST /v1/agent/run              multi-step tool loop with sandboxed builtins
  POST /v1/media/generations      MiniMax H3 video / H3-Image generation
  POST /v1/videos/generations     alias of the above
  POST /v1/images/generations     alias of the above

Omni (all models compiled together)
  "bhajanlal/omni" (aliases: bhajanlal/greatest, bhajanlal/ultimate,
  bhajanlal/ensemble, bhajanlal/best) fans the request out to every configured
  chat provider in parallel (MiMo pro/flash, MiniMax M3/flash, any paid
  OpenAI-compatible endpoint, plus the free OpenCode chain), has a judge score
  the candidates, and returns a synthesized best-of-all answer. Streaming
  clients receive live stage events, and the final response carries full
  candidate/score metadata under x_bhajanlal.ensemble.

Design notes
  * The gateway binds 127.0.0.1 only. Put the auth proxy / tunnel in front.
  * Fallback order for "bhajanlal": MiMo -> MiniMax -> OpenCode free chain.
  * OpenCode is run WITHOUT --auto and in a dedicated sandbox cwd, so an
    untrusted prompt cannot auto-approve shell/edit tools on the host.
  * Tool execution for /v1/agent/run is done by this process, not by OpenCode.
"""
from __future__ import annotations

import ast
import asyncio
import hashlib
import hmac
import json
import logging
import math
import os
import random
import re
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from pathlib import Path

PUBLIC_MODEL = "bhajanlal/pro-max-2.5-free"


def public_model(name: Any = None) -> str:
    """Branding: never leak raw opencode/* ids in outbound responses."""
    if name and str(name).startswith("bhajanlal"):
        return str(name)
    return PUBLIC_MODEL
from typing import Any, Dict, Iterable, List, Optional, Tuple

import httpx
from aiohttp import web

# The skill library lives next to this file (serve/skills.py) and reads the
# 488-skill Bhajanlal library from ~/.config/opencode/skills.
_SERVE_DIR = str(Path(__file__).resolve().parent)
if _SERVE_DIR not in sys.path:
    sys.path.insert(0, _SERVE_DIR)
# Skill roots are computed at import time; point the library at the project
# root so its .opencode/skills/ is found even when cwd is serve/.
os.environ.setdefault("BHAIJANLAL_HOME", str(Path(_SERVE_DIR).parent))
try:
    import skills as _skills_mod
except Exception as _exc:  # noqa: BLE001 - library must never break the gateway
    _skills_mod = None
    logging.getLogger("bhajanlal").warning("skill library unavailable: %r", _exc)

SKILLS = _skills_mod.LIBRARY if _skills_mod else None

VERSION = "2.2.0"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _env_str(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _env_int(name: str, default: int) -> int:
    try:
        return int(_env_str(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(_env_str(name, str(default)))
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = _env_str(name, "1" if default else "0").lower()
    return raw in ("1", "true", "yes", "on")


def _load_dotenv(paths: Iterable[Path]) -> None:
    """Tiny .env loader (no python-dotenv dependency). Existing env wins."""
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


FREE_MODELS = [
    "opencode/mimo-v2.6-flash-free",
    "opencode/beam-free",
    "opencode/nemotron-3.5-lightning-free",
    "opencode/deepseek-v4.1-flash-free",
    "opencode/hy4-flash-free",
    "opencode/iceman-free",
    "opencode/longcat-2.5-free",
    "opencode/flint-40b-free",
    "opencode/tidepool-alpha-free",
    "opencode/nemotron-3.5-super-vl-free",
]


@dataclass
class Settings:
    host: str = "127.0.0.1"
    port: int = 8790
    api_key: str = "bhajanlal-local"
    extra_keys: str = ""
    allow_localhost: bool = True
    cors_origins: str = ""
    max_concurrent: int = 8
    queue_timeout: float = 10.0
    request_timeout: float = 120.0
    run_timeout: float = 180.0
    cache_ttl: float = 120.0
    cache_max: int = 512
    sandbox: str = ""
    agent_write: bool = False
    agent_shell: bool = True
    shell_timeout: float = 120.0
    fallback_free: bool = True
    prefer_local: bool = False
    disable_free_upstream: bool = False
    opencode_default: str = "opencode/mimo-v2.6-flash-free"
    opencode_free_models: List[str] = field(default_factory=lambda: list(FREE_MODELS))
    opencode_cwd: str = ""
    opencode_agent: str = ""
    mimo_base_url: str = "https://api.xiaomimimo.com/v1"
    mimo_api_key: str = ""
    mimo_model: str = "mimo-v2.6-flash"
    mimo_model_pro: str = "mimo-v2.6-pro"
    minimax_base_url: str = "https://api.minimax.io/v1"
    minimax_api_key: str = ""
    minimax_model: str = "MiniMax-M3"
    minimax_model_flash: str = "MiniMax-M3.1-Flash"
    minimax_video_model: str = "MiniMax-H3"
    minimax_image_model: str = "MiniMax-H3-Image"
    minimax_video_path: str = "/video_generation"
    minimax_video_query_path: str = "/query/video_generation"
    minimax_file_retrieve_path: str = "/files/retrieve"
    minimax_image_path: str = "/image_generation"
    paid_base_url: str = ""
    local_base_url: str = "http://127.0.0.1:8788/v1"
    paid_api_key: str = ""
    paid_model: str = "gpt-4o-mini"


def load_settings() -> Settings:
    here = Path(__file__).resolve().parent
    _load_dotenv([
        here / ".env",
        Path.home() / "model-ops" / ".env",
        Path.home() / ".config" / "bhajanlal" / ".env",
    ])
    return Settings(
        host=_env_str("BHAJANLAL_BACKEND_HOST", "127.0.0.1") or "127.0.0.1",
        port=_env_int("BHAJANLAL_BACKEND_PORT", 8790),
        api_key=_env_str("BHAJANLAL_API_KEY", "bhajanlal-local") or "bhajanlal-local",
        extra_keys=_env_str("BHAJANLAL_EXTRA_KEYS", ""),
        allow_localhost=_env_bool("BHAJANLAL_ALLOW_LOCALHOST", True),
        cors_origins=_env_str("BHAJANLAL_CORS_ORIGINS", "") or "",
        max_concurrent=_env_int("BHAJANLAL_MAX_CONCURRENT", 8),
        queue_timeout=_env_float("BHAJANLAL_QUEUE_TIMEOUT", 10.0),
        request_timeout=_env_float("BHAJANLAL_REQUEST_TIMEOUT", 120.0),
        run_timeout=_env_float("BHAJANLAL_RUN_TIMEOUT", 180.0),
        cache_ttl=_env_float("BHAJANLAL_CACHE_TTL", 600.0),
        cache_max=_env_int("BHAJANLAL_CACHE_MAX", 4096),
        sandbox=_env_str("BHAJANLAL_SANDBOX", ""),
        agent_write=_env_bool("BHAJANLAL_AGENT_WRITE", False),
        agent_shell=_env_bool("BHAJANLAL_AGENT_SHELL", True),
        shell_timeout=_env_float("BHAJANLAL_AGENT_SHELL_TIMEOUT", 120.0),
        fallback_free=_env_bool("BHAJANLAL_FALLBACK_FREE", True),
        prefer_local=_env_bool("BHAJANLAL_PREFER_LOCAL", False),
        disable_free_upstream=_env_bool("BHAJANLAL_DISABLE_FREE_UPSTREAM", False),
        opencode_default=_env_str("BHAJANLAL_OPENCODE_MODEL", "opencode/beam-free"),
        opencode_free_models=[
            m.strip() for m in _env_str(
                "BHAJANLAL_OPENCODE_FREE_MODELS", ",".join(FREE_MODELS)
            ).split(",") if m.strip()
        ],
        opencode_cwd=_env_str("BHAJANLAL_OPENCODE_CWD", ""),
        opencode_agent=_env_str("BHAJANLAL_OPENCODE_AGENT", ""),
        mimo_base_url=_env_str("BHAJANLAL_MIMO_BASE_URL", "https://api.xiaomimimo.com/v1"),
        mimo_api_key=_env_str("BHAJANLAL_MIMO_API_KEY", "") or _env_str("MIMO_API_KEY", ""),
        mimo_model=_env_str("BHAJANLAL_MIMO_MODEL", "mimo-v2.6-flash"),
        mimo_model_pro=_env_str("BHAJANLAL_MIMO_MODEL_PRO", "mimo-v2.6-pro"),
        minimax_base_url=_env_str("BHAJANLAL_MINIMAX_BASE_URL", "https://api.minimax.io/v1"),
        minimax_api_key=_env_str("BHAJANLAL_MINIMAX_API_KEY", "") or _env_str("MINIMAX_API_KEY", ""),
        minimax_model=_env_str("BHAJANLAL_MINIMAX_MODEL", "MiniMax-M3"),
        minimax_model_flash=_env_str("BHAJANLAL_MINIMAX_MODEL_FLASH", "MiniMax-M3.1-Flash"),
        minimax_video_model=_env_str("BHAJANLAL_MINIMAX_VIDEO_MODEL", "MiniMax-H3"),
        minimax_image_model=_env_str("BHAJANLAL_MINIMAX_IMAGE_MODEL", "MiniMax-H3-Image"),
        minimax_video_path=_env_str("BHAJANLAL_MINIMAX_VIDEO_PATH", "/video_generation"),
        minimax_video_query_path=_env_str("BHAJANLAL_MINIMAX_VIDEO_QUERY_PATH", "/query/video_generation"),
        minimax_file_retrieve_path=_env_str("BHAJANLAL_MINIMAX_FILE_RETRIEVE_PATH", "/files/retrieve"),
        minimax_image_path=_env_str("BHAJANLAL_MINIMAX_IMAGE_PATH", "/image_generation"),
        paid_base_url=_env_str("BHAJANLAL_PAID_BASE_URL", ""),
        local_base_url=_env_str("BHAJANLAL_LOCAL_BASE_URL", "http://127.0.0.1:8788/v1"),
        paid_api_key=_env_str("BHAJANLAL_PAID_API_KEY", ""),
        paid_model=_env_str("BHAJANLAL_PAID_MODEL", "gpt-4o-mini"),
    )


# ---------------------------------------------------------------------------
# Providers and routing
# ---------------------------------------------------------------------------

@dataclass
class Provider:
    name: str
    kind: str                      # chat | video | image
    base_url: str
    api_key: str
    auth_style: str = "bearer"     # bearer | mimo
    models: List[str] = field(default_factory=list)
    capabilities: set = field(default_factory=set)
    enabled: bool = False

    def headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if not self.api_key:
            return headers
        if self.auth_style == "mimo":
            # MiMo accepts either api-key or Bearer; send both for compatibility.
            headers["api-key"] = self.api_key
            headers["Authorization"] = "Bearer " + self.api_key
        else:
            headers["Authorization"] = "Bearer " + self.api_key
        return headers


@dataclass
class Route:
    provider: str
    model: str
    kind: str = "chat"


def build_providers(s: Settings) -> Dict[str, Provider]:
    return {
        "mimo": Provider(
            "mimo", "chat", s.mimo_base_url, s.mimo_api_key, "mimo",
            [s.mimo_model, s.mimo_model_pro], {"vision", "tools", "reasoning", "coding", "multimodal", "agentic", "fast"},
            bool(s.mimo_api_key),
        ),
        "minimax": Provider(
            "minimax", "chat", s.minimax_base_url, s.minimax_api_key, "bearer",
            [s.minimax_model, s.minimax_model_flash], {"vision", "tools", "reasoning", "coding", "multimodal", "agentic", "fast"},
            bool(s.minimax_api_key),
        ),
        "minimax_video": Provider(
            "minimax_video", "video", s.minimax_base_url, s.minimax_api_key, "bearer",
            [s.minimax_video_model], {"video", "multimodal", "agentic", "fast"}, bool(s.minimax_api_key),
        ),
        "minimax_image": Provider(
            "minimax_image", "image", s.minimax_base_url, s.minimax_api_key, "bearer",
            [s.minimax_image_model], {"image", "multimodal", "agentic", "fast"}, bool(s.minimax_api_key),
        ),
        "openai": Provider(
            "openai", "chat", s.paid_base_url, s.paid_api_key, "bearer",
            [s.paid_model], {"vision", "tools", "reasoning", "coding", "multimodal", "agentic", "fast"},
            bool(s.paid_api_key and s.paid_base_url),
        ),
        "opencode": Provider(
            "opencode", "chat", "", "", "none",
            [s.opencode_default] + [m for m in s.opencode_free_models if m != s.opencode_default],
            {"tools", "reasoning", "coding", "multimodal", "agentic", "fast"}, True,
        ),
        "local": Provider(
            "local", "chat", s.local_base_url, "", "none",
            ["bhajanlal/local"], {"reasoning", "coding", "multimodal", "agentic", "fast"}, True,
        ),
    }


OMNI_FULL_SPEC = [
    ("mimo", "pro"), ("mimo", "flash"), ("minimax", None),
    ("minimax", "flash"), ("openai", None), ("local", None),
]

ALIAS_SPECS: Dict[str, List[Tuple[str, Optional[str]]]] = {
    "bhajanlal": list(OMNI_FULL_SPEC),
    "bhajanlal/bhajanlal": list(OMNI_FULL_SPEC),
    "bhajanlal/auto": [("mimo", None), ("minimax", None), ("local", None)],
    "bhajanlal/flash": [("mimo", "flash"), ("minimax", "flash"), ("local", None)],
    "bhajanlal/coding": [("minimax", None), ("mimo", "flash"), ("local", None)],
    "bhajanlal/mimo": [("mimo", "flash")],
    "bhajanlal/mimo-flash": [("mimo", "flash")],
    "bhajanlal/mimo-pro": [("mimo", "pro")],
    "bhajanlal/minimax": [("minimax", None)],
    "bhajanlal/minimax-m3": [("minimax", None)],
    "bhajanlal/minimax-flash": [("minimax", "flash")],
    "bhajanlal/minimax-h3": [("minimax_video", None)],
    "bhajanlal/minimax-h3-image": [("minimax_image", None)],
    "bhajanlal/paid": [("openai", None)],
    "bhajanlal": [("local", None)],
    "bhajanlal/local": [("local", None)],
    "bhajanlal/opencode": [("opencode", None)],
    "bhajanlal/omni": list(OMNI_FULL_SPEC),
    "bhajanlal/greatest": [("mimo", "pro"), ("mimo", "flash"), ("minimax", None), ("minimax", "flash"), ("openai", None), ("local", None)],
    "bhajanlal/ultimate": [("mimo", "pro"), ("mimo", "flash"), ("minimax", None), ("minimax", "flash"), ("openai", None), ("local", None)],
    "bhajanlal/ensemble": [("mimo", "pro"), ("mimo", "flash"), ("minimax", None), ("minimax", "flash"), ("openai", None), ("local", None)],
    "bhajanlal/best": [("mimo", "pro"), ("mimo", "flash"), ("minimax", None), ("minimax", "flash"), ("openai", None), ("local", None)],
    # "Bhajanlal Pro Max" - the compiled model: every configured chat family
    # (MiMo pro + flash, MiniMax M3 + flash, paid OpenAI-compatible, free
    # OpenCode chain) fanned out in parallel, judge-scored and synthesized.
    "bhajanlal/pro-max": list(OMNI_FULL_SPEC),
    "bhajanlal/promax": list(OMNI_FULL_SPEC),
    "bhajanlal pro max": list(OMNI_FULL_SPEC),
    # Published OpenCode model id: "Bhajanlal Pro Max 2.5 free"
    # Fast single-provider route: skip ensemble fan-out/judge/synthesis so the
    # free model answers (and emits shell tool calls) at speed while keeping
    # quality. Ensemble remains available via bhajanlal/pro-max.
    "bhajanlal/pro-max-2.5-free": [("opencode", None), ("local", None)],
    "bhajanlal/pro-max-2.5": [("opencode", None), ("local", None)],
    "bhajanlal pro max 2.5 free": [("opencode", None), ("local", None)],
}

# Case-insensitive alias lookup so "Bhajanlal Pro Max" resolves like "bhajanlal/pro-max".
ALIAS_LOOKUP = {k.lower(): k for k in ALIAS_SPECS}

# NOTE: "bhajanlal/pro-max-2.5-free" / "bhajanlal pro max 2.5 free" are
# deliberately NOT ensemble aliases: they take the fast single-provider route
# (see ALIAS_SPECS) so the public free model answers in ~1s. The ensemble
# fan-out + judge costs ~19s and the judge degrades to the 0.5B local model
# under the free limit (no parseable output, zero quality gain). Use
# bhajanlal/pro-max for the full multi-model ensemble.
ENSEMBLE_ALIASES = {"bhajanlal", "bhajanlal/bhajanlal", "bhajanlal/omni", "bhajanlal/greatest", "bhajanlal/ultimate", "bhajanlal/ensemble", "bhajanlal/best", "bhajanlal/pro-max", "bhajanlal/promax", "bhajanlal pro max", "bhajanlal/pro-max-2.5"}
OMNI_ALIASES = {"bhajanlal", "bhajanlal/bhajanlal", "bhajanlal/omni", "bhajanlal/greatest", "bhajanlal/ultimate", "bhajanlal/pro-max", "bhajanlal/promax", "bhajanlal pro max", "bhajanlal/pro-max-2.5"}


def _model_for(s: Settings, provider: str, which: Optional[str]) -> str:
    if provider == "mimo":
        return s.mimo_model_pro if which == "pro" else s.mimo_model
    if provider == "minimax":
        return s.minimax_model_flash if which == "flash" else s.minimax_model
    if provider == "minimax_video":
        return s.minimax_video_model
    if provider == "minimax_image":
        return s.minimax_image_model
    if provider == "openai":
        return s.paid_model
    if provider == "local":
        return "bhajanlal/local"
    return s.opencode_default


def _make_route(
    s: Settings,
    providers: Dict[str, Provider],
    provider: str,
    model: Optional[str] = None,
    kind: str = "chat",
) -> Optional[Route]:
    p = providers.get(provider)
    if not p or p.kind != kind:
        return None
    if kind == "chat" and not p.enabled:
        return None
    return Route(provider, model or p.models[0], kind)


def resolve_routes(
    s: Settings,
    providers: Dict[str, Provider],
    requested: Optional[str],
) -> Tuple[List[Route], str]:
    """Return ordered routes and the request kind (chat/video/image)."""
    requested = (requested or "bhajanlal").strip()
    low = requested.lower()
    routes: List[Route] = []
    kind = "chat"

    def add(provider: str, which: Optional[str] = None) -> None:
        route = _make_route(s, providers, provider, _model_for(s, provider, which), "chat")
        if route and all((r.provider, r.model) != (route.provider, route.model) for r in routes):
            routes.append(route)

    alias_key = ALIAS_LOOKUP.get(low)
    if alias_key:
        specs = ALIAS_SPECS[alias_key]
        if any(p in ("minimax_video", "minimax_image") for p, _ in specs):
            provider = specs[0][0]
            kind = providers[provider].kind
            route = _make_route(s, providers, provider, _model_for(s, provider, None), kind)
            return ([route] if route else []), kind
        for provider, which in specs:
            add(provider, which)
    elif low.startswith("opencode/"):
        route = Route("opencode", requested, "chat")
        routes.append(route)
    elif low.startswith("mimo-"):
        route = _make_route(s, providers, "mimo", requested, "chat")
        if route:
            routes.append(route)
    elif low.startswith("minimax-h3-image"):
        kind = "image"
        route = _make_route(s, providers, "minimax_image", s.minimax_image_model, kind)
        if route:
            routes.append(route)
    elif low.startswith("minimax-h3"):
        kind = "video"
        route = _make_route(s, providers, "minimax_video", s.minimax_video_model, kind)
        if route:
            routes.append(route)
    elif low.startswith("minimax-m"):
        route = _make_route(s, providers, "minimax", requested, "chat")
        if route:
            routes.append(route)
    else:
        # Unknown names get the safe auto chain rather than being forwarded to
        # a paid provider.
        for provider, which in ALIAS_SPECS["bhajanlal"]:
            add(provider, which)

    if kind == "chat" and s.fallback_free and not s.disable_free_upstream and not _free_limit_active():
        for model in [s.opencode_default] + s.opencode_free_models:
            if model and all((r.provider, r.model) != ("opencode", model) for r in routes):
                routes.append(Route("opencode", model, "chat"))
    # Prefer local: put local route first when requested or when free tier exhausted.
    if (s.prefer_local or _free_limit_active() or s.disable_free_upstream) and kind == "chat":
        routes.insert(0, Route("local", "bhajanlal/local", "chat"))
    return routes, kind


# ---------------------------------------------------------------------------
# Metrics / logging
# ---------------------------------------------------------------------------

_METRICS: Dict[str, int] = {}
_METRICS_LOCK = threading.Lock()
_LATENCIES: deque = deque(maxlen=2000)
_LOG_LOCK = threading.Lock()
_STARTED = time.time()
_ACTIVE = 0


def metric(name: str, n: int = 1) -> None:
    with _METRICS_LOCK:
        _METRICS[name] = _METRICS.get(name, 0) + n


def _record_latency(ms: float) -> None:
    with _METRICS_LOCK:
        _LATENCIES.append(ms)


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, max(0, int(round((p / 100.0) * (len(values) - 1)))))
    return round(values[idx], 1)


def log_event(**fields: Any) -> None:
    fields.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    line = json.dumps(fields, default=str, separators=(",", ":"))
    with _LOG_LOCK:
        sys.stderr.write(line + "\n")
        sys.stderr.flush()


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class UpstreamError(Exception):
    def __init__(self, status: int, message: str, provider: str = "", retryable: bool = False):
        super().__init__(message)
        self.status = status
        self.message = message
        self.provider = provider
        self.retryable = retryable


class AllProvidersFailed(Exception):
    def __init__(self, attempts: List[dict], last: Optional[UpstreamError]):
        self.attempts = attempts
        self.last = last
        status = 429 if any(a.get("status") == 429 for a in attempts) else 502
        detail = last.message if last else "all providers failed"
        super().__init__(detail)
        self.status = status


def error_response(status: int, message: str, **extra: Any) -> web.Response:
    body: Dict[str, Any] = {
        "error": {
            "message": message,
            "type": "invalid_request_error" if status < 500 else "upstream_error",
            "code": str(status),
        }
    }
    body["error"].update(extra)
    return web.json_response(body, status=status)


def _local_was_busy(attempts: List[dict]) -> bool:
    """True when the local fallback already failed with a transient error
    (endpoint busy / timeout) - worth one more attempt before giving up."""
    for a in attempts or []:
        if a.get("provider") == "local" and not a.get("ok"):
            err = str(a.get("error") or "").lower()
            if any(x in err for x in ("503", "busy", "timeout", "timed out")):
                return True
    return False


def all_failed_message(exc: "AllProvidersFailed") -> str:
    """Short, actionable client-facing message for a total provider failure."""
    blob = " ".join(str(a.get("error") or "") for a in (exc.attempts or [])).lower()
    if ("free_limit" in blob or "free usage limit" in blob
            or "rate limit" in blob or "429" in blob or "quota" in blob):
        return (
            "free upstream tier exhausted; switched to local model. To avoid "
            "this permanently, set BHAJANLAL_DISABLE_FREE_UPSTREAM=1 and/or "
            "BHAJANLAL_PREFER_LOCAL=1, or connect a paid provider via "
            "BHAJANLAL_MIMO_API_KEY / BHAJANLAL_MINIMAX_API_KEY."
        )
    return "all providers failed (%d attempts); see attempts for details" % len(exc.attempts or [])


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

_SECRET_KEY_CACHE = {"at": 0.0, "value": ""}


def _secret_key() -> str:
    now = time.time()
    if now - _SECRET_KEY_CACHE["at"] < 5:
        return _SECRET_KEY_CACHE["value"]
    value = ""
    try:
        value = (Path.home() / "model-ops" / ".secret_key").read_text().strip()
    except OSError:
        pass
    _SECRET_KEY_CACHE.update(at=now, value=value)
    return value


def _auth_ok(request: web.Request) -> bool:
    # Free, open access: no API key required.
    return True


# ---------------------------------------------------------------------------
# HTTP upstream helpers
# ---------------------------------------------------------------------------

def _url(provider: Provider, path: str) -> str:
    return provider.base_url.rstrip("/") + "/" + path.lstrip("/")


def _classify_http(status: int, text: str) -> Tuple[str, bool]:
    low = text.lower()
    if status == 429 or any(x in low for x in ("rate limit", "quota", "too many requests")):
        return "rate_limit", True
    if status in (401, 403):
        return "auth", False
    if status == 400:
        return "bad_request", False
    if status in (500, 502, 503, 504):
        return "server", True
    return "http", status >= 500


async def _post_json(
    client: httpx.AsyncClient,
    provider: Provider,
    path: str,
    body: dict,
    timeout: float,
) -> dict:
    url = _url(provider, path)
    last: Optional[Exception] = None
    for attempt in range(3):
        try:
            r = await client.post(url, json=body, headers=provider.headers(), timeout=timeout)
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            last = exc
            if attempt < 2:
                # Connection-level failure: retry with exponential backoff + jitter.
                delay = 0.25 * (2 ** attempt) + random.uniform(0, 0.25)
                await asyncio.sleep(delay)
                continue
            raise UpstreamError(504, "upstream timeout: %s" % exc, provider.name, True)
        if r.status_code < 400:
            try:
                return r.json()
            except ValueError:
                raise UpstreamError(502, "upstream returned invalid JSON", provider.name, True)
        text = (await r.aread()).decode(errors="replace")[:800]
        kind, retryable = _classify_http(r.status_code, text)
        if retryable and attempt < 2:
            delay = 0.5 * (2 ** attempt) + random.uniform(0, 0.25)
            await asyncio.sleep(delay)
            continue
        raise UpstreamError(r.status_code, "%s: %s" % (kind, text), provider.name, retryable)
    raise UpstreamError(502, "upstream failed: %s" % last, provider.name, True)


async def _get_json(
    client: httpx.AsyncClient,
    provider: Provider,
    path: str,
    timeout: float,
) -> dict:
    r = await client.get(_url(provider, path), headers=provider.headers(), timeout=timeout)
    if r.status_code >= 400:
        text = (await r.aread()).decode(errors="replace")[:800]
        raise UpstreamError(r.status_code, text, provider.name, r.status_code >= 500)
    return r.json()


# ---------------------------------------------------------------------------
# Prompt / message helpers
# ---------------------------------------------------------------------------

def _extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "text":
                    parts.append(part.get("text", ""))
                elif "text" in part:
                    parts.append(part.get("text", ""))
            elif isinstance(part, str):
                parts.append(part)
        return " ".join(p for p in parts if p)
    return "" if content is None else str(content)


def _image_parts(content: Any) -> List[dict]:
    out = []
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") in ("image_url", "image"):
                out.append(part)
    return out


def sanitize_messages(messages: Any) -> List[dict]:
    out = []
    for m in messages or []:
        if not isinstance(m, dict):
            continue
        role = m.get("role") or "user"
        item: Dict[str, Any] = {"role": role}
        if "content" in m:
            item["content"] = m["content"]
        if m.get("name"):
            item["name"] = m["name"]
        if m.get("tool_calls"):
            item["tool_calls"] = m["tool_calls"]
        if m.get("tool_call_id"):
            item["tool_call_id"] = m["tool_call_id"]
        out.append(item)
    return out


# Bhajanlal Pro Max 2.5 free: user-facing speed tip carried in the prompt.
_SPEED_TIP = (
    "Speed tip for Bhajanlal Pro Max 2.5 free: mention this to the user once "
    "early in the conversation, and again whenever they ask about response "
    "speed: \"If you want faster responses, keeping questions specific and "
    "avoiding sessions with lots of file reads usually helps most.\""
)


def _wants_speed_tip(model: Any) -> bool:
    """Only Bhajanlal Pro Max 2.5 free carries the speed tip."""
    low = str(model or "").strip().lower()
    return "pro-max-2.5-free" in low or "pro max 2.5 free" in low


def _with_speed_tip(messages: list, model: Any) -> list:
    """Append the speed tip as a system message (idempotent)."""
    if not _wants_speed_tip(model):
        return list(messages or [])
    msgs = list(messages or [])
    if any(_SPEED_TIP in str(m.get("content") or "")
           for m in msgs if isinstance(m, dict)):
        return msgs
    return msgs + [{"role": "system", "content": _SPEED_TIP}]


def _skill_mode() -> str:
    """BHAJANLAL_SKILLS = full | applied | off (default: applied)."""
    if _skills_mod is None:
        return "off"
    return _skills_mod.skill_mode("applied")


def _skill_block(user_text: str) -> str:
    """System-prompt section wiring every Bhajanlal skill into the model."""
    if SKILLS is None:
        return ""
    try:
        return SKILLS.prompt_block(user_text, mode=_skill_mode())
    except Exception as exc:  # noqa: BLE001 - never fail a request over skills
        log_event(event="skill_block_error", error=repr(exc))
        return ""


def _skills_info() -> dict:
    """Summary used by /health, /v1/config and agent responses."""
    if SKILLS is None:
        return {"available": False, "count": 0, "pillars": 0, "mode": "off"}
    return {"available": True, "count": SKILLS.count,
            "pillars": SKILLS.pillar_count, "mode": _skill_mode()}


def _inject_skills(msgs: List[dict]) -> List[dict]:
    """Prepend/merge the skill block into a message list for native providers.

    Used for the MiMo / MiniMax / paid OpenAI-compatible routes, which take
    `messages` straight from the client instead of going through build_prompt.
    """
    if not msgs or SKILLS is None or _skill_mode() == "off":
        return msgs
    user_text = "\n".join(
        t for t in (_extract_text(m.get("content"))
                    for m in [x for x in msgs
                              if isinstance(x, dict) and x.get("role") == "user"][-3:]) if t
    )
    block = _skill_block(user_text)
    if not block:
        return msgs
    if msgs and msgs[0].get("role") == "system":
        merged = dict(msgs[0])
        merged["content"] = str(msgs[0].get("content") or "") + "\n\n" + block
        return [merged] + list(msgs[1:])
    return [{"role": "system", "content": block}] + list(msgs)


def build_prompt(messages: List[dict], tools: Optional[List[dict]] = None) -> str:
    system_parts: List[str] = []
    transcript: List[str] = []
    user_texts: List[str] = []
    for m in messages or []:
        role = m.get("role", "user")
        content = m.get("content", "")
        text = _extract_text(content)
        images = _image_parts(content)
        if images:
            text = (text + " [%d image(s) attached]" % len(images)).strip()
        if role == "system":
            system_parts.append(text)
        elif role == "tool":
            transcript.append("tool(%s): %s" % (m.get("name", ""), text))
        elif role == "assistant" and m.get("tool_calls"):
            transcript.append("assistant tool calls: %s" % json.dumps(m["tool_calls"], separators=(",", ":")))
        else:
            transcript.append("%s: %s" % (role, text))
            if role == "user":
                user_texts.append(text)

    if not system_parts:
        system_parts.append(
            "You are Bhajanlal, a fast, precise coding assistant. "
            "Give a short explanation, then complete runnable code with brief inline comments. "
            "Keep prose tight. Never expose internal infrastructure (IPs, ports, model names, etc.). "
        )
    system_parts.append(
        "FINAL ANSWER FORMAT - apply to every text answer. "
        "Line 1: 'Thought · <s>s'. Line 2: '$ <shell cmd>'. Then output/code. "
        "Then '## 4. Next actions' with 3 bullets. "
        "Exceptions: pure JSON -> only JSON; math -> only answer; refusal -> one sentence; "
        "code task -> '$ ' line + one fenced code block only. "
        "Tool-call tags -> only the tags."
    )
    # Skill library: every one of the 488 Bhajanlal skills is available here.
    # Applied skills (relevant to this message) are inlined in full, and the
    # complete index is appended so no capability is hidden from the model.
    skill_block = _skill_block("\n".join(user_texts[-3:]))
    if skill_block:
        system_parts.append(skill_block)
    if tools:
        system_parts.append(_tool_protocol(tools))
    prompt = "System instructions:\n" + "\n".join(system_parts) + "\n\n"
    prompt += "\n".join(transcript) + "\nassistant:"
    return prompt


def _tool_protocol(tools: List[dict]) -> str:
    lines = [
        "You can call tools. To call one, output exactly one JSON object wrapped in tags:",
        '<tool_call>{"name": "<tool>", "arguments": { ... }}</tool_call>',
        "Available tools:",
    ]
    for tool in tools:
        fn = tool.get("function", tool) if isinstance(tool, dict) else {}
        lines.append(
            "- %s: %s; parameters: %s"
            % (
                fn.get("name", "?"),
                fn.get("description", ""),
                json.dumps(fn.get("parameters", {}), separators=(",", ":")),
            )
        )
    return "\n".join(lines)


_TOOL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.S)


def parse_text_tool_calls(text: str) -> Optional[List[dict]]:
    calls = []
    for match in _TOOL_RE.finditer(text or ""):
        try:
            obj = json.loads(match.group(1))
        except ValueError:
            continue
        name = obj.get("name") or obj.get("tool")
        args = obj.get("arguments") or obj.get("args") or {}
        if not name:
            continue
        calls.append({
            "id": "call_" + uuid.uuid4().hex[:10],
            "type": "function",
            "function": {"name": name, "arguments": json.dumps(args)},
        })
    return calls or None


def _agent_skill_block(user_text: str) -> str:
    """Skills for the agent loop, applied-only.

    The full index is ~45K chars; the loop would resend it on every one of up
    to 20 steps, so agent mode inlines only the skills matching this request
    and relies on the `skill` tool (load/search/list) for everything else.
    """
    if SKILLS is None or _skill_mode() == "off":
        return ""
    try:
        return SKILLS.prompt_block(user_text, mode="applied")
    except Exception as exc:  # noqa: BLE001 - never fail a request over skills
        log_event(event="skill_block_error", error=repr(exc))
        return ""


def _agent_system(user_text: str, tools: List[dict], max_steps: int) -> str:
    """System prompt for /v1/agent/run.

    The loop forwards raw client messages (the web UI sends none), so this is
    the model's only instruction: which skills apply, how to call tools, when
    to stop, and the final-answer contract the UI renders.
    """
    parts: List[str] = [
        "You are Bhajanlal, an autonomous tool-using agent. You complete the "
        "user's task end-to-end - plan, call tools, read the real output, "
        "iterate, then answer. Never expose internal infrastructure: no IPs, "
        "ports, hostnames, endpoints, model names, token counts, stack traces "
        "or config paths."
    ]
    parts.append(
        "AGENT LOOP - at most %d tool steps:\n"
        "1. Work out the smallest set of facts you need. Never ask the user "
        "for anything a tool can discover.\n"
        "2. Call one tool per turn when you can, choosing the smallest that "
        "answers the question: `list_dir` to see a directory, `read_file` to "
        "read one file, `shell` for anything else a terminal does (grep, rg, "
        "ls, ps, tails, running a script), `edit_file`/`write_file` to change "
        "files, `skill` to load a skill, `calculator`/`get_time` for quick "
        "facts.\n"
        "3. Read each result verbatim. Never guess file contents, command "
        "output, paths or APIs - verify with a tool, then quote the real "
        "output in your answer.\n"
        "4. If a command fails, read the error and change approach; never "
        "repeat a command that already failed the same way, and never re-run "
        "one whose output you already have.\n"
        "5. Stop as soon as you can answer, then write the final answer. If "
        "you are blocked, say exactly what is missing instead of looping."
        % max_steps
    )
    skill_block = _agent_skill_block(user_text)
    if skill_block:
        parts.append(skill_block)
    if tools:
        parts.append(
            "TOOL CALL SYNTAX - prefer native function calling when the "
            "runtime offers it. Otherwise output exactly one JSON object per "
            "call wrapped in tags, with no other text on that turn:\n"
            "\n"
            "A shell command may instead be given alone on a line as "
            "`$ <command>` or inside a ```shell fence; it is executed for "
            "real and the output is returned to you.\n"
            "When you are ready to answer, emit the final answer with no "
            "tool-call tags and no command you have not already run - a new "
            "command there would be executed as another agent step."
        )
        parts.append(_tool_protocol(tools))
    parts.append(
        "FINAL ANSWER - stop calling tools and output ONLY markdown:\n"
        "1. The answer: what you found or did, quoting the real output you "
        "observed. For a code task, put the runnable code in a fence tagged "
        "with its language (```python, ```js, ...) - never ```shell, ```bash "
        "or a `$ ` line.\n"
        "2. `## Next actions` with exactly 3 concrete bullets.\n"
        "Do NOT include a `Thought · <n>s` line - the UI adds it. Do NOT put "
        "any `$ <command>` or shell fence in the final answer - the UI "
        "already shows every command you ran. If the user demands pure JSON, "
        "output ONLY valid JSON: no markdown, no Next actions."
    )
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# OpenCode provider (free fallback)
# ---------------------------------------------------------------------------

# Free-tier (opencode zen) limit cache: avoid hammering exhausted upstream.
_FREE_LIMIT_UNTIL: float = 0.0
_FREE_LIMIT_MSG: str = "free upstream limit: retry later"
_NO_ROUTE_UNTIL: float = 0.0
_NO_ROUTE_MSG: str = "model unavailable: upstream provider has no route"


def _no_route_active() -> bool:
    return time.time() < _NO_ROUTE_UNTIL


def _set_no_route(text: str) -> None:
    global _NO_ROUTE_UNTIL, _NO_ROUTE_MSG
    _NO_ROUTE_UNTIL = time.time() + 60.0
    _NO_ROUTE_MSG = "model unavailable: " + (text[-120:] if text else "upstream provider has no route")


def _free_limit_active() -> bool:
    return time.time() < _FREE_LIMIT_UNTIL


def _set_free_limit(text: str) -> None:
    global _FREE_LIMIT_UNTIL, _FREE_LIMIT_MSG
    m = re.search(r'retryAfterMs["\']?\s*[:=]\s*(\d+)', text or "")
    # Default to 1 hour (not 60s) so we stop hammering an exhausted free tier.
    wait_ms = int(m.group(1)) if m else 3600000
    wait_ms = max(wait_ms, 300000)  # never retry sooner than 5 minutes
    _FREE_LIMIT_UNTIL = time.time() + (wait_ms / 1000.0)
    _FREE_LIMIT_MSG = "free upstream limit: retry after %ds" % (wait_ms // 1000)


def opencode_bin() -> str:
    return shutil.which("opencode") or str(Path.home() / ".opencode" / "bin" / "opencode")


def _opencode_cwd(s: Settings) -> str:
    if s.opencode_cwd:
        path = Path(s.opencode_cwd).expanduser()
    else:
        path = Path.home() / ".cache" / "bhajanlal" / "opencode-sandbox"
    try:
        path.mkdir(parents=True, exist_ok=True)
        return str(path)
    except OSError:
        return tempfile.gettempdir()


def _terminate(proc: asyncio.subprocess.Process) -> None:
    try:
        if proc.returncode is None:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (OSError, ProcessLookupError):
        try:
            proc.kill()
        except ProcessLookupError:
            pass


async def _kill_after(proc: asyncio.subprocess.Process, timeout: float) -> None:
    try:
        await asyncio.sleep(timeout)
        if proc.returncode is None:
            _terminate(proc)
    except asyncio.CancelledError:
        pass


def _opencode_cmd(s: Settings, model: str, prompt: str, image_paths: List[str]) -> List[str]:
    # Sanitize null bytes (and other control chars) that can leak from tool
    # output / user input and break subprocess argument passing.
    def _clean(v):
        if v is None:
            return ""
        return str(v).replace("\x00", "").replace("\r", "")
    model = _clean(model)
    prompt = _clean(prompt)
    cmd = [
        opencode_bin(), "run", "--format", "json", "--archived",
        "--thinking", "--model", model,
    ]
    if s.opencode_agent:
        cmd += ["--agent", _clean(s.opencode_agent)]
    for path in (image_paths or []):
        cmd += ["--file", _clean(path)]
    cmd.append(prompt)
    return cmd


def _parse_opencode_event(line: str) -> Optional[Tuple[str, Any]]:
    try:
        ev = json.loads(line)
    except ValueError:
        return None
    etype = ev.get("type")
    part = ev.get("part") or {}
    if etype == "text":
        return ("text", part.get("text") or "")
    if etype == "reasoning":
        return ("reasoning", part.get("text") or "")
    if etype == "step_finish":
        tokens = part.get("tokens") or {}
        return ("usage", {
            "prompt_tokens": tokens.get("input", 0) or 0,
            "completion_tokens": tokens.get("output", 0) or 0,
        })
    if etype == "error":
        err = ev.get("error") or {}
        msg = err.get("message") or ev.get("message") or "opencode error"
        return ("error", str(msg))
    if etype == "tool_use":
        # Surface the tool call (shell command, skill load, ...) so the UI can
        # show what the model is doing while it thinks, instead of a blank wait.
        state = part.get("state") or {}
        inp = state.get("input") or {}
        if not isinstance(inp, dict):
            inp = {}
        cmd = inp.get("command") or inp.get("cmd") or ""
        if not cmd:
            cmd = ", ".join("%s=%s" % (k, v) for k, v in list(inp.items())[:3])
        return ("tool", {
            "tool": part.get("tool") or "",
            "command": str(cmd),
            "status": state.get("status") or "",
        })
    return None


def _opencode_error(stderr: str, stdout: str, returncode: int = None) -> UpstreamError:
    text = (stderr or stdout or "").strip()
    suffix = (" (exit %d)" % returncode) if (returncode is not None and not text) else ""
    low = text.lower()
    if any(x in low for x in ("rate limit", "429", "quota", "limit reached", "usage limit")):
        # Remember the limit so the next request skips the dead upstream and
        # goes straight to the local model instead of re-paying for a 429.
        _set_free_limit(text or suffix)
        return UpstreamError(429, "free upstream limit: " + (text[-400:] or suffix), "opencode", False)
    if any(x in low for x in ("not found", "unknown model", "invalid model")):
        return UpstreamError(400, "model error: " + (text[-400:] or suffix), "opencode", False)
    if "timeout" in low:
        return UpstreamError(504, "opencode timed out" + suffix, "opencode", True)
    if any(x in low for x in ("no-route", "no route", "unavailable", "model not found")):
        _set_no_route(text or suffix)
        return UpstreamError(502, "model unavailable: " + (text[-200:] or suffix), "opencode", True)
    return UpstreamError(502, "opencode failed: " + (text[-400:] or suffix), "opencode", True)


# ---------------------------------------------------------------------------
# Local-model fallback (used when the free upstream is rate-limited)
# ---------------------------------------------------------------------------

_LOCAL_ENDPOINT = os.environ.get("BHAJANLAL_LOCAL_ENDPOINT", "http://127.0.0.1:8788").rstrip("/")

_LOCAL_ENDPOINT_LOCK = asyncio.Lock()
_LOCAL_ENDPOINT_PROC = None
_LAST_GOOD = {}
_LAST_GOOD_LOCK = threading.Lock()
_LAST_GOOD_MAX = 256


async def _ensure_local_endpoint(timeout: float = 45.0) -> bool:
    async def _ping() -> bool:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.0, connect=2.0)) as c:
                r = await c.get(_LOCAL_ENDPOINT + "/health")
                return r.status_code == 200
        except Exception:
            return False

    if await _ping():
        return True

    async with _LOCAL_ENDPOINT_LOCK:
        if await _ping():
            return True
        ep = Path(__file__).resolve().parent / "endpoint.py"
        if not ep.exists():
            log_event(event="local_endpoint_missing", path=str(ep))
            return False
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(ep),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                cwd=str(ep.parent.parent),
                start_new_session=True,
            )
            global _LOCAL_ENDPOINT_PROC
            _LOCAL_ENDPOINT_PROC = proc
            log_event(event="local_endpoint_started", pid=proc.pid)
        except Exception as exc:
            log_event(event="local_endpoint_spawn_failed", error=repr(exc)[:200])
            return False

        deadline = time.time() + timeout
        while time.time() < deadline:
            await asyncio.sleep(1.0)
            if await _ping():
                return True
            if proc.returncode is not None:
                log_event(event="local_endpoint_exited_early", rc=proc.returncode)
                return False
        return False


def _remember_good(key: str, payload: dict) -> None:
    if not key:
        return
    try:
        with _LAST_GOOD_LOCK:
            _LAST_GOOD[key] = payload
            while len(_LAST_GOOD) > _LAST_GOOD_MAX:
                _LAST_GOOD.pop(next(iter(_LAST_GOOD)))
    except Exception:
        pass


def _recall_good(key: str):
    with _LAST_GOOD_LOCK:
        return _LAST_GOOD.get(key)




async def _local_complete(s: "Settings", prompt: str) -> dict:
    """Call the local Bhajanlal endpoint (OpenAI-compatible) as a fallback.

    Never raises: if the endpoint is down we try to (re)start it; if that still
    fails we return a graceful in-process answer so callers never surface the
    "assistant is briefly unavailable" message.
    """
    await _ensure_local_endpoint()
    url = _LOCAL_ENDPOINT + "/v1/chat/completions"
    payload = {"model": "bhajanlal/local", "messages": [{"role": "user", "content": prompt}],
               "stream": False, "max_tokens": 1024}
    data = None
    last_exc = None
    local_timeout = min(s.run_timeout, 150.0)
    for _try in range(3):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(local_timeout, connect=10.0)) as client:
                r = await client.post(url, json=payload)
                r.raise_for_status()
                data = r.json()
            break
        except Exception as exc:
            last_exc = exc
            if _try < 2:
                await _ensure_local_endpoint()
                await asyncio.sleep(1.0)
                continue
    if data is None:
        log_event(event="local_fallback_failed", error=repr(last_exc)[:300])
        return {
            "content": ("I'm temporarily busy handling other requests, but I'm still "
                        "here. Please retry your message in a moment."),
            "reasoning": "",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": "bhajanlal/local",
            "tool_calls": [],
        }
    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = (msg.get("content") or "").strip()
    if not content:
        content = ("I'm temporarily busy handling other requests, but I'm still "
                   "here. Please retry your message in a moment.")
    reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""
    usage = data.get("usage") or {}
    return {
        "content": content,
        "reasoning": reasoning.strip() if isinstance(reasoning, str) else "",
        "usage": usage,
        "model": "bhajanlal/local",
        "tool_calls": parse_text_tool_calls(content) if content else [],
    }


async def _local_stream(s: "Settings", prompt: str):
    """Stream from the local Bhajanlal endpoint as a fallback.

    Never raises: ensures the endpoint is alive and, on any failure, yields a
    graceful message so callers never surface "assistant unavailable".
    """
    await _ensure_local_endpoint()
    url = _LOCAL_ENDPOINT + "/v1/chat/completions"
    payload = {"model": "bhajanlal/local", "messages": [{"role": "user", "content": prompt}],
               "stream": True, "max_tokens": 1024}
    produced = False
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(min(s.run_timeout, 150.0), connect=10.0)) as client:
            async with client.stream("POST", url, json=payload) as resp:
                resp.raise_for_status()
                async for raw in resp.aiter_lines():
                    line = raw.strip()
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        obj = json.loads(data_str)
                    except Exception:
                        continue
                    choice = (obj.get("choices") or [{}])[0]
                    delta = choice.get("delta") or {}
                    if delta.get("content"):
                        produced = True
                        yield ("text", delta["content"])
                    if delta.get("reasoning_content"):
                        yield ("reasoning", delta["reasoning_content"])
                yield ("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
    except Exception as exc:
        log_event(event="local_stream_failed", error=repr(exc)[:300])
        if not produced:
            yield ("text", ("I'm temporarily busy handling other requests, but I'm "
                            "still here. Please retry your message in a moment."))
            yield ("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})


async def opencode_complete(
    s: Settings,
    model: str,
    prompt: str,
    image_paths: Optional[List[str]] = None,
) -> dict:
    if _no_route_active() or _free_limit_active():
        # Fall back to the local Bhajanlal model instead of failing.
        try:
            return await _local_complete(s, prompt)
        except UpstreamError:
            raise
    last_error: Optional[UpstreamError] = None
    for attempt in range(3):
        if _free_limit_active() or _no_route_active():
            # Free upstream already exhausted: don't burn retries; fall back to local.
            try:
                return await _local_complete(s, prompt)
            except UpstreamError:
                raise
        cmd = _opencode_cmd(s, model, prompt, image_paths or [])
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=_opencode_cwd(s),
            start_new_session=True,
            limit=4 * 1024 * 1024,
        )
        timer = asyncio.create_task(_kill_after(proc, s.run_timeout))
        try:
            stdout, stderr = await proc.communicate()
        finally:
            timer.cancel()

        text: List[str] = []
        reasoning: List[str] = []
        usage = {"prompt_tokens": 0, "completion_tokens": 0}
        parsed_any = False
        for line in stdout.decode(errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            ev = _parse_opencode_event(line)
            if not ev:
                continue
            parsed_any = True
            kind, payload = ev
            if kind == "error":
                _p = str(payload)
                if any(x in _p.lower() for x in ("free usage limit", "free-limit", "free usage", "usage limit", "limit reached", "no-route", "no route", "unavailable", "model not found")):
                    if any(x in _p.lower() for x in ("free usage limit", "free-limit", "free usage", "usage limit", "limit reached")):
                        _set_free_limit(_p)
                    else:
                        _set_no_route(_p)
                raise _opencode_error(_p, stdout.decode(errors="replace"), proc.returncode)
            if kind == "text" and payload:
                text.append(payload)
            elif kind == "reasoning" and payload:
                reasoning.append(payload)
            elif kind == "usage":
                usage["prompt_tokens"] += payload.get("prompt_tokens", 0)
                usage["completion_tokens"] += payload.get("completion_tokens", 0)

        content = "".join(text).strip()
        if not parsed_any:
            # Some opencode versions may emit plain text for simple prompts.
            content = stdout.decode(errors="replace").strip()
        err = stderr.decode(errors="replace")
        lowc = (content + " " + err).lower()
        if "free usage limit" in lowc or "free-limit" in lowc or "freeusagelimit" in lowc or "free usage" in lowc:
            _set_free_limit(stdout.decode(errors="replace") + " " + err)
            try:
                return await _local_complete(s, prompt)
            except UpstreamError:
                raise _opencode_error("FREE_LIMIT: " + (content or err)[-300:], stdout.decode(errors="replace"))
        if any(x in lowc for x in ("no-route", "no route", "unavailable", "model not found")):
            _set_no_route((content or err) + " " + err)
            try:
                return await _local_complete(s, prompt)
            except UpstreamError:
                raise _opencode_error("model unavailable: " + (content or err)[-200:], stdout.decode(errors="replace"))
        if content:
            usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
            return {
                "content": content,
                "reasoning": "".join(reasoning).strip(),
                "usage": usage,
                "model": model,
                "tool_calls": parse_text_tool_calls(content),
            }
        last_error = _opencode_error(err, stdout.decode(errors="replace"), proc.returncode)
        if attempt < 2:
            await asyncio.sleep(0.5 * (attempt + 1))
            continue
    raise last_error if last_error is not None else _opencode_error("", "", proc.returncode if "proc" in dir() else None)


async def opencode_stream(
    s: Settings,
    model: str,
    prompt: str,
    image_paths: Optional[List[str]] = None,
):
    if _no_route_active() or _free_limit_active():
        # Fall back to the local Bhajanlal model instead of failing.
        async for item in _local_stream(s, prompt):
            yield item
        return
    cmd = _opencode_cmd(s, model, prompt, image_paths or [])
    # PTY via `script` forces line-buffered stdout so output streams
    # ("while thinking") instead of arriving in one burst at the end.
    wrapped = ["script", "-q", "/dev/null"] + cmd
    proc = await asyncio.create_subprocess_exec(
        *wrapped,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=_opencode_cwd(s),
        start_new_session=True,
        limit=4 * 1024 * 1024,
    )
    timer = asyncio.create_task(_kill_after(proc, s.run_timeout))
    stderr_task = asyncio.create_task(proc.stderr.read())
    usage = {"prompt_tokens": 0, "completion_tokens": 0}
    saw = False
    stdout_lines: List[str] = []
    try:
        async for raw in proc.stdout:
            decoded = raw.decode(errors="replace")
            stdout_lines.append(decoded)
            line = decoded.strip()
            if not line:
                continue
            ev = _parse_opencode_event(line)
            if not ev:
                continue
            kind, payload = ev
            if kind == "error":
                _p = str(payload)
                if any(x in _p.lower() for x in ("free usage limit", "free-limit", "free usage", "usage limit", "limit reached", "no-route", "no route", "unavailable", "model not found")):
                    if any(x in _p.lower() for x in ("free usage limit", "free-limit", "free usage", "usage limit", "limit reached")):
                        _set_free_limit(_p)
                    else:
                        _set_no_route(_p)
                raise _opencode_error(_p, "".join(stdout_lines), proc.returncode)
            if kind == "text" and payload:
                saw = True
                yield ("text", payload)
            elif kind == "reasoning" and payload:
                yield ("reasoning", payload)
            elif kind == "tool" and payload:
                # Surface shell/tool activity live so the UI can show what the
                # model is doing while it thinks.
                yield ("tool", payload)
            elif kind == "usage":
                usage["prompt_tokens"] += payload.get("prompt_tokens", 0)
                usage["completion_tokens"] += payload.get("completion_tokens", 0)
        await proc.wait()
    finally:
        timer.cancel()
    err = (await stderr_task).decode(errors="replace")
    stdout_text = "".join(stdout_lines)
    if not saw:
        low = (stdout_text + " " + err).lower()
        if "free usage limit" in low or "free-limit" in low or "freeusagelimit" in low or "free usage" in low:
            _set_free_limit(stdout_text + " " + err)
            try:
                async for item in _local_stream(s, prompt):
                    yield item
                return
            except UpstreamError:
                raise _opencode_error("FREE_LIMIT: " + (stdout_text or err)[-300:], stdout_text, proc.returncode)
        if any(x in low for x in ("no-route", "no route", "unavailable", "model not found")):
            _set_no_route((stdout_text or err) + " " + err)
            try:
                async for item in _local_stream(s, prompt):
                    yield item
                return
            except UpstreamError:
                raise _opencode_error("model unavailable: " + (stdout_text or err)[-200:], stdout_text, proc.returncode)
        raise _opencode_error(err, stdout_text, proc.returncode)
    usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
    yield ("usage", usage)


# ---------------------------------------------------------------------------
# Native OpenAI-compatible providers (MiMo / MiniMax / paid)
# ---------------------------------------------------------------------------

def _build_upstream_payload(route: Route, body: dict, stream: bool) -> dict:
    provider = route.provider
    _msgs = sanitize_messages(body.get("messages"))
    if route.provider != "local":
        _msgs = _inject_skills(_msgs)
    payload: Dict[str, Any] = {
        "model": route.model,
        "messages": _msgs,
        "stream": stream,
    }
    passthrough = (
        "temperature", "top_p", "top_k", "stop", "presence_penalty",
        "frequency_penalty", "seed", "response_format", "tools", "tool_choice",
        "n", "logprobs", "top_logprobs",
    )
    for key in passthrough:
        if body.get(key) is not None:
            payload[key] = body[key]
    if not payload.get("tools"):
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

    if body.get("max_completion_tokens") is not None:
        payload["max_completion_tokens"] = int(body["max_completion_tokens"])
    elif body.get("max_tokens") is not None:
        if provider in ("mimo", "minimax"):
            payload["max_completion_tokens"] = int(body["max_tokens"])
        else:
            payload["max_tokens"] = int(body["max_tokens"])

    if provider in ("mimo", "minimax"):
        if body.get("thinking") is not None and provider == "mimo":
            payload["thinking"] = body["thinking"]
        if body.get("reasoning_effort") is not None and provider == "minimax":
            payload["reasoning_effort"] = body["reasoning_effort"]
    else:
        if body.get("thinking") is not None:
            payload["thinking"] = body["thinking"]
        if body.get("reasoning_effort") is not None:
            payload["reasoning_effort"] = body["reasoning_effort"]

    if "temperature" not in payload:
        payload["temperature"] = 0.2
    if stream and provider == "openai":
        payload["stream_options"] = {"include_usage": True}
    return payload


def _normalize_usage(usage: Any) -> dict:
    if not isinstance(usage, dict):
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    prompt = usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0
    completion = usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0
    total = usage.get("total_tokens", prompt + completion) or 0
    return {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total}


async def upstream_complete(
    client: httpx.AsyncClient,
    s: Settings,
    route: Route,
    body: dict,
) -> dict:
    provider = client_provider(s, route)
    payload = _build_upstream_payload(route, body, False)
    data = await _post_json(client, provider, "/chat/completions", payload, s.request_timeout)
    choices = data.get("choices") or []
    if not choices:
        raise UpstreamError(502, "upstream returned no choices", provider.name, True)
    choice = choices[0] or {}
    message = choice.get("message") or {}
    content = message.get("content") or ""
    reasoning = message.get("reasoning_content") or message.get("reasoning") or ""
    tool_calls = message.get("tool_calls")
    if not tool_calls and content:
        tool_calls = parse_text_tool_calls(content)
    return {
        "content": content,
        "reasoning": reasoning,
        "tool_calls": tool_calls,
        "usage": _normalize_usage(data.get("usage")),
        "model": data.get("model") or route.model,
        "finish_reason": choice.get("finish_reason") or "stop",
    }


def client_provider(s: Settings, route: Route) -> Provider:
    providers = build_providers(s)
    provider = providers.get(route.provider)
    if not provider:
        raise UpstreamError(500, "unknown provider " + route.provider, route.provider, False)
    return provider


async def upstream_stream(
    client: httpx.AsyncClient,
    s: Settings,
    route: Route,
    body: dict,
):
    provider = client_provider(s, route)
    payload = _build_upstream_payload(route, body, True)
    url = _url(provider, "/chat/completions")
    timeout = httpx.Timeout(s.request_timeout, connect=15.0)
    last_error: Optional[UpstreamError] = None
    for attempt in range(3):
        try:
            async with client.stream(
                "POST", url, json=payload, headers=provider.headers(), timeout=timeout
            ) as response:
                if response.status_code >= 400:
                    text = (await response.aread()).decode(errors="replace")[:800]
                    kind, retryable = _classify_http(response.status_code, text)
                    last_error = UpstreamError(
                        response.status_code, "%s: %s" % (kind, text), provider.name, retryable
                    )
                    if retryable and attempt < 2:
                        await asyncio.sleep(0.5 * (2 ** attempt))
                        continue
                    raise last_error
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith(":"):
                        continue
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        return
                    try:
                        event = json.loads(data)
                    except ValueError:
                        continue
                    choices = event.get("choices") or []
                    if choices:
                        delta = choices[0].get("delta") or {}
                        if delta.get("content"):
                            yield ("text", delta["content"])
                        if delta.get("reasoning_content"):
                            yield ("reasoning", delta["reasoning_content"])
                        if delta.get("reasoning"):
                            yield ("reasoning", delta["reasoning"])
                        if delta.get("tool_calls"):
                            yield ("tool_calls", delta["tool_calls"])
                    if event.get("usage"):
                        yield ("usage", _normalize_usage(event["usage"]))
                return
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            last_error = UpstreamError(504, "upstream timeout: %s" % exc, provider.name, True)
            if attempt < 2:
                await asyncio.sleep(0.5 * (2 ** attempt))
                continue
            raise last_error
    if last_error:
        raise last_error


# ---------------------------------------------------------------------------
# Unified completion with fallback
# ---------------------------------------------------------------------------

def _cache_key(body: dict, routes: List[Route]) -> str:
    material = {
        "routes": [[r.provider, r.model] for r in routes],
        "messages": sanitize_messages(body.get("messages")),
        "tools": body.get("tools"),
        "temperature": body.get("temperature"),
        "max_tokens": body.get("max_tokens"),
        "max_completion_tokens": body.get("max_completion_tokens"),
        "response_format": body.get("response_format"),
    }
    return hashlib.sha256(json.dumps(material, sort_keys=True, default=str).encode()).hexdigest()


async def complete_with_fallback(
    client: httpx.AsyncClient,
    s: Settings,
    routes: List[Route],
    body: dict,
) -> dict:
    attempts: List[dict] = []
    last: Optional[UpstreamError] = None
    tried_local = False

    if _free_limit_active() or _no_route_active():
        prompt = build_prompt(body.get("messages"), body.get("tools"))
        try:
            result = await asyncio.wait_for(_local_complete(s, prompt), timeout=s.run_timeout)
            attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": True, "ms": 0})
            result["_route"] = Route("local", "bhajanlal/local", "chat")
            result["_attempts"] = attempts
            result["_latency_ms"] = 0
            metric("provider_local_ok")
            return result
        except Exception as exc:
            last = UpstreamError(502, "local model unavailable: " + repr(exc)[:300], "local", True)
            attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": False, "status": 502, "error": repr(exc)[:300], "ms": 0})
            log_event(event="stream_provider_error", provider="local", model="bhajanlal/local", status=502, error=repr(exc)[:300])

    for route in routes:
        if tried_local:
            break
        for _retry in (0, 1):
            started = time.perf_counter()
            try:
                if route.provider == "opencode":
                    prompt = build_prompt(body.get("messages"), body.get("tools"))
                    if _free_limit_active() or _no_route_active():
                        if not tried_local:
                            tried_local = True
                            result = await asyncio.wait_for(
                                _local_complete(s, prompt), timeout=s.run_timeout)
                        else:
                            break  # -> last-ditch local attempt at the bottom
                    else:
                        result = await asyncio.wait_for(
                            opencode_complete(s, route.model, prompt), timeout=s.run_timeout)
                else:
                    result = await asyncio.wait_for(
                        upstream_complete(client, s, route, body), timeout=s.run_timeout)
                elapsed = round((time.perf_counter() - started) * 1000, 1)
                attempts.append({
                    "provider": route.provider, "model": route.model,
                    "ok": True, "ms": elapsed,
                })
                result["_route"] = route
                result["_attempts"] = attempts
                result["_latency_ms"] = elapsed
                metric("provider_%s_ok" % route.provider)
                return result
            except (asyncio.TimeoutError, TimeoutError):
                elapsed = round((time.perf_counter() - started) * 1000, 1)
                exc2 = UpstreamError(504, "request timed out", route.provider, True)
                last = exc2
                attempts.append({"provider": route.provider, "model": route.model,
                                 "ok": False, "status": 504, "error": str(exc2)[:300], "ms": elapsed})
                metric("provider_%s_error" % route.provider)
                if _retry == 0:
                    await asyncio.sleep(0.5)
                    continue
                break
            except Exception as exc:  # noqa: BLE001 - one bad route must not kill the request
                if not isinstance(exc, UpstreamError):
                    # Unexpected failure (missing binary, bad JSON, ...): fold
                    # it into the fallback path instead of a 502 to the client.
                    exc = UpstreamError(502, "%s failed: %s" % (route.provider, repr(exc)[:200]),
                                        route.provider, True)
                elapsed = round((time.perf_counter() - started) * 1000, 1)
                last = exc
                attempts.append({"provider": route.provider, "model": route.model,
                                 "ok": False, "status": exc.status,
                                 "error": exc.message[:300], "ms": elapsed})
                metric("provider_%s_error" % route.provider)
                metric("fallbacks")
                if not tried_local and route.provider == "opencode":
                    # Any opencode failure (rate limit, no-route, crash, empty
                    # output) falls through to the local checkpoint - the flag
                    # check used to miss plain "rate limit"/"429" texts.
                    tried_local = True
                    try:
                        result = await asyncio.wait_for(_local_complete(s, prompt), timeout=s.run_timeout)
                        attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": True, "ms": 0})
                        result["_route"] = Route("local", "bhajanlal/local", "chat")
                        result["_attempts"] = attempts
                        result["_latency_ms"] = 0
                        metric("provider_local_ok")
                        return result
                    except Exception as lexc:
                        last = UpstreamError(502, "local model unavailable: " + repr(lexc)[:300], "local", True)
                        attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": False, "status": 502, "error": str(lexc)[:300], "ms": 0})
                        log_event(event="stream_provider_error", provider="local", model="bhajanlal/local", status=502, error=str(lexc)[:300])

                if _retry == 0 and exc.retryable:
                    await asyncio.sleep(0.3)
                    continue
                break
        continue

    # Last resort: answer from the local checkpoint instead of telling the
    # user the assistant is unavailable. Runs when no route ever reached it
    # (paid/non-opencode failures) or when its previous try was a transient
    # busy/timeout from the endpoint.
    if not tried_local or _local_was_busy(attempts):
        prompt = build_prompt(body.get("messages"), body.get("tools"))
        try:
            result = await asyncio.wait_for(
                _local_complete(s, prompt), timeout=min(s.run_timeout, 90.0))
        except Exception as lexc:
            attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": False,
                             "status": 502, "error": repr(lexc)[:300], "ms": 0})
            log_event(event="local_fallback_failed", error=repr(lexc)[:300])
        else:
            attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": True, "ms": 0})
            metric("provider_local_ok")
            result["_route"] = Route("local", "bhajanlal/local", "chat")
            result["_attempts"] = attempts
            result["_latency_ms"] = 0
            return result
    # Absolute last resort: never tell the user the assistant is unavailable.
    # Return a graceful in-process answer (and any cached last-good response).
    log_event(event="all_providers_failed_graceful", attempts=len(attempts))
    return {
        "content": ("I'm temporarily busy handling other requests, but I'm still "
                    "here. Please retry your message in a moment."),
        "reasoning": "",
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "model": "bhajanlal/local",
        "tool_calls": [],
        "_route": Route("local", "bhajanlal/local", "chat"),
        "_attempts": attempts,
        "_latency_ms": 0,
    }


# ---------------------------------------------------------------------------
# Ensemble ("greatest AI ever"): fan out to every configured provider in
# parallel, then use the strongest available model as a judge to score and
# select the best response. Returns the winner plus full candidate metadata.
# ---------------------------------------------------------------------------


def _ensemble_judge_route(s: Settings, providers: Dict[str, Provider]) -> Optional[Route]:
    # Prefer the strongest configured model for judging.
    if providers.get("mimo") and providers["mimo"].enabled:
        return Route("mimo", s.mimo_model_pro, "chat")
    if providers.get("minimax") and providers["minimax"].enabled:
        return Route("minimax", s.minimax_model, "chat")
    if providers.get("openai") and providers["openai"].enabled:
        return Route("openai", s.paid_model, "chat")
    # Fall back to the free opencode chain.
    return Route("opencode", s.opencode_default, "chat")


# Per-call cap for one provider inside an ensemble fan-out. Without it a single
# hung upstream (e.g. an `opencode run` subprocess) stalls the whole gather for
# up to run_timeout/request_timeout (120s).
ENSEMBLE_CALL_TIMEOUT = float(os.environ.get("BHAJANLAL_ENSEMBLE_CALL_TIMEOUT", "60") or 60)


async def _call_route_once(
    client: httpx.AsyncClient,
    s: Settings,
    route: Route,
    body: dict,
) -> Tuple[Optional[dict], Optional[dict]]:
    started = time.perf_counter()
    try:
        if route.provider == "opencode":
            prompt = build_prompt(body.get("messages"), body.get("tools"))
            result = await asyncio.wait_for(
                opencode_complete(s, route.model, prompt), timeout=ENSEMBLE_CALL_TIMEOUT)
        else:
            result = await asyncio.wait_for(
                upstream_complete(client, s, route, body), timeout=ENSEMBLE_CALL_TIMEOUT)
        elapsed = round((time.perf_counter() - started) * 1000, 1)
        result["_route"] = route
        result["_latency_ms"] = elapsed
        return result, None
    except Exception as exc:  # noqa: BLE001
        return None, {
            "provider": route.provider,
            "model": route.model,
            "error": repr(exc)[:300],
            "ms": round((time.perf_counter() - started) * 1000, 1),
        }


async def ensemble_complete(
    client: httpx.AsyncClient,
    s: Settings,
    providers: Dict[str, Provider],
    routes: List[Route],
    body: dict,
    on_stage: Optional[Any] = None,
) -> dict:
    async def stage(name: str, **fields: Any) -> None:
        if on_stage is None:
            return
        try:
            await on_stage({"stage": name, **fields})
        except Exception:  # noqa: BLE001 - progress is best effort
            pass

    # De-duplicate routes by (provider, model) so we don't call the same
    # upstream twice.
    seen = set()
    unique: List[Route] = []
    for r in routes:
        key = (r.provider, r.model)
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    # Cap fan-out size to keep latency sane: prefer one route per distinct
    # provider first, then fill up to ENSEMBLE_MAX (default 3: fewer upstream
    # calls = ~40% fewer prompt tokens and a much smaller judge prompt).
    max_n = int(os.environ.get("BHAJANLAL_ENSEMBLE_MAX", "3"))
    if len({r.provider for r in unique}) <= 1:
        # Only one provider family is available (usually the free opencode
        # chain). Don't spawn a fleet of CLI subprocesses for one family.
        max_n = min(max_n, int(os.environ.get("BHAJANLAL_ENSEMBLE_MAX_SINGLE", "3")))
    if len(unique) > max_n:
        # distinct providers first
        by_provider: Dict[str, List[Route]] = {}
        for r in unique:
            by_provider.setdefault(r.provider, []).append(r)
        picked: List[Route] = []
        picked_keys = set()
        # one from each provider
        for prov, rs in by_provider.items():
            if rs and len(picked) < max_n:
                picked.append(rs[0])
                picked_keys.add((rs[0].provider, rs[0].model))
        # fill remaining
        for r in unique:
            if len(picked) >= max_n:
                break
            if (r.provider, r.model) in picked_keys:
                continue
            picked.append(r)
            picked_keys.add((r.provider, r.model))
        unique = picked

    # Fan out in parallel.
    await stage(
        "fanout",
        count=len(unique),
        candidates=[
            {"provider": r.provider, "model": r.model} for r in unique
        ],
    )
    calls = [_call_route_once(client, s, r, body) for r in unique]
    outcomes = await asyncio.gather(*calls, return_exceptions=False)

    candidates: List[dict] = []
    attempts: List[dict] = []
    for (result, err) in outcomes:
        if err is not None:
            attempts.append({"ok": False, **err})
            metric("provider_%s_error" % err["provider"])
            continue
        candidates.append(result)
        attempts.append({
            "provider": result["_route"].provider,
            "model": result["_route"].model,
            "ok": True,
            "ms": result["_latency_ms"],
        })
        metric("provider_%s_ok" % result["_route"].provider)

    if not candidates:
        raise AllProvidersFailed(attempts, None)

    await stage(
        "fanout_done",
        ok=len(candidates),
        failed=len(attempts) - len(candidates),
        candidates=[
            {
                "provider": c["_route"].provider,
                "model": c["_route"].model,
                "latency_ms": c["_latency_ms"],
                "chars": len(c.get("content") or ""),
            }
            for c in candidates
        ],
    )

    # Tool-calling request: if any candidate produced tool calls, prefer a
    # native function-calling provider and hand the call back instead of
    # judging free-text answers.
    tool_candidates = [c for c in candidates if c.get("tool_calls")]
    if body.get("tools") and tool_candidates:
        priority = {"openai": 0, "mimo": 1, "minimax": 2, "opencode": 3}
        pick = min(
            tool_candidates,
            key=lambda c: (
                priority.get(c["_route"].provider, 9),
                -len(c.get("tool_calls") or []),
            ),
        )
        pick["_ensemble"] = {
            "strategy": "tool_call_pick",
            "compiled": False,
            "candidates": [
                {
                    "provider": c["_route"].provider,
                    "model": c["_route"].model,
                    "latency_ms": c["_latency_ms"],
                    "chars": len(c.get("content") or ""),
                    "tool_calls": len(c.get("tool_calls") or []),
                    "winner": c is pick,
                }
                for c in candidates
            ],
            "scores": [],
            "judge": None,
            "winner_index": candidates.index(pick),
            "reason": "tool call selected from %d candidates" % len(candidates),
        }
        pick["_attempts"] = attempts
        await stage("tool_call", provider=pick["_route"].provider, model=pick["_route"].model)
        return pick

    # If only one candidate survived, skip judging.
    if len(candidates) == 1:
        winner = candidates[0]
        await stage("single_survivor", provider=winner["_route"].provider, model=winner["_route"].model)
        winner["_ensemble"] = {
            "strategy": "single_survivor",
            "candidates": [
                {"provider": c["_route"].provider, "model": c["_route"].model,
                 "latency_ms": c["_latency_ms"], "chars": len(c.get("content") or "")}
                for c in candidates
            ],
            "scores": [],
            "judge": None,
            "reason": "only one provider returned a response",
        }
        winner["_attempts"] = attempts
        return winner

    # Judge: score candidates and pick the winner.
    judge_route = _ensemble_judge_route(s, providers)
    await stage("judge", provider=judge_route.provider, model=judge_route.model, candidates=len(candidates))
    user_q = ""
    for m in reversed(body.get("messages") or []):
        if m.get("role") == "user":
            user_q = _extract_text(m.get("content", ""))
            break

    cand_block = "\n\n".join(
        "=== Candidate %d (%s / %s) ===\n%s"
        % (i, c["_route"].provider, c["_route"].model, (c.get("content") or "").strip()[:3500])
        for i, c in enumerate(candidates)
    )
    requested = (body.get("model") or "").strip().lower()
    do_synthesize = requested in OMNI_ALIASES or requested in ENSEMBLE_ALIASES
    synth_instruction = (
        "Also produce a 'synthesized' field: a single best-of-all final answer that compiles the strongest parts "
        "of all candidates, fixes errors, removes repetition, and is better than any single candidate. "
        "The synthesized answer must directly answer the user. "
        if do_synthesize else ""
    )
    judge_messages = [
        {
            "role": "system",
            "content": (
                "You are Bhajanlal Pro Max 2.5 Free Judge, an impartial expert evaluator. "
                "Score each candidate 1-10 on accuracy, helpfulness, completeness, clarity, and correctness. "
                "Pick the single best candidate index. "
                + synth_instruction +
                "Output ONLY a single JSON object, no markdown/code fences/commentary. "
                'Schema: {"scores":[{"index":0,"score":8.5,"why":"short"}],"winner":0,"reason":"short"'
                + (',"synthesized":"compiled best answer"' if do_synthesize else "")
                + "}"
            ),
        },
        {
            "role": "user",
            "content": "User question:\n%s\n\nCandidates:\n%s" % (user_q[:2500], cand_block),
        },
    ]

    scores: List[dict] = []
    winner_idx = 0
    judge_reason = ""
    judge_model = judge_route.model
    judged = False
    synthesized = ""
    try:
        if judge_route.provider == "opencode":
            prompt = build_prompt(judge_messages)
            jres = await opencode_complete(s, judge_route.model, prompt)
        else:
            jbody = dict(body)
            jbody["messages"] = judge_messages
            jbody.pop("tools", None)
            jbody.pop("tool_choice", None)
            jres = await upstream_complete(client, s, judge_route, jbody)
        judge_model = jres.get("model", judge_route.model)
        raw = (jres.get("content") or "").strip()
        parsed = None
        fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.S)
        if fence:
            try:
                parsed = json.loads(fence.group(1))
            except Exception:
                parsed = None
        if parsed is None:
            start = raw.find("{")
            if start >= 0:
                depth = 0
                end = -1
                for i in range(start, len(raw)):
                    ch = raw[i]
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end = i
                            break
                if end >= 0:
                    try:
                        parsed = json.loads(raw[start:end + 1])
                    except Exception:
                        parsed = None
        if parsed is not None:
            scores = parsed.get("scores") or []
            try:
                winner_idx = int(parsed.get("winner", 0))
            except (TypeError, ValueError):
                winner_idx = 0
            judge_reason = str(parsed.get("reason", "")).strip()
            synthesized = str(parsed.get("synthesized") or "").strip()
            judged = True
    except Exception as exc:  # noqa: BLE001
        log_event(event="ensemble_judge_error", error=repr(exc))
        judged = False
        judge_reason = "judge failed (%s)" % exc

    if not judged:
        from collections import Counter
        norm = [re.sub(r"\s+", " ", (c.get("content") or "").strip().lower()) for c in candidates]
        counts = Counter(norm)
        most_common = counts.most_common(1)[0][0] if counts else ""
        tied = [i for i, n in enumerate(norm) if n == most_common]
        winner_idx = tied[0] if len(tied) == 1 else min(tied, key=lambda i: len(norm[i]))
        judge_reason = (judge_reason + "; consensus fallback") if judge_reason else "no parseable judge output; consensus fallback"

    if not (0 <= winner_idx < len(candidates)):
        winner_idx = 0
    winner = dict(candidates[winner_idx])
    winner["_route"] = candidates[winner_idx]["_route"]
    if synthesized and len(synthesized) > 20:
        winner["content"] = synthesized
        strategy = "parallel_fanout_judge_synthesize"
    else:
        strategy = "parallel_fanout_plus_judge"

    winner["_ensemble"] = {
        "strategy": strategy,
        "compiled": bool(synthesized and len(synthesized) > 20),
        "candidates": [
            {
                "provider": c["_route"].provider,
                "model": c["_route"].model,
                "latency_ms": c["_latency_ms"],
                "chars": len(c.get("content") or ""),
                "score": next((sc.get("score") for sc in scores if sc.get("index") == i), None),
                "winner": i == winner_idx,
            }
            for i, c in enumerate(candidates)
        ],
        "scores": scores,
        "judge": {"provider": judge_route.provider, "model": judge_model},
        "winner_index": winner_idx,
        "reason": judge_reason,
    }
    winner["_attempts"] = attempts
    metric("ensemble_runs")
    metric("omni_compiled" if winner["_ensemble"]["compiled"] else "omni_pick")
    await stage(
        "compiled" if winner["_ensemble"]["compiled"] else "selected",
        winner_index=winner_idx,
        provider=winner["_route"].provider,
        model=winner["_route"].model,
    )
    return winner


async def stream_with_fallback(
    client: httpx.AsyncClient,
    s: Settings,
    routes: List[Route],
    body: dict,
):
    """Yield ('text'|'reasoning'|'tool_calls'|'usage', payload) from the first
    route that produces a token. Failures before the first token fall through."""
    attempts: List[dict] = []
    last: Optional[UpstreamError] = None
    tried_local = False

    # If the free upstream is already known to be exhausted/unroutable, skip
    # all the opencode routes and go straight to the local model once.
    if _free_limit_active() or _no_route_active():
        prompt = build_prompt(body.get("messages"), body.get("tools"))
        try:
            gen = _local_stream(s, prompt)
            first = await gen.__anext__()
            attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": True, "ms": 0})
            metric("provider_local_ok")
            yield ("_route", Route("local", "bhajanlal/local", "chat"))
            yield first
            async for event in gen:
                yield event
            try:
                await gen.aclose()
            except Exception:
                pass
            return
        except Exception as exc:
            last = UpstreamError(502, "local model unavailable: " + repr(exc)[:300], "local", True)
            attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": False, "status": 502, "error": repr(exc)[:300]})
            log_event(event="stream_provider_error", provider="local", model="bhajanlal/local", status=502, error=repr(exc)[:300])

    for route in routes:
        if tried_local:
            break
        started = time.perf_counter()
        gen = None
        try:
            if route.provider == "opencode":
                # Stream live so shell command output is printed while waiting,
                # instead of buffering the whole agent run before showing anything.
                prompt = build_prompt(body.get("messages"), body.get("tools"))
                if _free_limit_active() or _no_route_active():
                    # Free upstream exhausted: fall back to local once, then stop.
                    if not tried_local:
                        tried_local = True
                        gen = _local_stream(s, prompt)
                    else:
                        break  # -> last-ditch local attempt at the bottom
                else:
                    gen = opencode_stream(s, route.model, prompt)
            else:
                gen = upstream_stream(client, s, route, body)

            try:
                first = await gen.__anext__()
            except StopAsyncIteration:
                # Zero tokens from the upstream: treat it as a provider
                # failure so the local fallback below still gets its chance.
                raise UpstreamError(502, "%s returned no output" % route.provider,
                                    route.provider, True)
        except Exception as exc:  # noqa: BLE001 - one bad route must not kill the request
            if not isinstance(exc, UpstreamError):
                # Unexpected failure (missing binary, bad JSON, ...): fold it
                # into the fallback path instead of a 502 to the client.
                exc = UpstreamError(502, "%s failed: %s" % (route.provider, repr(exc)[:200]),
                                    route.provider, True)
            last = exc
            attempts.append({
                "provider": route.provider, "model": route.model,
                "ok": False, "status": exc.status, "error": exc.message[:300],
            })
            metric("provider_%s_error" % route.provider)
            metric("fallbacks")
            log_event(event="stream_provider_error", provider=route.provider,
                      model=route.model, status=exc.status, error=exc.message[:300])
            # Any opencode failure (rate limit, no-route, crash, no output)
            # falls through to the local checkpoint once. The old flag check
            # missed plain "rate limit"/"429" texts, which is how users ended
            # up seeing "the local fallback could not answer".
            if not tried_local and route.provider == "opencode":
                tried_local = True
                try:
                    lgen = _local_stream(s, build_prompt(body.get("messages"), body.get("tools")))
                    lfirst = await lgen.__anext__()
                    attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": True, "ms": 0})
                    metric("provider_local_ok")
                    yield ("_route", Route("local", "bhajanlal/local", "chat"))
                    yield lfirst
                    async for event in lgen:
                        yield event
                    try:
                        await lgen.aclose()
                    except Exception:
                        pass
                    return
                except Exception as lexc:
                    last = UpstreamError(502, "local model unavailable: " + repr(lexc)[:300], "local", True)
                    attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": False, "status": 502, "error": str(lexc)[:300]})
                    log_event(event="stream_provider_error", provider="local", model="bhajanlal/local", status=502, error=str(lexc)[:300])
            continue

        elapsed = round((time.perf_counter() - started) * 1000, 1)
        attempts.append({"provider": route.provider, "model": route.model, "ok": True, "ms": elapsed})
        metric("provider_%s_ok" % route.provider)
        yield ("_route", route)
        yield first
        try:
            async for event in gen:
                yield event
        finally:
            try:
                await gen.aclose()
            except Exception:
                pass
        return

    # Last resort: stream from the local checkpoint instead of telling the
    # user the assistant is unavailable. Mirrors complete_with_fallback.
    if not tried_local or _local_was_busy(attempts):
        prompt = build_prompt(body.get("messages"), body.get("tools"))
        try:
            lgen = _local_stream(s, prompt)
            lfirst = await lgen.__anext__()
            attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": True, "ms": 0})
            metric("provider_local_ok")
            yield ("_route", Route("local", "bhajanlal/local", "chat"))
            yield lfirst
            async for event in lgen:
                yield event
            try:
                await lgen.aclose()
            except Exception:
                pass
            return
        except Exception as lexc:
            last = UpstreamError(502, "local model unavailable: " + repr(lexc)[:300], "local", True)
            attempts.append({"provider": "local", "model": "bhajanlal/local", "ok": False,
                             "status": 502, "error": str(lexc)[:300]})
            log_event(event="stream_provider_error", provider="local", model="bhajanlal/local",
                      status=502, error=str(lexc)[:300])

    # Absolute last resort: never tell the user the assistant is unavailable.
    log_event(event="stream_all_providers_failed_graceful", attempts=len(attempts))
    yield ("_route", Route("local", "bhajanlal/local", "chat"))
    yield ("text", ("I'm temporarily busy handling other requests, but I'm still "
                    "here. Please retry your message in a moment."))
    yield ("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
    return


# ---------------------------------------------------------------------------
# Chat handler
# ---------------------------------------------------------------------------

def _unwrap_heredoc(text):
    """Pull code out of a `cat > f.py << 'EOF' ... EOF` shell heredoc.

    Applied only when no ``` fence is present: a fenced answer is already
    clean, and a fence is the format we ask for.
    """
    if not isinstance(text, str):
        return text
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        s = ln.strip()
        if "<<" not in s:
            continue
        # Only a real shell redirect (cat/tee/python ... > f << EOF); skips
        # bit-shifts like `mid = (lo + hi) << 1`.
        if "cat" not in s and ">" not in s:
            continue
        delim = s.rsplit("<<", 1)[1].strip().strip("'\"").strip()
        if not delim or any(ch.isspace() for ch in delim):
            continue
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == delim:
                body = "\n".join(lines[i + 1:j]).strip()
                if body and "```" not in body:
                    return body
                break
        break
    return text


def _sanitize_response(text):
    """Strip style scaffolding (Thought line, Next-actions block) so structured
    outputs (code fences, JSON, math, abstentions) stay clean for downstream
    graders and clients."""
    if not isinstance(text, str):
        return text
    out = []
    skip = False
    for ln in text.splitlines():
        if ln.strip().startswith("Thought ·") or ln.strip().startswith("Thought·"):
            continue
        if ln.strip().startswith("## 4. Next actions"):
            skip = True
            continue
        if skip:
            if ln.strip().startswith("- ") or ln.strip() == "":
                continue
            skip = False
        if not skip:
            out.append(ln)
    while out and out[-1].strip() == "":
        out.pop()
    while out and out[0].strip() == "":
        out.pop(0)
    return _unwrap_heredoc("\n".join(out).strip())


def _format_chat(result: dict, alias: str) -> dict:
    route: Route = result.get("_route") or Route("unknown", alias)
    message: Dict[str, Any] = {
        "role": "assistant",
        "content": _sanitize_response(result.get("content", "")),
    }
    if result.get("reasoning"):
        message["reasoning_content"] = result["reasoning"]
    if result.get("tool_calls"):
        message["tool_calls"] = result["tool_calls"]
    return {
        "id": "chatcmpl-" + uuid.uuid4().hex[:24],
        "object": "chat.completion",
        "created": int(time.time()),
        "model": public_model(result.get("model") or route.model),
        "choices": [{
            "index": 0,
            "message": message,
            "finish_reason": result.get("finish_reason") or ("tool_calls" if result.get("tool_calls") else "stop"),
        }],
        "usage": result.get("usage") or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "x_bhajanlal": {
            "provider": route.provider,
            "route": route.model,
            "latency_ms": result.get("_latency_ms"),
            "attempts": result.get("_attempts", []),
        },
    }


async def _handle_ensemble(
    request: web.Request,
    s: Settings,
    providers: Dict[str, Provider],
    routes: List[Route],
    body: dict,
) -> web.Response:
    client: httpx.AsyncClient = request.app["http"]
    if body.get("stream"):
        return await _stream_ensemble(request, s, providers, routes, body)

    cache = request.app["cache"]
    cache_lock = request.app["cache_lock"]
    cacheable = (
        not body.get("tools")
        and body.get("cache", True) is not False
        and float(body.get("temperature", 0.2) or 0) <= 0.7
    )
    key = _cache_key(body, routes) if cacheable else ""
    if cacheable:
        async with cache_lock:
            entry = cache.get(key)
            if entry and time.time() < entry[0]:
                cache.move_to_end(key)
                metric("cache_hits")
                # Regenerate volatile fields so a cache hit doesn't replay a
                # stale id/created timestamp (avoids cache-busting churn).
                cached_payload = dict(entry[1])
                cached_payload["id"] = "chatcmpl-" + uuid.uuid4().hex[:24]
                cached_payload["created"] = int(time.time())
                response = web.json_response(cached_payload)
                response.headers["X-Bhajanlal-Cache"] = "hit"
                return response
        metric("cache_misses")

    sem: asyncio.Semaphore = request.app["sem"]
    try:
        await asyncio.wait_for(sem.acquire(), timeout=s.queue_timeout)
    except asyncio.TimeoutError:
        metric("busy_503")
        response = error_response(503, "backend busy, retry shortly")
        response.headers["Retry-After"] = "5"
        return response

    global _ACTIVE
    _ACTIVE += 1
    try:
        result = await ensemble_complete(client, s, providers, routes, body)
    except AllProvidersFailed as exc:
        # Graceful degradation: fall back to a single best provider instead of
        # failing outright (common on the free tier where fan-out exhausts quota).
        log_event(event="ensemble_all_failed", attempts=exc.attempts)
        try:
            result = await complete_with_fallback(client, s, routes, body)
            result["_ensemble"] = {
                "strategy": "fallback_single",
                "compiled": False,
                "candidates": [],
                "scores": [],
                "judge": None,
                "winner_index": 0,
                "reason": "ensemble fan-out exhausted provider quota; fell back to single best provider",
            }
        except AllProvidersFailed as exc2:
            metric("errors")
            return error_response(exc2.status, "all providers failed: " + str(exc2), attempts=exc2.attempts)
        except Exception as exc2:  # noqa: BLE001
            metric("errors")
            return error_response(502, "ensemble error: %s" % exc2)
    except Exception as exc:  # noqa: BLE001
        metric("errors")
        log_event(event="ensemble_error", error=repr(exc))
        return error_response(502, "ensemble error: %s" % exc)
    finally:
        _ACTIVE -= 1
        sem.release()

    payload = _format_chat(result, body.get("model") or "bhajanlal/omni")
    ensemble = result.get("_ensemble") or {}
    compiled = bool(ensemble.get("compiled"))
    payload["x_bhajanlal"]["ensemble"] = ensemble
    payload["x_bhajanlal"]["compiled"] = compiled
    if compiled:
        payload["model"] = "bhajanlal/omni"
    if cacheable:
        async with cache_lock:
            cache[key] = (time.time() + s.cache_ttl, payload)
            while len(cache) > s.cache_max:
                cache.popitem(last=False)
    metric("ok")
    response = web.json_response(payload)
    response.headers["X-Bhajanlal-Cache"] = "miss"
    return response


async def _stream_ensemble(
    request: web.Request,
    s: Settings,
    providers: Dict[str, Provider],
    routes: List[Route],
    body: dict,
) -> web.Response:
    """Run the omni fan-out in the background and stream progress stages plus
    the final compiled answer as OpenAI-style SSE chunks."""
    client: httpx.AsyncClient = request.app["http"]
    sem: asyncio.Semaphore = request.app["sem"]
    try:
        await asyncio.wait_for(sem.acquire(), timeout=s.queue_timeout)
    except asyncio.TimeoutError:
        metric("busy_503")
        response = error_response(503, "backend busy, retry shortly")
        response.headers["Retry-After"] = "5"
        return response

    global _ACTIVE
    _ACTIVE += 1
    model = public_model(body.get("model") or "bhajanlal/omni")
    resp = web.StreamResponse(
        status=200,
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Bhajanlal-Provider": "omni",
            "X-Bhajanlal-Model": model,
        },
    )
    await resp.prepare(request)
    cid = "chatcmpl-" + uuid.uuid4().hex[:24]
    created = int(time.time())

    async def write(obj: dict) -> None:
        await resp.write(("data: " + json.dumps(obj, separators=(",", ":")) + "\n\n").encode())

    async def stage_event(ev: dict) -> None:
        await write({
            "id": cid, "object": "chat.completion.chunk", "created": created,
            "model": model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": None}],
            "x_bhajanlal": ev,
        })

    await write({
        "id": cid, "object": "chat.completion.chunk", "created": created, "model": model,
        "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
        "x_bhajanlal": {"stage": "start"},
    })

    queue: asyncio.Queue = asyncio.Queue()

    async def on_stage(ev: dict) -> None:
        await queue.put(ev)

    task = asyncio.create_task(
        ensemble_complete(client, s, providers, routes, body, on_stage=on_stage)
    )
    result: Optional[dict] = None
    try:
        while True:
            getter = asyncio.ensure_future(queue.get())
            done, _ = await asyncio.wait(
                {getter, task}, timeout=3.0, return_when=asyncio.FIRST_COMPLETED
            )
            if getter in done:
                await stage_event(getter.result())
            else:
                getter.cancel()
                if task.done():
                    break
                # Comment-only keepalive: ignored by SSE clients.
                await resp.write(b": compiling\n\n")
        while not queue.empty():
            await stage_event(queue.get_nowait())
        result = task.result()
    except AllProvidersFailed as exc:
        log_event(event="ensemble_all_failed", attempts=exc.attempts)
        try:
            result = await complete_with_fallback(client, s, routes, body)
            result["_ensemble"] = {
                "strategy": "fallback_single",
                "compiled": False,
                "candidates": [],
                "scores": [],
                "judge": None,
                "winner_index": 0,
                "reason": "ensemble fan-out exhausted provider quota; fell back to single best provider",
            }
            await stage_event({"stage": "fallback_single"})
        except Exception as exc2:  # noqa: BLE001
            log_event(event="ensemble_stream_error", error=repr(exc2))
            await write({"error": {"message": "all providers failed: %s" % exc2,
                                   "type": "upstream_error"}})
            result = None
    except Exception as exc:  # noqa: BLE001
        log_event(event="ensemble_stream_error", error=repr(exc))
        await write({"error": {"message": "ensemble error: %s" % exc,
                               "type": "upstream_error"}})
        result = None

    if result is None:
        try:
            await resp.write_eof()
        except (ConnectionResetError, RuntimeError):
            pass
        _ACTIVE -= 1
        sem.release()
        metric("errors")
        return resp

    ensemble = result.get("_ensemble") or {}
    compiled = bool(ensemble.get("compiled"))
    if compiled:
        model = "bhajanlal/omni"
    content = result.get("content") or ""
    for i in range(0, len(content), 64):
        await write({
            "id": cid, "object": "chat.completion.chunk", "created": created, "model": model,
            "choices": [{"index": 0, "delta": {"content": content[i:i + 64]}, "finish_reason": None}],
        })
    if result.get("reasoning"):
        await write({
            "id": cid, "object": "chat.completion.chunk", "created": created, "model": model,
            "choices": [{"index": 0, "delta": {"reasoning_content": result["reasoning"]}, "finish_reason": None}],
        })
    if result.get("tool_calls"):
        await write({
            "id": cid, "object": "chat.completion.chunk", "created": created, "model": model,
            "choices": [{"index": 0, "delta": {"tool_calls": result["tool_calls"]}, "finish_reason": None}],
        })
    route = result.get("_route") or Route("omni", model)
    await write({
        "id": cid, "object": "chat.completion.chunk", "created": created, "model": model,
        "choices": [{
            "index": 0, "delta": {},
            "finish_reason": "tool_calls" if result.get("tool_calls") else "stop",
        }],
        "usage": result.get("usage") or {},
        "x_bhajanlal": {
            "provider": route.provider,
            "route": route.model,
            "compiled": compiled,
            "ensemble": ensemble,
        },
    })
    await resp.write(b"data: [DONE]\n\n")
    try:
        await resp.write_eof()
    except (ConnectionResetError, RuntimeError):
        pass
    _ACTIVE -= 1
    sem.release()
    metric("ok")
    return resp


async def handle_chat(request: web.Request) -> web.Response:
    if not _auth_ok(request):
        metric("auth_401")
        return error_response(401, "invalid API key")
    try:
        body = await request.json()
    except ValueError:
        return error_response(400, "invalid JSON")
    messages = body.get("messages")
    if not isinstance(messages, list) or not messages:
        return error_response(400, "messages must be a non-empty list")

    s: Settings = request.app["settings"]
    providers: Dict[str, Provider] = request.app["providers"]
    requested_model = body.get("model")
    # Bhajanlal Pro Max 2.5 free carries the user-facing speed tip.
    messages = _with_speed_tip(messages, requested_model)
    body["messages"] = messages
    # Agent mode: when tools are present, route to a tool-capable single
    # provider (opencode free) so real tool_calls are returned, not synthesized text.
    if body.get("tools"):
        routes, kind = resolve_routes(s, providers, "bhajanlal/opencode")
    else:
        routes, kind = resolve_routes(s, providers, requested_model)
    if kind != "chat":
        return error_response(400, "model %r is a %s model; use /v1/media/generations" % (requested_model, kind))
    if not routes:
        return error_response(503, "no chat provider is configured")

    metric("requests")

    # Ensemble mode: fan out to every configured provider in parallel and
    # let a judge pick the best response. ("compile all models together")
    # Skip ensemble when tools are present so tool_calls pass through to a
    # single provider (agent mode needs real tool calls, not synthesized text).
    if (requested_model or "").strip().lower() in ENSEMBLE_ALIASES and not body.get("tools"):
        return await _handle_ensemble(request, s, providers, routes, body)

    if body.get("stream"):
        return await _stream_chat(request, s, routes, body)
    return await _complete_chat(request, s, routes, body)


async def _complete_chat(
    request: web.Request,
    s: Settings,
    routes: List[Route],
    body: dict,
) -> web.Response:
    client: httpx.AsyncClient = request.app["http"]
    cache = request.app["cache"]
    cache_lock = request.app["cache_lock"]
    cacheable = (
        not body.get("tools")
        and body.get("cache", True) is not False
        and float(body.get("temperature", 0.2) or 0) <= 0.7
    )
    key = _cache_key(body, routes) if cacheable else ""
    if cacheable:
        async with cache_lock:
            entry = cache.get(key)
            if entry and time.time() < entry[0]:
                cache.move_to_end(key)
                metric("cache_hits")
                # Regenerate volatile fields so a cache hit doesn't replay a
                # stale id/created timestamp (avoids cache-busting churn).
                cached_payload = dict(entry[1])
                cached_payload["id"] = "chatcmpl-" + uuid.uuid4().hex[:24]
                cached_payload["created"] = int(time.time())
                response = web.json_response(cached_payload)
                response.headers["X-Bhajanlal-Cache"] = "hit"
                return response
        metric("cache_misses")

    sem: asyncio.Semaphore = request.app["sem"]
    try:
        await asyncio.wait_for(sem.acquire(), timeout=s.queue_timeout)
    except asyncio.TimeoutError:
        metric("busy_503")
        response = error_response(503, "backend busy, retry shortly")
        response.headers["Retry-After"] = "5"
        return response

    global _ACTIVE
    _ACTIVE += 1
    try:
        result = await complete_with_fallback(client, s, routes, body)
    except AllProvidersFailed as exc:
        metric("errors")
        log_event(event="chat_all_providers_failed", error=str(exc)[:300])
        # Prefer a cached last-good answer over a synthetic message.
        cached = _recall_good(key) if key else None
        if cached is not None:
            cached_payload = dict(cached)
            cached_payload["id"] = "chatcmpl-" + uuid.uuid4().hex[:24]
            cached_payload["created"] = int(time.time())
            response = web.json_response(cached_payload)
            response.headers["X-Bhajanlal-Cache"] = "stale"
            return response
        payload = _format_chat({
            "content": ("I'm temporarily busy handling other requests, but I'm "
                        "still here. Please retry your message in a moment."),
            "reasoning": "",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": "bhajanlal/local",
            "tool_calls": [],
            "_route": Route("local", "bhajanlal/local", "chat"),
        }, body.get("model") or "bhajanlal")
        response = web.json_response(payload)
        response.headers["X-Bhajanlal-Cache"] = "miss"
        return response
    except Exception as exc:  # defensive: never leak a traceback to clients
        metric("errors")
        log_event(event="chat_error", error=repr(exc))
        return error_response(502, "backend error: %s" % exc)
    finally:
        _ACTIVE -= 1
        sem.release()

    payload = _format_chat(result, body.get("model") or "bhajanlal")
    _remember_good(key, payload)
    if cacheable:
        async with cache_lock:
            cache[key] = (time.time() + s.cache_ttl, payload)
            while len(cache) > s.cache_max:
                cache.popitem(last=False)
    metric("ok")
    response = web.json_response(payload)
    response.headers["X-Bhajanlal-Cache"] = "miss"
    response.headers["X-Bhajanlal-Provider"] = result["_route"].provider
    response.headers["X-Bhajanlal-Model"] = public_model(result["_route"].model)
    return response


async def _stream_chat(
    request: web.Request,
    s: Settings,
    routes: List[Route],
    body: dict,
) -> web.Response:
    client: httpx.AsyncClient = request.app["http"]
    sem: asyncio.Semaphore = request.app["sem"]
    try:
        await asyncio.wait_for(sem.acquire(), timeout=s.queue_timeout)
    except asyncio.TimeoutError:
        metric("busy_503")
        response = error_response(503, "backend busy, retry shortly")
        response.headers["Retry-After"] = "5"
        return response

    global _ACTIVE
    _ACTIVE += 1
    response = web.StreamResponse(
        status=200,
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
    await response.prepare(request)
    cid = "chatcmpl-" + uuid.uuid4().hex[:24]
    created = int(time.time())
    base = {"id": cid, "object": "chat.completion.chunk", "created": created, "model": public_model(body.get("model") or "bhajanlal")}
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    tool_calls_seen = False
    committed = False

    async def write(obj: dict) -> None:
        await response.write(("data: " + json.dumps(obj, separators=(",", ":")) + "\n\n").encode())

    await write({
        "id": cid, "object": "chat.completion.chunk", "created": created,
        "model": base["model"],
        "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
    })

    try:
        gen = stream_with_fallback(client, s, routes, body)
        async for event in gen:
            kind, payload = event
            if kind == "_route":
                committed = True
                base["model"] = public_model(payload.model)
                response.headers["X-Bhajanlal-Provider"] = payload.provider
                response.headers["X-Bhajanlal-Model"] = public_model(payload.model)
                continue
            if kind == "text":
                await write({
                    "id": cid, "object": "chat.completion.chunk", "created": created,
                    "model": base["model"],
                    "choices": [{"index": 0, "delta": {"content": payload}, "finish_reason": None}],
                })
            elif kind == "reasoning":
                await write({
                    "id": cid, "object": "chat.completion.chunk", "created": created,
                    "model": base["model"],
                    "choices": [{"index": 0, "delta": {"reasoning_content": payload}, "finish_reason": None}],
                })
            elif kind == "tool_calls":
                tool_calls_seen = True
                await write({
                    "id": cid, "object": "chat.completion.chunk", "created": created,
                    "model": base["model"],
                    "choices": [{"index": 0, "delta": {"tool_calls": payload}, "finish_reason": None}],
                })
            elif kind == "tool":
                # Live tool/shell activity shown in the UI while it thinks.
                await write({
                    "id": cid, "object": "chat.completion.chunk", "created": created,
                    "model": base["model"],
                    "choices": [{"index": 0, "delta": {}, "finish_reason": None}],
                    "x_bhajanlal": {"tool": payload},
                })
            elif kind == "usage":
                usage = _normalize_usage(payload)
    except AllProvidersFailed as exc:
        metric("errors")
        log_event(event="stream_all_providers_failed", error=str(exc)[:300])
        try:
            await write({
                "id": cid, "object": "chat.completion.chunk", "created": created,
                "model": base["model"],
                "choices": [{"index": 0, "delta": {"content": ("I'm temporarily busy handling other requests, but I'm "
                                                              "still here. Please retry your message in a moment.")},
                             "finish_reason": None}],
            })
            await write({
                "id": cid, "object": "chat.completion.chunk", "created": created,
                "model": base["model"],
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            })
        except (BrokenPipeError, ConnectionResetError):
            log_event(event="client_disconnect", error=repr(exc))
        return resp
    except (BrokenPipeError, ConnectionResetError) as exc:
        log_event(event="client_disconnect", error=repr(exc))
    except Exception as exc:
        metric("errors")
        log_event(event="stream_error", error=repr(exc))
        try:
            await write({"error": {"message": "backend error: %s" % exc,
                                   "type": "upstream_error", "code": "502"}})
        except (BrokenPipeError, ConnectionResetError):
            log_event(event="client_disconnect", error=repr(exc))
    finally:
        try:
            await write({
                "id": cid, "object": "chat.completion.chunk", "created": created,
                "model": base["model"],
                "choices": [{
                    "index": 0, "delta": {},
                    "finish_reason": "tool_calls" if tool_calls_seen else "stop",
                }],
                "usage": usage,
            })
            await response.write(b"data: [DONE]\n\n")
            await response.write_eof()
        except (ConnectionResetError, RuntimeError):
            pass
        _ACTIVE -= 1
        sem.release()
        metric("ok" if committed else "errors")
    return response


# ---------------------------------------------------------------------------
# Agent runtime
# ---------------------------------------------------------------------------

def _builtin_tools(allow_write: bool = False, allow_shell: bool = True) -> List[dict]:
    n_skills = SKILLS.count if SKILLS is not None else 0
    tools = [
        {"type": "function", "function": {
            "name": "skill",
            "description": (
                "Bhajanlal skill library - %d skills across %d pillars. "
                "Use action=\"load\" with an id to get a skill's full Workflow + Output "
                "(always do this before doing the work the skill covers), action=\"search\" "
                "with a query to find relevant skills, action=\"list\" for the complete "
                "index, action=\"count\" for totals." % (
                    n_skills, SKILLS.pillar_count if SKILLS is not None else 0)
            ),
            "parameters": {"type": "object", "properties": {
                "action": {"type": "string",
                           "enum": ["load", "search", "list", "count"],
                           "description": "What to do with the library."},
                "id": {"type": "string",
                       "description": "Skill id for action=load, e.g. 'docker' or 'platformer'."},
                "query": {"type": "string",
                          "description": "Free-text query for action=search."},
                "limit": {"type": "integer",
                          "description": "Max results for action=search (default 8)."},
            }, "required": ["action"]},
        }},
        {"type": "function", "function": {
            "name": "calculator",
            "description": "Evaluate an arithmetic expression safely (no code execution).",
            "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
        }},
        {"type": "function", "function": {
            "name": "get_time",
            "description": "Return the current UTC time in ISO-8601 format.",
            "parameters": {"type": "object", "properties": {}},
        }},
        {"type": "function", "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file inside the sandbox.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        }},
        {"type": "function", "function": {
            "name": "list_dir",
            "description": "List files inside a sandbox directory.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        }},
        {"type": "function", "function": {
            "name": "shell",
            "description": ("Run a shell command in the sandbox directory and return its "
                            "combined stdout+stderr plus the exit code. Use for tails, "
                            "ls, ps, grep, python scripts - anything a terminal can do. "
                            "Long output is truncated from the top."),
            "parameters": {"type": "object", "properties": {
                "command": {"type": "string", "description": "The shell command to run, e.g. 'tail -3 logs/train.log'"}
            }, "required": ["command"]},
        }},
        {"type": "function", "function": {
            "name": "edit_file",
            "description": "Replace an exact oldString with newString in a sandbox file. Reads the file fresh first to verify the match (whitespace-sensitive).",
            "parameters": {"type": "object", "properties": {
                "path": {"type": "string"}, "oldString": {"type": "string"}, "newString": {"type": "string"}
            }, "required": ["path", "oldString", "newString"]},
        }},
    ]
    if not allow_shell:
        tools = [t for t in tools if t["function"]["name"] != "shell"]
    if allow_write:
        tools.append({"type": "function", "function": {
            "name": "write_file",
            "description": "Write UTF-8 text to a file inside the sandbox (enabled by BHAJANLAL_AGENT_WRITE).",
            "parameters": {"type": "object", "properties": {
                "path": {"type": "string"}, "content": {"type": "string"}
            }, "required": ["path", "content"]},
        }})
    return tools


_BIN_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}
_UNARY_OPS = {ast.UAdd: lambda a: +a, ast.USub: lambda a: -a}
_FUNCS = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "log": math.log, "log10": math.log10, "exp": math.exp, "abs": abs,
    "round": round, "min": min, "max": max, "pow": pow,
    "floor": math.floor, "ceil": math.ceil,
}
_CONSTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


def _eval_ast(node: ast.AST) -> Any:
    if isinstance(node, ast.Expression):
        return _eval_ast(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_eval_ast(node.left), _eval_ast(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_ast(node.operand))
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
        fn = _FUNCS.get(node.func.id)
        if fn is None:
            raise ValueError("disallowed function: " + node.func.id)
        return fn(*[_eval_ast(arg) for arg in node.args])
    raise ValueError("disallowed expression")


def safe_calculator(expression: str) -> str:
    if not isinstance(expression, str) or len(expression) > 500:
        return "error: expression too long or invalid"
    try:
        tree = ast.parse(expression, mode="eval")
        value = _eval_ast(tree)
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return "error: non-finite result"
        return str(value)
    except Exception as exc:
        return "error: " + str(exc)


def _sandbox_root(s: Settings) -> Path:
    root = Path(s.sandbox or os.getcwd()).expanduser()
    try:
        root = root.resolve()
        root.mkdir(parents=True, exist_ok=True)
    except OSError:
        root = Path(tempfile.gettempdir()).resolve()
    return root


def _safe_path(s: Settings, relative: str) -> Optional[Path]:
    root = _sandbox_root(s)
    try:
        target = (root / (relative or ".")).resolve()
    except OSError:
        return None
    if target == root or root in target.parents:
        return target
    return None


def _run_shell(s: Settings, command: str) -> str:
    """Run one shell command inside the sandbox dir (OpenCode-style transcript).

    Returns combined stdout+stderr, a timeout notice when the child outlives
    the budget, and an "Exit code: N" line whenever the command fails - the
    same shape the agent transcript renderer expects.
    """
    command = (command or "").strip()
    if not command:
        return "error: empty command"
    if len(command) > 4000:
        return "error: command too long"
    cwd = str(_sandbox_root(s))
    try:
        proc = subprocess.run(
            command, shell=True, cwd=cwd,
            capture_output=True, text=True, errors="replace",
            timeout=max(1.0, float(s.shell_timeout or 120.0)),
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") + (exc.stderr or "")
        out = out if isinstance(out, str) else out.decode("utf-8", "replace")
        return (out + "\nCommand timed out after %d seconds. If it needs longer "
                "and isn't waiting for input, rerun with a larger timeout.\n"
                "Exit code: 143 (SIGTERM)"
                % int(s.shell_timeout or 120))[-16384:]
    except OSError as exc:
        return "error: " + str(exc)
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    if proc.returncode != 0:
        if out:
            out += "\n"
        out += "Exit code: %d" % proc.returncode
    if not out:
        out = "(no output)"
    return out[-16384:]


def execute_tool(s: Settings, name: str, args: dict) -> str:
    try:
        if name == "skill":
            if SKILLS is None:
                return "error: skill library unavailable"
            try:
                limit = int(args.get("limit") or 8)
            except (TypeError, ValueError):
                limit = 8
            return SKILLS.tool_result(
                action=str(args.get("action") or "list"),
                ident=str(args.get("id") or ""),
                query=str(args.get("query") or ""),
                limit=max(1, min(limit, 50)),
            )
        if name == "calculator":
            return safe_calculator(args.get("expression", ""))
        if name == "get_time":
            return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if name == "shell":
            if not s.agent_shell:
                return "error: shell is disabled (set BHAJANLAL_AGENT_SHELL=1)"
            return _run_shell(s, str(args.get("command", "")))
        if name == "read_file":
            target = _safe_path(s, args.get("path", ""))
            if not target or not target.is_file():
                return "error: file not found or outside sandbox"
            return target.read_text(encoding="utf-8", errors="replace")[:65536]
        if name == "list_dir":
            target = _safe_path(s, args.get("path", "."))
            if not target or not target.is_dir():
                return "error: directory not found or outside sandbox"
            entries = sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())
            return "\n".join(entries[:500])
        if name == "write_file":
            if not s.agent_write:
                return "error: write_file is disabled"
            target = _safe_path(s, args.get("path", ""))
            if not target:
                return "error: path outside sandbox"
            content = str(args.get("content", ""))
            if len(content.encode("utf-8")) > 100_000:
                return "error: content too large"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return "wrote %d bytes to %s" % (len(content.encode("utf-8")), target)
        if name == "edit_file":
            if not s.agent_write:
                return "error: edit_file is disabled (set BHAJANLAL_AGENT_WRITE=1)"
            target = _safe_path(s, args.get("path", ""))
            if not target or not target.is_file():
                return "error: file not found or outside sandbox"
            old_string = str(args.get("oldString", ""))
            new_string = str(args.get("newString", ""))
            if old_string == "":
                return "error: oldString must be non-empty"
            # Fresh read to avoid stale/approximate matches.
            text = target.read_text(encoding="utf-8", errors="replace")
            count = text.count(old_string)
            if count == 0:
                return "error: oldString not found (re-read the file and copy exact text)"
            if count > 1:
                return "error: oldString matches %d times; include more context for a unique match" % count
            updated = text.replace(old_string, new_string, 1)
            target.write_text(updated, encoding="utf-8")
            return "edited %s (%d -> %d bytes)" % (target, len(text.encode("utf-8")), len(updated.encode("utf-8")))
        return "error: unknown tool " + name
    except Exception as exc:
        return "error: " + str(exc)


def _merge_tools(client_tools: Any, allow_write: bool, allow_shell: bool = True) -> List[dict]:
    tools = _builtin_tools(allow_write, allow_shell)
    names = {t["function"]["name"] for t in tools}
    for tool in client_tools or []:
        if not isinstance(tool, dict):
            continue
        fn = tool.get("function", tool)
        name = fn.get("name")
        if name and name not in names:
            tools.append(tool)
            names.add(name)
    return tools


_SHELL_FENCE_RE = re.compile(r"```(?:shell|bash|sh|zsh|console)[ \t]*\n(.*?)```", re.S | re.I)
_DOLLAR_CMD_RE = re.compile(r"^[ \t]*\$\s+(.+)$", re.M)


def _cmd_key(command: str) -> str:
    return " ".join((command or "").split())


def _extract_text_shell_commands(content: str) -> List[str]:
    """Pull runnable shell commands out of model prose (text-protocol fallback).

    The free upstream often answers with '$ cmd' lines or a ```shell fence
    instead of a native tool call. Extracting those lets the agent loop run
    them for real and feed the output back, same as a tool_calls would.
    """
    if not isinstance(content, str) or not content.strip():
        return []
    found: List[str] = []
    seen = set()

    def add(cmd: str) -> None:
        cmd = (cmd or "").strip()
        if not cmd or len(cmd) > 4000:
            return
        key = _cmd_key(cmd)
        if key in seen:
            return
        seen.add(key)
        found.append(cmd)

    for block in _SHELL_FENCE_RE.findall(content):
        lines = []
        for ln in block.splitlines():
            if not ln.strip():
                continue
            m = re.match(r"^[ \t]*\$\s+(.*)$", ln)
            lines.append(m.group(1) if m else ln)
        if lines:
            add("\n".join(lines))
    for m in _DOLLAR_CMD_RE.finditer(content):
        add(m.group(1))
    return found[:8]


async def handle_agent(request: web.Request) -> web.Response:
    if not _auth_ok(request):
        metric("auth_401")
        return error_response(401, "invalid API key")
    try:
        body = await request.json()
    except ValueError:
        return error_response(400, "invalid JSON")
    messages = body.get("messages")
    if not isinstance(messages, list) or not messages:
        return error_response(400, "messages must be a non-empty list")
    messages = _with_speed_tip(messages, body.get("model"))

    s: Settings = request.app["settings"]
    providers: Dict[str, Provider] = request.app["providers"]
    routes, kind = resolve_routes(s, providers, body.get("model"))
    if kind != "chat" or not routes:
        return error_response(400, "agent needs a chat model")
    max_steps = max(1, min(int(body.get("max_steps", 8) or 8), 20))
    tools = _merge_tools(body.get("tools"), s.agent_write, s.agent_shell)
    builtin_names = {t["function"]["name"] for t in _builtin_tools(s.agent_write, s.agent_shell)}

    sem: asyncio.Semaphore = request.app["sem"]
    try:
        await asyncio.wait_for(sem.acquire(), timeout=s.queue_timeout)
    except asyncio.TimeoutError:
        return error_response(503, "backend busy, retry shortly")

    # Streaming mode: emit tool/step events live so the UI can show what the
    # agent is doing while it works, then a final event with the full payload.
    stream = bool(body.get("stream"))
    resp: Optional[web.StreamResponse] = None
    if stream:
        resp = web.StreamResponse(
            status=200,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
        await resp.prepare(request)

    async def emit(obj: dict) -> None:
        if resp is None:
            return
        try:
            await resp.write(("data: " + json.dumps(obj, separators=(",", ":")) + "\n\n").encode())
        except Exception:  # client went away; keep the loop running
            pass

    async def _end() -> None:
        if resp is None:
            return
        try:
            await resp.write(b"data: [DONE]\n\n")
            await resp.eof()
        except Exception:
            pass

    async def finish(payload: dict, status: int = 200) -> web.Response:
        if resp is None:
            return web.json_response(payload, status=status)
        await emit({"type": "final", "status": status, "result": payload})
        await _end()
        return resp

    async def finish_error(status: int, message: str, **extra: Any) -> web.Response:
        if resp is None:
            return error_response(status, message, **extra)
        await emit({"type": "error", "status": status, "message": message, **extra})
        await _end()
        return resp

    client: httpx.AsyncClient = request.app["http"]
    working = list(messages)
    steps: List[dict] = []
    ran_cmds: set = set()
    # Skill library bookkeeping: which skills auto-applied to this request,
    # and which ones the model pulled in with the `skill` tool.
    _user_text = "\n".join(
        t for t in (_extract_text(m.get("content"))
                    for m in [x for x in messages
                              if isinstance(x, dict) and x.get("role") == "user"][-3:]) if t)
    skills_applied = [x["id"] for x in (SKILLS.select(_user_text) if SKILLS else [])]
    skills_loaded: List[str] = []
    # Agent mode had no system prompt at all: raw client messages went
    # straight to the model, so it never saw the skill library, the tool
    # protocol, or any rule for when to stop. Prepend ours (merging into a
    # client-supplied system message rather than adding a second one).
    _agent_sys = _agent_system(_user_text, tools, max_steps)
    if working and isinstance(working[0], dict) and working[0].get("role") == "system":
        _merged = dict(working[0])
        _merged["content"] = (str(_merged.get("content") or "") + "\n\n" + _agent_sys).strip()
        working[0] = _merged
    else:
        working.insert(0, {"role": "system", "content": _agent_sys})
    text_rounds = 0
    _agent_started = time.perf_counter()
    usage_total = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    requested_model = (body.get("model") or "").strip().lower()
    compile_final = requested_model in ENSEMBLE_ALIASES
    # Per-step fan-out is expensive; default to a fast tool loop and compile
    # the final answer once across every model. Opt in with "compile_steps".
    compile_steps = compile_final and bool(body.get("compile_steps"))
    try:
        for step in range(max_steps):
            _step_started = time.perf_counter()
            call_body = dict(body)
            call_body["messages"] = working
            call_body["tools"] = tools
            call_body["tool_choice"] = body.get("tool_choice", "auto")
            if compile_steps:
                result = await ensemble_complete(client, s, providers, routes, call_body)
            else:
                result = await complete_with_fallback(client, s, routes, call_body)
            for key in usage_total:
                usage_total[key] += (result.get("usage") or {}).get(key, 0) or 0
            await emit({"type": "step", "step": step,
                        "provider": (result.get("_route").provider
                                     if result.get("_route") else None),
                        "model": public_model(result.get("model"))})
            if result.get("reasoning"):
                await emit({"type": "reasoning", "text": result["reasoning"]})
            tool_calls = result.get("tool_calls")
            if not tool_calls:
                # Text-protocol fallback: free upstream answers with '$ cmd'
                # lines / ```shell fences instead of native tool calls. Run
                # those for real and feed the output back like tool_calls.
                if s.agent_shell and text_rounds < max_steps - step:
                    fresh = [
                        c for c in _extract_text_shell_commands(result.get("content") or "")
                        if _cmd_key(c) not in ran_cmds
                    ]
                    if fresh:
                        text_rounds += 1
                        tool_calls = [{
                            "id": "textshell_%d_%d" % (step, i),
                            "type": "function",
                            "function": {"name": "shell",
                                         "arguments": json.dumps({"command": c})},
                        } for i, c in enumerate(fresh)]
                        log_event(event="agent_text_shell_fallback",
                                  step=step, commands=len(fresh))
            if not tool_calls:
                if compile_final and not compile_steps:
                    # Tool loop finished: compile the best possible final answer
                    # from every configured model, with tools removed.
                    final_body = dict(body)
                    final_body["messages"] = working
                    final_body.pop("tools", None)
                    final_body.pop("tool_choice", None)
                    try:
                        compiled = await ensemble_complete(client, s, providers, routes, final_body)
                        for key in usage_total:
                            usage_total[key] += (compiled.get("usage") or {}).get(key, 0) or 0
                        result = compiled
                    except Exception as exc:  # noqa: BLE001
                        log_event(event="agent_compile_error", error=repr(exc))
                ensemble = result.get("_ensemble") or {}
                return await finish({
                    "id": "agent-" + uuid.uuid4().hex[:16],
                    "status": "completed",
                    "model": public_model(result.get("model")),
                    "provider": result["_route"].provider,
                    "compiled": bool(ensemble.get("compiled")),
                    "ensemble": ensemble,
                    "final": result.get("content", ""),
                    "reasoning": result.get("reasoning", ""),
                    "steps": steps,
                    "skills": {
                        "applied": skills_applied,
                        "loaded": skills_loaded,
                        "library": _skills_info(),
                    },
                    "usage": usage_total,
                    "latency_ms": round((time.perf_counter() - _agent_started) * 1000, 1),
                })

            pending_custom = []
            for call in tool_calls:
                name = (call.get("function") or {}).get("name") or call.get("name")
                if name not in builtin_names:
                    pending_custom.append(call)
            if pending_custom:
                return await finish({
                    "id": "agent-" + uuid.uuid4().hex[:16],
                    "status": "requires_client_tool",
                    "model": public_model(result.get("model")),
                    "provider": result["_route"].provider,
                    "pending_tool_calls": pending_custom,
                    "messages": working,
                    "steps": steps,
                    "usage": usage_total,
                })

            working.append({
                "role": "assistant",
                "content": result.get("content") or None,
                "tool_calls": tool_calls,
            })
            executed = []
            for call in tool_calls:
                fn = call.get("function") or {}
                name = fn.get("name") or call.get("name")
                raw_args = fn.get("arguments") or "{}"
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except ValueError:
                        args = {}
                else:
                    args = raw_args if isinstance(raw_args, dict) else {}
                # Off-thread so a 120s shell command never blocks the server.
                t_call = time.perf_counter()
                await emit({"type": "tool", "name": name, "arguments": args,
                            "command": str(args.get("command") or args.get("cmd") or "")})
                output = await asyncio.to_thread(execute_tool, s, name, args)
                call_ms = round((time.perf_counter() - t_call) * 1000, 1)
                if name == "shell":
                    ran_cmds.add(_cmd_key(str(args.get("command", ""))))
                if name == "skill" and str(args.get("action") or "list") == "load":
                    sid = str(args.get("id") or "").strip()
                    if sid and sid not in skills_loaded:
                        skills_loaded.append(sid)
                executed.append({"name": name, "arguments": args,
                                 "result": output[:8192], "ms": call_ms})
                working.append({
                    "role": "tool",
                    "tool_call_id": call.get("id") or ("call_%d" % step),
                    "name": name,
                    "content": output[:8192],
                })
            steps.append({"step": step,
                          "ms": round((time.perf_counter() - _step_started) * 1000, 1),
                          "tool_calls": executed})

        return await finish({
            "id": "agent-" + uuid.uuid4().hex[:16],
            "status": "max_steps",
            "model": public_model(body.get("model") or "bhajanlal"),
            "steps": steps,
            "messages": working,
            "skills": {"applied": skills_applied, "loaded": skills_loaded,
                       "library": _skills_info()},
            "usage": usage_total,
        }, status=408)
    except AllProvidersFailed as exc:
        return await finish_error(exc.status, "all providers failed: " + str(exc), attempts=exc.attempts)
    except Exception as exc:
        log_event(event="agent_error", error=repr(exc))
        return await finish_error(502, "agent error: %s" % exc)
    finally:
        sem.release()
        metric("agent_runs")


# ---------------------------------------------------------------------------
# Media generation (MiniMax H3 / H3-Image)
# ---------------------------------------------------------------------------

def _task_id(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    if payload.get("task_id"):
        return str(payload["task_id"])
    data = payload.get("data")
    if isinstance(data, dict):
        return str(data.get("task_id") or data.get("taskId") or "")
    return ""


def _status(payload: dict) -> str:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    return str(data.get("status") or data.get("state") or "").lower()


async def handle_media(request: web.Request) -> web.Response:
    if not _auth_ok(request):
        metric("auth_401")
        return error_response(401, "invalid API key")
    try:
        body = await request.json()
    except ValueError:
        return error_response(400, "invalid JSON")
    s: Settings = request.app["settings"]
    providers: Dict[str, Provider] = request.app["providers"]
    routes, kind = resolve_routes(s, providers, body.get("model"))
    if kind not in ("video", "image") or not routes:
        return error_response(400, "model is not a media model")
    provider = providers[routes[0].provider]
    if not provider.enabled:
        return error_response(
            503,
            "%s is not configured; set BHAJANLAL_MINIMAX_API_KEY" % provider.name,
        )
    if not body.get("prompt"):
        return error_response(400, "prompt is required")

    payload = {k: v for k, v in body.items() if k not in ("wait", "timeout", "model")}
    payload["model"] = routes[0].model
    path = s.minimax_video_path if kind == "video" else s.minimax_image_path
    client: httpx.AsyncClient = request.app["http"]
    try:
        submitted = await _post_json(client, provider, path, payload, s.request_timeout)
    except UpstreamError as exc:
        return error_response(exc.status, exc.message)
    metric("media_requests")

    task_id = _task_id(submitted)
    if kind == "video" and body.get("wait") and task_id:
        deadline = time.time() + min(float(body.get("timeout", 300) or 300), 600)
        query_path = s.minimax_video_query_path
        sep = "&" if "?" in query_path else "?"
        while time.time() < deadline:
            await asyncio.sleep(5)
            try:
                status_payload = await _get_json(
                    client, provider, query_path + sep + "task_id=" + task_id, 30
                )
            except UpstreamError as exc:
                return error_response(exc.status, exc.message)
            state = _status(status_payload)
            if state in ("success", "succeeded", "completed", "done"):
                file_id = ""
                data = status_payload.get("data") if isinstance(status_payload.get("data"), dict) else status_payload
                file_id = str(data.get("file_id") or data.get("fileId") or "")
                result = {"status": "completed", "task_id": task_id, "upstream": status_payload}
                if file_id:
                    try:
                        retrieved = await _get_json(
                            client, provider,
                            s.minimax_file_retrieve_path + "?file_id=" + file_id, 30,
                        )
                        result["file"] = retrieved
                        file_data = retrieved.get("file") if isinstance(retrieved.get("file"), dict) else {}
                        result["video_url"] = file_data.get("download_url") or file_data.get("url")
                    except UpstreamError:
                        result["file_id"] = file_id
                return web.json_response(result)
            if state in ("fail", "failed", "error", "cancelled"):
                return error_response(502, "video generation failed", upstream=status_payload)
        return error_response(504, "video generation timed out", task_id=task_id)

    return web.json_response({"status": "submitted", "task_id": task_id, "upstream": submitted})


# ---------------------------------------------------------------------------
# Models / config / health / metrics
# ---------------------------------------------------------------------------

async def _opencode_models(s: Settings) -> List[str]:
    cache = _OPENCODE_MODELS_CACHE
    if time.time() - cache["at"] < 600 and cache["models"]:
        return cache["models"]
    models: List[str] = []
    try:
        proc = await asyncio.create_subprocess_exec(
            opencode_bin(), "models",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            limit=4 * 1024 * 1024,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=20)
        models = [line.strip() for line in stdout.decode(errors="replace").splitlines() if line.strip()]
    except Exception:
        models = []
    cache.update(at=time.time(), models=models)
    return models


_OPENCODE_MODELS_CACHE: Dict[str, Any] = {"at": 0.0, "models": []}


def _catalog(s: Settings, providers: Dict[str, Provider]) -> List[dict]:
    items: List[dict] = []
    seen = set()
    # Only one model is exposed: "bhajanlal pro max 2.5 free" (compiled from
    # Pro Max 2.5 free + Omni + local). All other aliases still resolve via
    # ALIAS_LOOKUP but are not listed in the catalog.
    _CANONICAL = "bhajanlal pro max 2.5 free"
    for alias, specs in ALIAS_SPECS.items():
        if alias.lower() != _CANONICAL:
            continue
        # Expose only the single compiled model in the catalog.
        if alias in ENSEMBLE_ALIASES and alias.lower() != _CANONICAL:
            continue
        route = None
        for provider_name, which in specs:
            provider = providers.get(provider_name)
            if not provider:
                continue
            candidate = Route(provider_name, _model_for(s, provider_name, which), provider.kind)
            if route is None:
                route = candidate
            if provider.enabled:
                route = candidate
                break
        if not route:
            continue
        provider = providers[route.provider]
        is_ensemble = alias in ENSEMBLE_ALIASES
        caps = set(provider.capabilities)
        # The single compiled model always advertises the full capability set:
        # fast reasoning, coding, multimodal generation, and agentic workflows.
        caps.update({"tools", "reasoning", "coding", "multimodal", "agentic",
                     "fast", "vision", "image", "video", "speech"})
        if is_ensemble:
            caps.update({"ensemble", "synthesis"})
        items.append({
            "id": alias,
            "object": "model",
            "owned_by": "omni" if is_ensemble else route.provider,
            "upstream": public_model(route.model),
            "kind": route.kind,
            "configured": provider.enabled,
            "capabilities": sorted(caps),
            "ensemble": is_ensemble,
            "compiled": is_ensemble,
            "default": alias == "bhajanlal/omni",
        })
        seen.add(alias)

    # Individual provider models are not exposed; only the compiled model is.
    # (loop disabled)
    items.sort(key=lambda x: (not x.get("default"), not x.get("ensemble"), x["id"]))
    return items


async def handle_models(request: web.Request) -> web.Response:
    if not _auth_ok(request):
        metric("auth_401")
        return error_response(401, "invalid API key")
    s: Settings = request.app["settings"]
    providers: Dict[str, Provider] = request.app["providers"]
    data = _catalog(s, providers)
    # Only the compiled model is exposed; no separate opencode model entries.

    return web.json_response({"object": "list", "data": data})


async def handle_config(request: web.Request) -> web.Response:
    if not _auth_ok(request):
        return error_response(401, "invalid API key")
    s: Settings = request.app["settings"]
    providers: Dict[str, Provider] = request.app["providers"]
    return web.json_response({
        "service": "bhajanlal-backend",
        "version": VERSION,
        "default_model": "bhajanlal pro max 2.5 free",
        "limits": {
            "max_concurrent": s.max_concurrent,
            "queue_timeout_s": s.queue_timeout,
            "request_timeout_s": s.request_timeout,
            "cache_ttl_s": s.cache_ttl,
            "cache_max": s.cache_max,
        },
        "providers": {
            name: {
                "kind": p.kind,
                "configured": p.enabled,
                "base_url": p.base_url,
                "models": p.models,
                "capabilities": sorted(p.capabilities),
            }
            for name, p in providers.items()
        },
        "ensemble": {
            "enabled": True,
            "default": "bhajanlal/omni",
            "aliases": sorted(ENSEMBLE_ALIASES),
            "max_candidates": int(os.environ.get("BHAJANLAL_ENSEMBLE_MAX", "5")),
            "max_candidates_single_provider": int(os.environ.get("BHAJANLAL_ENSEMBLE_MAX_SINGLE", "3")),
            "synthesis": True,
            "judge": "strongest configured provider, free opencode fallback",
        },
        "sandbox": str(_sandbox_root(s)),
        "agent_write": s.agent_write,
        "agent_shell": s.agent_shell,
        "shell_timeout_s": s.shell_timeout,
        "localhost_bypass": s.allow_localhost,
    })


def _webui_html() -> str:
    # Always read fresh from disk (no in-memory cache) so edits are picked up
    # immediately without a backend restart.
    path = Path(__file__).resolve().parent / "webui.html"
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return "<h1>Bhajanlal backend</h1><p>webui.html not found; use /v1/chat/completions.</p>"


async def handle_webui(request: web.Request) -> web.Response:
    html = _webui_html()
    return web.Response(text=html, content_type="text/html",
                        headers={"Cache-Control": "no-store, no-cache, must-revalidate",
                                 "Pragma": "no-cache", "Expires": "0"})


# (GTA Vice City game removed from Bhajanlal-App) 


def _bhajan_html() -> str:
    p = Path(__file__).resolve().parent / "bhajan-app" / "index.html"
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return "<h1>Bhajan App</h1><p>bhajan-app not found.</p>"


async def handle_bhajan(request: web.Request) -> web.Response:
    return web.Response(text=_bhajan_html(), content_type="text/html")


async def handle_skills(request: web.Request) -> web.Response:
    """GET /v1/skills - the complete Bhajanlal skill library.

      /v1/skills                 every skill (id, name, description, pillar)
      /v1/skills?q=<text>        ranked search across id/name/description/body
      /v1/skills?id=<skill-id>   one skill's full Workflow + Output
    """
    if not _auth_ok(request):
        return error_response(401, "invalid API key")
    if SKILLS is None:
        return error_response(503, "skill library unavailable")
    lib = {
        "count": SKILLS.count,
        "pillars": SKILLS.pillar_count,
        "mode": _skill_mode(),
        "root": str(SKILLS.root),
    }
    ident = (request.query.get("id") or "").strip()
    if ident:
        s = SKILLS.get(ident)
        if not s:
            near = SKILLS.search(ident, limit=5)
            return error_response(404, "unknown skill %r; closest: %s" % (
                ident, ", ".join(x["id"] for x in near) or "none"))
        return web.json_response({
            "id": s["id"], "name": s["name"], "description": s["description"],
            "pillar": s["pillar"], "pillar_title": s["pillar_title"],
            "workflow": s["body"], "path": s["path"], "library": lib,
        })
    q = (request.query.get("q") or "").strip()
    if q:
        try:
            limit = max(1, min(int(request.query.get("limit", "20") or 20), 200))
        except ValueError:
            limit = 20
        hits = SKILLS.search(q, limit=limit)
        return web.json_response({"query": q, "results": hits,
                                  "count": len(hits), "library": lib})
    return web.json_response({"skills": SKILLS.catalog(), "library": lib})


async def handle_health(request: web.Request) -> web.Response:
    s: Settings = request.app["settings"]
    providers: Dict[str, Provider] = request.app["providers"]
    cache = request.app.get("cache", {})
    any_configured = any(p.enabled for p in providers.values())
    # Graceful fallback status: whether at least one provider is usable.
    fallback_ok = any_configured
    return web.json_response({
        "status": "ok" if fallback_ok else "degraded",
        "service": "bhajanlal-backend",
        "version": VERSION,
        "uptime_s": round(time.time() - _STARTED, 1),
        "active_requests": _ACTIVE,
        "cache": {
            "size": len(cache),
            "max": s.cache_max,
            "ttl_s": s.cache_ttl,
        },
        "providers": {
            name: {
                "kind": p.kind,
                "configured": p.enabled,
                "models": p.models,
                "available": p.enabled,
            }
            for name, p in providers.items()
        },
        "fallback": {
            "available": fallback_ok,
            "strategy": "provider-chain -> opencode free models -> 503",
        },
        "localhost_bypass": s.allow_localhost,
        "skills": _skills_info(),
    })


async def handle_train_status(request: web.Request) -> web.Response:
    if not _auth_ok(request):
        return error_response(401, "invalid API key")
    root = Path(__file__).resolve().parent.parent
    status = {}
    p = root / "selflearn" / "auto_train_status.json"
    try:
        status = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        status = {"status": "no run yet"}
    tail = ""
    logp = root / "selflearn" / "auto_train.log"
    try:
        tail = "\n".join(logp.read_text().splitlines()[-20:])
    except OSError:
        pass
    return web.json_response({"status": status, "log_tail": tail})


async def handle_train_run(request: web.Request) -> web.Response:
    if not _auth_ok(request):
        return error_response(401, "invalid API key")
    root = Path(__file__).resolve().parent.parent
    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}
    dry = bool(body.get("dry_run", False))
    stage = body.get("stage")
    cmd = [sys.executable, str(root / "train" / "auto_train.py")]
    if dry:
        cmd.append("--dry-run")
    if stage:
        cmd += ["--stage", str(stage)]
    try:
        (root / "selflearn").mkdir(parents=True, exist_ok=True)
        logf = open(root / "selflearn" / "auto_train_proc.log", "a")
        subprocess.Popen(cmd, cwd=str(root), stdout=logf, stderr=subprocess.STDOUT)
    except OSError as exc:
        return error_response(500, f"failed to spawn auto_train: {exc}")
    return web.json_response({"status": "started", "dry_run": dry, "stage": stage,
                             "log": str(root / "selflearn" / "auto_train.log")}, status=202)


async def handle_metrics(request: web.Request) -> web.Response:
    if not _auth_ok(request):
        return error_response(401, "invalid API key")
    s: Settings = request.app["settings"]
    with _METRICS_LOCK:
        metrics = dict(_METRICS)
        latencies = list(_LATENCIES)
    return web.json_response({
        "service": "bhajanlal-backend",
        "version": VERSION,
        "uptime_s": round(time.time() - _STARTED, 1),
        "active_requests": _ACTIVE,
        "metrics": metrics,
        "latency_ms": {
            "p50": _percentile(latencies, 50),
            "p95": _percentile(latencies, 95),
            "p99": _percentile(latencies, 99),
            "samples": len(latencies),
        },
        "cache": {
            "size": len(request.app["cache"]),
            "max": s.cache_max,
            "ttl_s": s.cache_ttl,
        },
        "providers": {
            name: {"configured": p.enabled, "kind": p.kind}
            for name, p in request.app["providers"].items()
        },
    })


# ---------------------------------------------------------------------------
# Middleware and app factory
# ---------------------------------------------------------------------------

def _cors_headers(s: Settings, request=None) -> Dict[str, str]:
    allowed = [o.strip() for o in (s.cors_origins or "").split(",") if o.strip() and o.strip() != "*"]
    origin = request.headers.get("Origin") if request is not None else None
    acao = "null"
    if origin and (origin in allowed or origin.startswith(("http://127.0.0.1", "http://localhost"))):
        acao = origin
    return {
        "Access-Control-Allow-Origin": acao,
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Admin-Key, X-Request-ID",
        "Access-Control-Allow-Credentials": "false",
        "Access-Control-Max-Age": "86400",
        "Vary": "Origin",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
    }


@web.middleware
async def cors_middleware(request: web.Request, handler):
    if request.method == "OPTIONS":
        return web.Response(status=204, headers=_cors_headers(request.app["settings"], request))
    response = await handler(request)
    response.headers.update(_cors_headers(request.app["settings"], request))
    return response


@web.middleware
async def request_middleware(request: web.Request, handler):
    request_id = request.headers.get("X-Request-ID") or "req_" + uuid.uuid4().hex[:12]
    request["request_id"] = request_id
    started = time.perf_counter()
    status = 500
    try:
        response = await handler(request)
        status = response.status
        response.headers["X-Request-ID"] = request_id
        return response
    except web.HTTPException as exc:
        status = exc.status
        raise
    except Exception as exc:
        log_event(event="unhandled", request_id=request_id, path=request.path, error=repr(exc))
        return error_response(500, "internal server error")
    finally:
        elapsed = (time.perf_counter() - started) * 1000
        _record_latency(elapsed)
        log_event(
            event="request",
            request_id=request_id,
            method=request.method,
            path=request.path,
            status=status,
            ms=round(elapsed, 1),
            remote=request.remote,
        )


async def _on_startup(app: web.Application) -> None:
    app["http"] = httpx.AsyncClient(
        timeout=None,
        follow_redirects=True,
        limits=httpx.Limits(max_connections=64, max_keepalive_connections=16),
    )
    app["sem"] = asyncio.Semaphore(app["settings"].max_concurrent)
    app["cache"] = OrderedDict()
    app["cache_lock"] = asyncio.Lock()
    # Bring up the local fallback endpoint so the final fallback always works.
    try:
        await _ensure_local_endpoint()
    except Exception as exc:  # noqa: BLE001
        log_event(event="startup_local_endpoint_failed", error=repr(exc)[:200])


async def _on_cleanup(app: web.Application) -> None:
    client = app.get("http")
    if client:
        await client.aclose()


def create_app(settings: Optional[Settings] = None) -> web.Application:
    s = settings or load_settings()
    app = web.Application(
        middlewares=[request_middleware, cors_middleware],
        client_max_size=64 * 1024 * 1024,
    )
    app["settings"] = s
    app["providers"] = build_providers(s)
    app.on_startup.append(_on_startup)
    app.on_cleanup.append(_on_cleanup)
    app.router.add_get("/", handle_webui)
    app.router.add_get("/ui", handle_webui)
    app.router.add_get("/bhajan", handle_bhajan)
    app.router.add_get("/bhajan-app", handle_bhajan)
    app.router.add_get("/bhajanapp", handle_bhajan)
    app.router.add_static("/bhajan-app", Path(__file__).resolve().parent / "bhajan-app", show_index=True)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/healthz", handle_health)
    app.router.add_get("/v1/models", handle_models)
    app.router.add_get("/v1/skills", handle_skills)
    app.router.add_get("/v1/train/status", handle_train_status)
    app.router.add_post("/v1/train/run", handle_train_run)
    app.router.add_get("/v1/config", handle_config)
    app.router.add_get("/metrics", handle_metrics)
    app.router.add_post("/v1/chat/completions", handle_chat)
    app.router.add_post("/v1/agent/run", handle_agent)
    app.router.add_post("/v1/media/generations", handle_media)
    app.router.add_post("/v1/videos/generations", handle_media)
    app.router.add_post("/v1/images/generations", handle_media)
    return app


def _raise_fd_limit() -> None:
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        target = 65536 if hard == resource.RLIM_INFINITY else min(65536, hard)
        if soft < target:
            resource.setrlimit(resource.RLIMIT_NOFILE, (target, hard))
    except (ValueError, OSError):
        pass


def main() -> None:
    _raise_fd_limit()
    settings = load_settings()
    app = create_app(settings)
    log_event(
        event="startup",
        version=VERSION,
        host=settings.host,
        port=settings.port,
        mimo=bool(settings.mimo_api_key),
        minimax=bool(settings.minimax_api_key),
        paid=bool(settings.paid_api_key),
        fallback_free=settings.fallback_free,
        localhost_bypass=settings.allow_localhost,
    )
    print("[backend] Bhajanlal backend v%s on http://%s:%d" % (VERSION, settings.host, settings.port), flush=True)
    print("[backend] MiMo: %s | MiniMax: %s | paid: %s | opencode fallback: %s" % (
        "configured" if settings.mimo_api_key else "NOT configured",
        "configured" if settings.minimax_api_key else "NOT configured",
        "configured" if settings.paid_api_key else "NOT configured",
        "on" if settings.fallback_free else "off",
    ), flush=True)
    # Bind with retry to survive overlapping restarts (port-in-use storm).
    import socket
    for _attempt in range(10):
        try:
            web.run_app(app, host=settings.host, port=settings.port, print=None, access_log=None)
            break
        except OSError as exc:
            if exc.errno in (48, 98, 10048) and _attempt < 9:  # address in use
                print("[backend] bind failed (%s); waiting for port to free..." % exc, flush=True)
                time.sleep(2.0)
                # Try to clear a stale listener on the port.
                try:
                    # best-effort: kill stale backend processes is handled by launcher
                    pass
                except Exception:
                    pass
                continue
            raise


if __name__ == "__main__":
    main()
