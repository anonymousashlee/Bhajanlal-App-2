#!/usr/bin/env python3
"""Generate reasoning/intent-alignment training rows."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".opencode" / "skills"
OUT = Path(__file__).resolve().parent / "data_reasoning.jsonl"

PROMPTS = [
    "How do I make sure I understand what the user actually wants before coding?",
    "The user said 'it's broken' with no details. What should I do first?",
    "I have three possible root causes. How do I pick which to test first?",
    "The user asked for a quick fix but the code needs a refactor. How do I proceed?",
    "My last edit failed twice. What should I do now?",
    "I'm unsure about a file path. Should I guess or verify?",
    "The user wants JSON output only. How do I format my response?",
    "A test is failing intermittently. How do I diagnose?",
    "I found a bug outside the task scope. What do I do?",
    "The user's request conflicts with an earlier instruction. How do I resolve?",
]

RESPONSES = [
    "Parse the user's goal, constraints, and desired output format first. Check the codebase for facts. Ask one targeted question only if two interpretations would change the architecture. Then implement the simplest correct solution and verify.",
    "Don't guess. Run the build/tests, read the error, and inspect the relevant code. Ask a clarifying question only if the symptom is ambiguous. State assumptions explicitly.",
    "List the hypotheses ranked by probability and cost to test. Test the cheapest first. Update probabilities with evidence. Conclude with the verified cause.",
    "Honor the user's intent: do the minimal fix now, log the refactor as out-of-scope, and offer it separately. Don't over-engineer.",
    "Stop repeating the failed approach. Change strategy: widen the edit anchor, re-read the file, or try a different diagnostic. Use git checkout to revert if messy.",
    "Never guess. Use grep/glob/read to verify the path exists. If still unsure, ask the user or state the assumption.",
    "Output bare raw JSON with no markdown fences or commentary, exactly as requested.",
    "Treat intermittent failures as race conditions or env flakiness. Re-run in isolation 3x. Check shared state, missing awaits, and caching.",
    "Log it as tech debt and stay in scope. Don't expand a small fix into a refactor without asking.",
    "Prioritize safety > explicit user rules > repo conventions > defaults. Flag the conflict politely and ask which to follow.",
]

def main():
    rows = []
    for p, r in zip(PROMPTS, RESPONSES):
        rows.append({"instruction": p, "response": r, "quadrant": "reasoning"})
    # add skill-derived rows
    import re
    if SKILLS.exists():
        for d in sorted(SKILLS.iterdir()):
            if not d.is_dir():
                continue
            p = d / "SKILL.md"
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            # extract name and desc
            import re
            nm = re.search(r"^name:\s*(.+)$", text, re.M)
            dc = re.search(r"^description:\s*(.+)$", text, re.M)
            name = nm.group(1).strip() if nm else d.name
            desc = dc.group(1).strip() if dc else ""
            rows.append({
                "instruction": f"How do I {name.replace('-', ' ')}?",
                "response": desc,
                "quadrant": "reasoning",
            })
    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                   encoding="utf-8")
    print(f"Wrote {len(rows)} reasoning rows to {OUT}")

if __name__ == "__main__":
    main()