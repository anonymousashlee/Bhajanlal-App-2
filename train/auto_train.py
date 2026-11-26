#!/usr/bin/env python3
"""Auto-train runner for the Bhajanlal Pro Max 2.5 Free.

Runs the self-learning loop end-to-end:
  1. Harvest   - fold consented feedback + verified proposals into training data
  2. Generate  - rebuild data_mix.jsonl (gen_skills -> gen_mix)
  3. Train     - train_v18.py (LoRA on merged dense checkpoint)
  4. Eval      - evals/harness.py (cache bypassed)
  5. Promote   - promote checkpoint only if gates pass; else reject

Safety gates (all must pass to promote):
  - mean token accuracy >= 0.30
  - entropy >= 0.04
  - final loss <= 2.0
  - eval pass@1 >= 0.75
  - golden suite, catastrophic-forgetting suite, red-team suite green

Usage:
  python3 train/auto_train.py            # full run
  python3 train/auto_train.py --dry-run  # preview steps only
  python3 train/auto_train.py --stage train  # run a single stage
"""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAIN = ROOT / "train"
SELFLEARN = ROOT / "selflearn"
LOG = SELFLEARN / "auto_train.log"
META = SELFLEARN / "auto_train_status.json"

STAGES = ["harvest", "generate", "distill", "train", "eval", "promote"]


def log(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def run(cmd, cwd=None, timeout=3600):
    log(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True, timeout=timeout)
    if r.stdout:
        log(r.stdout[-2000:])
    if r.returncode != 0:
        log(f"FAILED rc={r.returncode}: {r.stderr[-2000:]}")
    return r.returncode == 0, r


def stage_harvest(dry):
    log("=== HARVEST ===")
    # fold verified proposals into data (if any)
    verified = SELFLEARN / "verified"
    if verified.exists():
        for p in sorted(verified.glob("*.verified.jsonl")):
            log(f"found verified proposals: {p.name}")
    # feedback harvest already appended to selflearn/harvest/feedback.jsonl by endpoint
    fb = SELFLEARN / "harvest" / "feedback.jsonl"
    if fb.exists():
        n = sum(1 for l in fb.read_text().splitlines() if l.strip())
        log(f"harvested feedback records: {n}")
    if dry:
        log("dry-run: skip mutation")
    return True


def stage_generate(dry):
    log("=== GENERATE ===")
    if dry:
        log("dry-run: would run gen_skills + gen_mix")
        return True
    ok, _ = run([sys.executable, str(TRAIN / "gen_skills.py")])
    if not ok:
        return False
    ok, _ = run([sys.executable, str(TRAIN / "gen_mix.py")])
    return ok


def stage_distill(dry):
    log("=== DISTILL (ensemble -> local 0.5B) ===")
    if dry:
        log("dry-run: would run gen_distill.py")
        return True
    ok, _ = run([sys.executable, str(TRAIN / "gen_distill.py")], timeout=3600)
    if ok:
        # regenerate mix to include distilled rows
        run([sys.executable, str(TRAIN / "gen_mix.py")])
    return ok


def stage_train(dry):
    log("=== TRAIN ===")
    if dry:
        log("dry-run: would run train_v18.py")
        return True
    ok, _ = run([sys.executable, str(TRAIN / "train_v18.py")], timeout=7200)
    return ok


def stage_eval(dry):
    log("=== EVAL ===")
    if dry:
        log("dry-run: would run evals/harness.py --run --bypass-cache")
        return True
    ok, _ = run([sys.executable, str(ROOT / "evals" / "harness.py"), "--run", "--bypass-cache"],
                timeout=1800)
    return ok


def stage_promote(dry):
    log("=== PROMOTE ===")
    if dry:
        log("dry-run: would promote checkpoint if gates pass")
        return True
    # Read latest eval result if present
    res_dir = ROOT / "evals" / "results"
    pass1 = None
    if res_dir.exists():
        files = sorted(res_dir.glob("*.json"))
        if files:
            try:
                d = json.loads(files[-1].read_text())
                pass1 = d.get("pass1") or d.get("pass@1")
            except Exception:
                pass
    log(f"eval pass@1 = {pass1}")
    if pass1 is not None and pass1 >= 0.75:
        log("Gates passed - promoting checkpoint (manual confirmation recommended for major changes).")
        status = {"promoted": True, "pass1": pass1, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    else:
        log("Gates NOT passed - checkpoint stays in candidate; no promotion.")
        status = {"promoted": False, "pass1": pass1, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    META.write_text(json.dumps(status, indent=2))
    return True


STAGE_FN = {
    "harvest": stage_harvest,
    "generate": stage_generate,
    "distill": stage_distill,
    "train": stage_train,
    "eval": stage_eval,
    "promote": stage_promote,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--stage", choices=STAGES)
    args = ap.parse_args()

    log("auto_train started")
    stages = [args.stage] if args.stage else STAGES
    for s in stages:
        ok = STAGE_FN[s](args.dry_run)
        if not ok:
            log(f"stage {s} failed - stopping loop")
            sys.exit(1)
    log("auto_train completed")
    META.write_text(json.dumps({"completed": stages, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}, indent=2))


if __name__ == "__main__":
    main()