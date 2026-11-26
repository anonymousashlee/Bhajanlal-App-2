#!/usr/bin/env python3
"""Generate training rows from the Bhajanlal skill library (including God's Eye View skills).

Converts every SKILL.md under .opencode/skills into instruction/response pairs so
the model learns the techniques in the library (super-resolution, denoising,
deblurring, low-light, weather clearing, geometric rectification, car/human
detection). Output: train/data_skills.jsonl (picked up by gen_mix.py).
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".opencode" / "skills"
OUT = Path(__file__).resolve().parent / "data_skills.jsonl"

_FRONT = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
_NAME = re.compile(r"^name:\s*(.+)$", re.M)
_DESC = re.compile(r"^description:\s*(.+)$", re.M)


def parse_skill(text):
    fm = _FRONT.match(text)
    meta = fm.group(1) if fm else ""
    name_m = _NAME.search(meta)
    desc_m = _DESC.search(meta)
    name = name_m.group(1).strip() if name_m else ""
    desc = desc_m.group(1).strip() if desc_m else ""
    body = text[fm.end():] if fm else text
    # extract workflow + output
    wf = ""
    out = ""
    if "## Workflow" in body:
        wf = body.split("## Workflow", 1)[1].split("## Output", 1)[0].strip()
    if "## Output" in body:
        out = body.split("## Output", 1)[1].strip()
    return name, desc, wf, out


def rows_for(name, desc, wf, out):
    if not name or not wf:
        return []
    r = []
    r.append({
        "instruction": f"How do I apply the {name} technique to improve image clarity or detect cars and humans?",
        "response": (f"Apply {name}: {desc}\n\nWorkflow:\n{wf}\n\n"
                     f"Expected output: {out}"),
    })
    r.append({
        "instruction": f"Explain the {name} algorithm and when to use it in a God's Eye View pipeline.",
        "response": f"{name} — {desc}\n\nSteps:\n{wf}\n\nResult: {out}",
    })
    return r


def main():
    all_rows = []
    seen = set()
    for d in sorted(SKILLS.iterdir()):
        if not d.is_dir():
            continue
        p = d / "SKILL.md"
        if not p.exists():
            continue
        name, desc, wf, out = parse_skill(p.read_text(encoding="utf-8"))
        for row in rows_for(name, desc, wf, out):
            key = (row["instruction"], row["response"])
            if key in seen:
                continue
            seen.add(key)
            all_rows.append(row)
    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in all_rows) + "\n",
                   encoding="utf-8")
    print(f"Wrote {len(all_rows)} skill-derived rows to {OUT}")


if __name__ == "__main__":
    main()