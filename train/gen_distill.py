#!/usr/bin/env python3
"""Distill high-quality responses from the Bhajanlal Pro Max 2.5 Free ensemble
into training data for the local 0.5B student model.

For each skill-derived prompt, calls the running backend (ensemble) to get a
high-quality response and writes data_distilled.jsonl. Requires the backend
to be running at BHAJANLAL_BACKEND_URL.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
URL = os.environ.get("BHAJANLAL_BACKEND_URL", "http://127.0.0.1:8796").rstrip("/")
OUT = Path(__file__).resolve().parent / "data_distilled.jsonl"
SKILLS = ROOT / ".opencode" / "skills"


def call_ensemble(prompt):
    body = {
        "model": "bhajanlal/pro-max-2.5-free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 256,
        "temperature": 0.2,
    }
    req = urllib.request.Request(URL + "/v1/chat/completions",
                                data=json.dumps(body).encode(),
                                headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
            return d["choices"][0]["message"].get("content", "")
    except Exception as e:
        return ""


def main():
    rows = []
    # skill prompts
    prompts = []
    if SKILLS.exists():
        for d in sorted(SKILLS.iterdir()):
            p = d / "SKILL.md"
            if not p.exists():
                continue
            import re
            text = p.read_text(encoding="utf-8")
            nm = re.search(r"^name:\s*(.+)$", text, re.M)
            name = nm.group(1).strip() if nm else d.name
            prompts.append(f"Explain and apply the {name} technique.")
    # limit to keep runtime sane
    prompts = prompts[:200]
    for i, pr in enumerate(prompts):
        resp = call_ensemble(pr)
        if resp and len(resp) > 20:
            rows.append({"instruction": pr, "response": resp, "quadrant": "reasoning"})
        if (i + 1) % 20 == 0:
            print(f"distilled {i+1}/{len(prompts)}", flush=True)
            time.sleep(0.5)
    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                   encoding="utf-8")
    print(f"Wrote {len(rows)} distilled rows to {OUT}")


if __name__ == "__main__":
    main()