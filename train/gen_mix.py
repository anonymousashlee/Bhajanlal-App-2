"""4-quadrant retraining mix generator.

Balances the fine-tuning dataset across the four capability quadrants at:
  35% Coding & Verification
  25% Agentic Tool-Use & Recovery
  20% Fast Compressed Reasoning
  20% Multimodal Generation & Visual Inspection

Reads all data*.jsonl (dedup), classifies each row by keyword, then
resamples (with replacement where needed) to the exact target mix.
Writes data_mix.jsonl + metadata_mix.json.
"""
import json
import glob
import random
from pathlib import Path

TRAIN = Path(__file__).resolve().parent
random.seed(2502)  # deterministic mix

TARGET = {
    "coding": 0.30,
    "agentic": 0.25,
    "reasoning": 0.30,
    "multimodal": 0.15,
}

KW = {
    "coding": {"code","function","test","debug","bug","refactor","python",
               "typescript","javascript","sql","api","compile","lint","type",
               "stacktrace","exception","regex","class","import","git","commit",
               "deploy","docker","schema","endpoint","backend","frontend"},
    "multimodal": {"image","video","audio","screenshot","render","design",
                   "color","font","layout","ui","ux","svg","png","gif","chart",
                   "visual","animation","voice","tts","music","poster","logo",
                   "theme","css","html","wireframe","mockup","frame","camera"},
    "agentic": {"tool","agent","workflow","skill","session","parallel","plan",
                "sandbox","mcp","pipeline","retry","checkpoint","delegate",
                "subagent","orchestrat","harness","loop","spawn","automation"},
    "reasoning": {"reason","logic","hypothesis","analy","quick","fast","terse",
                  "concise","compress","priority","decision","tradeoff",
                  "ambigu","estimate","simpl","minimal","steps","explain"},
}


def classify(row):
    toks = set(str(row.get("instruction","")).lower().split()) | \
           set(str(row.get("response","")).lower().split())
    best, best_n = "reasoning", 0
    for quad, kw in KW.items():
        n = sum(1 for t in toks if any(k in t for k in kw))
        if n > best_n:
            best, best_n = quad, n
    return best


def main():
    seen, rows = set(), []
    for f in sorted(glob.glob(str(TRAIN / "data*.jsonl"))):
        if f.endswith("data_mix.jsonl"):
            continue
        for line in open(f):
            line = line.strip()
            if not line or line in seen:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if row.get("instruction") and row.get("response"):
                # Skip rows that leak raw template markup into training data —
                # these cause the model to emit template tokens at inference.
                _resp = str(row.get("response", ""))
                _inst = str(row.get("instruction", ""))
                if "### Instruction" in _resp or "### Instruction" in _inst:
                    continue
                if "\U000f0002" in _resp or "\U000f0002" in _inst:
                    continue
                if "Thought ·" in _resp and "###" in _resp:
                    continue
                seen.add(line)
                rows.append(row)

    buckets = {q: [] for q in TARGET}
    for r in rows:
        buckets[classify(r)].append(r)

    total = len(rows)
    out = []
    stats = {}
    for quad, share in TARGET.items():
        want = round(total * share)
        pool = buckets[quad] or rows  # fallback: any rows
        picked = [pool[i % len(pool)] for i in range(want)]
        for r in picked:
            out.append({**r, "quadrant": quad})
        stats[quad] = want

    random.shuffle(out)
    (TRAIN / "data_mix.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n")
    meta = {
        "mix": TARGET,
        "counts": stats,
        "total": len(out),
        "source_rows": total,
        "note": "4-quadrant balanced retraining mix (coding 30 / agentic 25 / "
                "reasoning 30 / multimodal 15)",
    }
    (TRAIN / "metadata_mix.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
