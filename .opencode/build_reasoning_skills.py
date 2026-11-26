#!/usr/bin/env python3
"""Generate reasoning & intent-alignment skills."""
from pathlib import Path

PILLAR = ("Part of the **Bhajanlal** model-building skill library. "
          "Pillar: 108. Reasoning, Intent & Chain-of-Thought (20 skills)")
OUT = Path(__file__).resolve().parent / "skills"

SKILLS = [
("intent-understanding", "intent-understanding", "Use when parsing the user's true goal, constraints, and desired output format before acting.",
 ["Restate the goal and constraints internally.",
  "Identify the desired output shape.",
  "Resolve ambiguities by checking the codebase.",
  "Choose the simplest correct approach."],
 "Accurate intent alignment."),
("chain-of-thought-reasoning", "chain-of-thought-reasoning", "Use when reasoning step-by-step internally before producing the final answer.",
 ["Break the problem into steps.",
  "Reason through each step.",
  "Verify intermediate results.",
  "Produce a concise final answer."],
 "Well-reasoned answers."),
("hypothesis-testing", "hypothesis-testing", "Use when listing and testing root-cause hypotheses ranked by probability.",
 ["List top hypotheses.",
  "Test the cheapest first.",
  "Update probabilities with evidence.",
  "Conclude with the verified cause."],
 "Hypothesis-driven diagnosis."),
("ambiguity-clarification", "ambiguity-clarification", "Use when asking one targeted question only when interpretations diverge architecturally.",
 ["Detect ambiguity.",
  "Ask one focused question.",
  "Offer concrete options.",
  "Proceed once resolved."],
 "Clear requirement resolution."),
("assumption-stating", "assumption-stating", "Use when stating assumptions explicitly when uncertain.",
 ["Identify unknowns.",
  "State assumptions clearly.",
  "Choose simplest defaults.",
  "Validate later."],
 "Transparent assumptions."),
("counterfactual-checking", "counterfactual-checking", "Use when stress-testing solutions against null, zero, concurrency, and timeout edge cases.",
 ["List edge cases.",
  "Test each mentally.",
  "Fix vulnerabilities.",
  "Validate."],
 "Robust edge-case handling."),
("first-principles-decomposition", "first-principles-decomposition", "Use when stripping a problem to fundamental constraints before choosing frameworks.",
 ["Identify core constraints.",
  "Ignore surface syntax.",
  "Derive minimal solution.",
  "Validate."],
 "First-principles solutions."),
("tradeoff-evaluation", "tradeoff-evaluation", "Use when evaluating speed, memory, complexity, and cost to pick a Pareto-optimal design.",
 ["List options and metrics.",
  "Compare tradeoffs.",
  "Select Pareto-optimal.",
  "Justify choice."],
 "Balanced design decisions."),
("goal-drift-prevention", "goal-drift-prevention", "Use when re-anchoring to the original user goal after chasing nested errors.",
 ["Track original goal.",
  "Detect drift.",
  "Re-anchor.",
  "Complete the goal."],
 "Goal-focused execution."),
("verification-before-answer", "verification-before-answer", "Use when verifying claims against tool output and codebase before answering.",
 ["Gather evidence.",
  "Verify facts.",
  "Avoid fabrication.",
  "Answer with confidence."],
 "Verified, grounded answers."),
("multi-step-planning", "multi-step-planning", "Use when decomposing complex tasks into ordered, verifiable milestones.",
 ["Decompose into milestones.",
  "Order by dependency.",
  "Verify each step.",
  "Deliver result."],
 "Structured task execution."),
("self-correction", "self-correction", "Use when diagnosing and fixing errors from tool output without repeating failed approaches.",
 ["Read error.",
  "Hypothesize fix.",
  "Apply and re-test.",
  "Avoid loops."],
 "Self-correcting execution."),
("minimal-solution-preference", "minimal-solution-preference", "Use when preferring the simplest correct solution over over-engineered abstractions.",
 ["Identify minimal approach.",
  "Avoid speculative abstractions.",
  "Implement cleanly.",
  "Validate."],
 "Minimal, correct solutions."),
("context-grounding", "context-grounding", "Use when grounding answers in retrieved files and tool output instead of guessing.",
 ["Read relevant files.",
  "Ground claims in evidence.",
  "Cite file:line.",
  "Avoid hallucination."],
 "Grounded, accurate answers."),
("negative-constraint-compliance", "negative-constraint-compliance", "Use when honoring 'do not' constraints and format restrictions reliably.",
 ["Parse constraints.",
  "Honor all negatives.",
  "Check output format.",
  "Validate compliance."],
 "Constraint-compliant output."),
("precision-in-formatting", "precision-in-formatting", "Use when matching requested word counts, bullet structures, and schemas exactly.",
 ["Parse format request.",
  "Match exactly.",
  "Validate output."],
 "Precisely formatted output."),
("error-recovery", "error-recovery", "Use when recovering from tool failures by changing strategy instead of repeating.",
 ["Detect failure.",
  "Change approach.",
  "Retry.",
  "Validate."],
 "Resilient error recovery."),
("scope-containment", "scope-containment", "Use when staying within the original task scope and logging out-of-scope ideas separately.",
 ["Define scope.",
  "Avoid scope creep.",
  "Log extras separately.",
  "Complete in scope."],
 "Focused, in-scope work."),
("evidence-based-promotion", "evidence-based-promotion", "Use when promoting changes only after tests and verification pass.",
 ["Run verification.",
  "Check gates.",
  "Promote only if pass.",
  "Document."],
 "Evidence-gated promotion."),
("intent-feedback-loop", "intent-feedback-loop", "Use when using thumbs/edit/retry feedback to refine understanding of user intent.",
 ["Capture feedback.",
  "Infer intent gaps.",
  "Adjust approach.",
  "Improve alignment."],
 "Continuously improving intent alignment."),
]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for slug, name, desc, steps, output in SKILLS:
        d = OUT / slug
        d.mkdir(parents=True, exist_ok=True)
        steps_md = "\n".join(f"{i+1}. {st}" for i, st in enumerate(steps))
        content = f"""---
name: {name}
description: {desc}
---

# {name}

{PILLAR}

{desc}

## Workflow

{steps_md}

## Output

{output}
"""
        (d / "SKILL.md").write_text(content, encoding="utf-8")
        count += 1
    print(f"Wrote {count} skills to {OUT}")

if __name__ == "__main__":
    main()