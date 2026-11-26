#!/usr/bin/env python3
"""Bhajanlal v18: 4-quadrant balanced LoRA fine-tune on top of bhajanlal-pro-max-2.

Trains on data_mix.jsonl (35% coding / 25% agentic / 20% fast reasoning /
20% multimodal) so all four capability quadrants are balanced.

Fixes the three root causes found in the v17 -> v18 quadrant-mix run (local pass@1
0.389, all 6 code cases failing):

  1. Train/infer system-prompt mismatch: training uses the SAME `_STYLE` prompt
     that serve/endpoint.py injects at inference time.
  2. Zero fenced code in training data: every code response in data_mix.jsonl is
     exactly the fenced block the eval prompts ask for.
  3. Ungrounded logic: every code sample in data_v6 was executed against its
     assertions before being written (see gen_v6.py).

The adapter is trained on the *merged* dense checkpoint (bhajanlal-pro-max-2)
so prior capabilities survive, then merged back into a dense model and
promoted only if the validation gate passes.
"""
from __future__ import annotations

import importlib.util
import json
import math
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAIN = ROOT / "train"
CKPT = TRAIN / "checkpoints" / "bhajanlal-v18-adapter"   # LoRA adapter output
FINAL = TRAIN / "checkpoints" / "bhajanlal-pro-max-2"     # dense model we promote into
FINAL_NEW = TRAIN / "checkpoints" / "bhajanlal-pro-max-2-new"
REJECTED = TRAIN / "checkpoints" / "rejected"
DATA = TRAIN / "data_mix.jsonl"
BASE_CKPT = FINAL  # fine-tune on top of the merged dense model
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
CACHE = Path.home() / ".cache" / "huggingface"

# Import the shared _STYLE prompt from the endpoint module (single source of truth).
def _load_endpoint_module():
    spec = importlib.util.spec_from_file_location("bhajanlal_endpoint", ROOT / "serve" / "endpoint.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_EP = _load_endpoint_module()
_STYLE = _EP._STYLE

EPOCHS = 6
BATCH = 1
GRAD_ACCUM = 4
LR = 2e-4
WARMUP_RATIO = 0.05
MAX_SEQ_LEN = 384

MIN_MEAN_TOKEN_ACC = 0.30
MIN_ENTROPY = 0.04
MAX_FINAL_LOSS = 2.0


def load_samples():
    out = []
    for line in DATA.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    # de-dupe exact (instruction,response) pairs
    seen = set(); uniq = []
    for s in out:
        key = (s["instruction"], s["response"])
        if key in seen:
            continue
        seen.add(key); uniq.append(s)
    return uniq


def validate_run(final: dict, model, tokenizer, device) -> list[str]:
    problems = []
    acc = final.get("mean_token_accuracy")
    if not isinstance(acc, (int, float)) or not math.isfinite(acc):
        problems.append(f"mean_token_accuracy is not finite: {acc!r}")
    elif acc < MIN_MEAN_TOKEN_ACC:
        problems.append(f"mean_token_accuracy {acc:.4f} < {MIN_MEAN_TOKEN_ACC} "
                        f"(model learned nothing usable)")

    ent = final.get("entropy")
    if not isinstance(ent, (int, float)) or not math.isfinite(ent):
        problems.append(f"entropy is not finite (NaN/diverged): {ent!r}")
    elif ent < MIN_ENTROPY:
        problems.append(f"entropy {ent:.4f} < {MIN_ENTROPY} (collapsed: "
                        f"model emits one token regardless of input)")

    loss = final.get("train_loss", final.get("loss"))
    if not isinstance(loss, (int, float)) or not math.isfinite(loss):
        problems.append(f"train_loss is not finite: {loss!r}")
    elif loss > MAX_FINAL_LOSS:
        problems.append(f"train_loss {loss:.4f} > {MAX_FINAL_LOSS}")

    try:
        msgs = [{"role": "system", "content": _STYLE},
                {"role": "user", "content": "Reply with exactly: OK"}]
        prompt = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        if not prompt:
            problems.append("chat template rendered empty smoke prompt")
        else:
            import torch
            enc = tokenizer(prompt, return_tensors="pt").to(device)
            with torch.inference_mode():
                out = model.generate(
                    **enc, max_new_tokens=16, do_sample=False,
                    pad_token_id=tokenizer.eos_token_id, use_cache=True)
            text = tokenizer.decode(
                out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            if not text:
                problems.append("smoke generation returned empty output")
            elif "\U000f0002" in text or "### Instruction" in text:
                problems.append(f"smoke generation leaked template markup: {text[:80]!r}")
    except Exception as exc:
        problems.append(f"smoke generation failed: {exc}")
    return problems


def quarantine(reason: str) -> Path | None:
    if not CKPT.exists() or not any(CKPT.iterdir()):
        return None
    REJECTED.mkdir(parents=True, exist_ok=True)
    dest = REJECTED / f"{CKPT.name}-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.move(str(CKPT), str(dest))
    (dest / "REJECTED.txt").write_text(
        f"rejected: {reason}\nat: {time.strftime('%Y-%m-%dT%H:%M:%S')}\n"
        f"script: {Path(__file__).name}\n", encoding="utf-8")
    return dest


def main():
    TRAIN.mkdir(parents=True, exist_ok=True)
    samples = load_samples()
    print(f"=== Bhajanlal v8 training -> {CKPT.name} ({len(samples)} samples) ===", flush=True)

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, get_peft_model
    from datasets import Dataset
    from trl import SFTTrainer, SFTConfig

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Device: {device} | torch {torch.__version__}", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(str(BASE_CKPT), cache_dir=str(CACHE))
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Fine-tune on top of the merged dense checkpoint (preserves prior caps).
    model = AutoModelForCausalLM.from_pretrained(
        str(BASE_CKPT), cache_dir=str(CACHE), torch_dtype=torch.float16,
        trust_remote_code=True)
    # fp16 + gradient checkpointing to stay inside MPS memory budget (0.5B + LoRA).
    model.gradient_checkpointing_enable()
    model.config.use_cache = False
    model.to(device)
    torch.set_float32_matmul_precision("high")

    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                      task_type="CAUSAL_LM",
                      target_modules=["q_proj", "v_proj"])
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    def fmt(s):
        msgs = [
            {"role": "system", "content": _STYLE},
            {"role": "user", "content": s["instruction"]},
            {"role": "assistant", "content": s["response"]},
        ]
        try:
            text = tokenizer.apply_chat_template(msgs, tokenize=False)
        except Exception as exc:
            raise RuntimeError(
                f"apply_chat_template failed on sample {s.get('instruction', '')[:60]!r}: {exc}. "
                "Refusing to train on a fallback format."
            ) from exc
        if not text:
            raise RuntimeError(
                "chat template produced empty text - refusing to train. "
                "The tokenizer likely has no chat template for this model."
            )
        return text

    ds = Dataset.from_dict({"text": [fmt(s) for s in samples]})

    args = SFTConfig(output_dir=str(CKPT), num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH, gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR, warmup_ratio=WARMUP_RATIO, lr_scheduler_type="cosine",
        logging_steps=5, save_strategy="epoch", fp16=False, bf16=False,
        dataset_text_field="text", max_length=MAX_SEQ_LEN, packing=False,
        report_to="none", dataloader_num_workers=0, dataloader_pin_memory=False)
    trainer = SFTTrainer(model=model, args=args, train_dataset=ds, processing_class=tokenizer)

    print("Training...", flush=True)
    t0 = time.time()
    trainer.train()
    dur = time.time() - t0

    history = trainer.state.log_history or []
    metric_entries = [e for e in history if "mean_token_accuracy" in e]
    tr = metric_entries[-1] if metric_entries else (history[-1] if history else {})
    print("log_history entries:", len(history), "metric-bearing:", len(metric_entries), flush=True)
    if metric_entries:
        print("last metrics:", {k: metric_entries[-1].get(k) for k in
              ("loss", "entropy", "mean_token_accuracy", "train_loss")}, flush=True)
    # TRL logs the scalar as "loss" inside metric-bearing entries; normalize so
    # the validation gate (which keys on "train_loss") keeps working.
    if "train_loss" not in tr and "loss" in tr:
        tr = dict(tr)
        tr["train_loss"] = tr["loss"]
    print("Validating run...", flush=True)
    problems = validate_run(tr, model, tokenizer, device)

    meta = {"base_model": str(BASE_CKPT), "method": "LoRA (r=32, alpha=64, 7 modules) on pro-max-2",
            "device": device, "epochs": EPOCHS, "samples": len(samples),
            "checkpoint": str(CKPT), "train_seconds": round(dur, 1), "final": tr}

    if problems:
        reason = "; ".join(problems)
        dest = quarantine(reason)
        meta.update({"status": "failed", "problems": problems,
                     "quarantined_to": str(dest) if dest else None, "usable": False})
        (TRAIN / "metadata_v18.json").write_text(json.dumps(meta, indent=2))
        print(f"=== v6 training FAILED validation ===", flush=True)
        for p in problems:
            print(f"  FAIL: {p}", flush=True)
        print(f"checkpoint quarantined -> {dest}", flush=True)
        sys.exit(1)

    # Save adapter
    model.save_pretrained(str(CKPT))
    tokenizer.save_pretrained(str(CKPT))
    meta.update({"status": "adapter_ok", "problems": [], "usable": False,
                 "gates": {"min_mean_token_accuracy": MIN_MEAN_TOKEN_ACC,
                           "min_entropy": MIN_ENTROPY, "max_final_loss": MAX_FINAL_LOSS}})
    (TRAIN / "metadata_v18.json").write_text(json.dumps(meta, indent=2))
    print(f"=== v6 adapter trained in {dur/60:.1f} min; merging into dense model ===", flush=True)

    # Merge adapter into the base dense model -> new dense checkpoint.
    print("Merging adapter into base dense model...", flush=True)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    base = AutoModelForCausalLM.from_pretrained(
        str(BASE_CKPT), cache_dir=str(CACHE), torch_dtype=torch.float16,
        trust_remote_code=True)
    merged_model = PeftModel.from_pretrained(base, str(CKPT))
    merged_model = merged_model.merge_and_unload()
    merged_model.eval()

    if FINAL_NEW.exists():
        shutil.rmtree(FINAL_NEW)
    FINAL_NEW.mkdir(parents=True, exist_ok=True)
    merged_model.half().save_pretrained(str(FINAL_NEW), safe_serialization=True)
    tokenizer.save_pretrained(str(FINAL_NEW))

    # Smoke check on the merged dense model.
    print("Smoke-testing merged dense model...", flush=True)
    device2 = "mps" if torch.backends.mps.is_available() else "cpu"
    merged_model.to(device2)
    msgs = [{"role": "system", "content": _STYLE},
            {"role": "user", "content": "Write a Python function to reverse a string. Return ONLY the function in a code block."}]
    prompt = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    enc = tokenizer(prompt, return_tensors="pt").to(device2)
    with torch.inference_mode():
        out = merged_model.generate(**enc, max_new_tokens=64, do_sample=False,
                                    pad_token_id=tokenizer.eos_token_id, use_cache=True)
    text = tokenizer.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()
    print(f"smoke output: {text[:200]!r}", flush=True)
    if not text or "```" not in text:
        reason = f"merged model smoke failed: {text[:120]!r}"
        shutil.rmtree(FINAL_NEW, ignore_errors=True)
        meta.update({"status": "failed", "problems": [reason], "usable": False})
        (TRAIN / "metadata_v18.json").write_text(json.dumps(meta, indent=2))
        print(f"FAIL: {reason}", flush=True)
        sys.exit(1)

    # Atomic swap: old dense -> backup, new -> FINAL.
    backup = REJECTED / f"bhajanlal-pro-max-2-pre-v6-{time.strftime('%Y%m%d-%H%M%S')}"
    REJECTED.mkdir(parents=True, exist_ok=True)
    shutil.move(str(FINAL), str(backup))
    shutil.move(str(FINAL_NEW), str(FINAL))

    meta.update({"status": "ok", "problems": [], "usable": True,
                 "final_checkpoint": str(FINAL),
                 "backup": str(backup),
                 "gates": {"min_mean_token_accuracy": MIN_MEAN_TOKEN_ACC,
                           "min_entropy": MIN_ENTROPY, "max_final_loss": MAX_FINAL_LOSS}})
    (TRAIN / "metadata_v18.json").write_text(json.dumps(meta, indent=2))
    print(f"=== v6 promoted -> {FINAL} (backup {backup}) ===", flush=True)


if __name__ == "__main__":
    main()
