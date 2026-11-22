"""Builds the writeup figures from committed run artifacts (no invented numbers).

    python3 scripts/make_figures.py

Reads runs/*/metrics.json and runs/*/*.json plus runs/kit-check.log; every
number plotted is parsed from those files. Output goes to figures/.
"""

import json
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(run):
  with open(os.path.join(ROOT, "runs", run, "metrics.json")) as fh:
    metrics = json.load(fh)
  with open(os.path.join(ROOT, "runs", run, "trajectory.json")) as fh:
    traj = json.load(fh)
  return metrics, traj


def figure_steps_vs_tokens():
  """Step mix and tool-output volume of a full local replay (long-memo when committed)."""
  run = "long-memo" if os.path.exists(os.path.join(ROOT, "runs", "long-memo", "trajectory.json")) else "hello"
  metrics, traj = load(run)
  steps = traj["steps"]
  model_steps = [i + 1 for i, s in enumerate(steps) if s["source"] == "model"]
  tool_steps = [i + 1 for i, s in enumerate(steps) if s["source"] == "tool"]

  # replay usage accounting exactly as the loop does: prompt tokens grow with
  # each model call; per-call values are stored in the metrics total only, so
  # plot the trajectory's tool-output volume against model-call index instead.
  out_sizes = []
  n = 0
  for s in steps:
    if s["source"] == "tool":
      n += 1
      out_sizes.append(len(s["message"].get("output", "")))
  fig, ax = plt.subplots(figsize=(7, 3.5))
  ax.bar(range(1, len(out_sizes) + 1), out_sizes, color="#4c72b0")
  ax.set_xlabel("tool call #")
  ax.set_ylabel("chars returned to the model")
  ax.set_title(
      f"{run} sample run: {len(model_steps)} model calls,"
      f" {len(tool_steps)} exec results,\n{metrics['prompt_tokens']:,} prompt /"
      f" {metrics['completion_tokens']:,} completion tokens"
  )
  fig.tight_layout()
  fig.savefig(os.path.join(ROOT, "figures", "sample_run_tool_activity.png"), dpi=140)
  plt.close(fig)


def figure_run_costs():
  """Steps and tokens for each verified run, straight from metrics.json."""
  runs = [d for d in sorted(os.listdir(os.path.join(ROOT, "runs"))) if os.path.isdir(os.path.join(ROOT, "runs", d))]
  names, steps, prompt, completion = [], [], [], []
  for run in runs:
    try:
      with open(os.path.join(ROOT, "runs", run, "metrics.json")) as fh:
        m = json.load(fh)
    except (FileNotFoundError, KeyError):
      continue
    names.append(run)
    steps.append(m["total_steps"])
    prompt.append(m["prompt_tokens"])
    completion.append(m["completion_tokens"])
  x = range(len(names))
  w = 0.4
  fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.2))
  ax1.bar([i - w / 2 for i in x], steps, w, label="steps", color="#55a868")
  ax1.set_xticks(list(x), names)
  ax1.set_ylabel("model round trips")
  ax1.legend()
  ax2.bar([i - w / 2 for i in x], prompt, w, label="prompt", color="#4c72b0")
  ax2.bar([i + w / 2 for i in x], completion, w, label="completion", color="#c44e52")
  ax2.set_xticks(list(x), names)
  ax2.set_ylabel("tokens")
  ax2.legend()
  fig.suptitle("verified local-model sample runs (from metrics.json)")
  fig.tight_layout()
  fig.savefig(os.path.join(ROOT, "figures", "run_costs.png"), dpi=140)
  plt.close(fig)


def figure_kit_stages():
  """Stage-by-stage results parsed straight out of runs/kit-check.log."""
  with open(os.path.join(ROOT, "runs", "kit-check.log")) as fh:
    log = fh.read()
  stages = re.findall(r"\[(PASS|FAIL|SKIP|INFO|WARN)\]\s+([a-z0-9_.-]+)[^\n]*", log)
  seen = {}
  for status, name in stages:
    if name not in seen or seen[name] == "INFO":
      seen[name] = status
  names = list(seen)
  colors = {
      "PASS": "#55a868",
      "FAIL": "#c44e52",
      "SKIP": "#8c8c8c",
      "INFO": "#4c72b0",
      "WARN": "#dd8452",
  }
  fig, ax = plt.subplots(figsize=(7, 1.1 + 0.4 * len(names)))
  ax.barh(
      names, [1] * len(names), color=[colors[seen[n]] for n in names]
  )
  for i, n in enumerate(names):
    ax.text(1.02, i, seen[n], va="center")
  ax.set_xlim(0, 1.25)
  ax.set_xticks([])
  ax.set_title("official kit check stages (parsed from runs/kit-check.log)")
  fig.tight_layout()
  fig.savefig(os.path.join(ROOT, "figures", "kit_check_stages.png"), dpi=140)
  plt.close(fig)


if __name__ == "__main__":
  os.makedirs(os.path.join(ROOT, "figures"), exist_ok=True)
  figure_steps_vs_tokens()
  figure_run_costs()
  figure_kit_stages()
  print("wrote", ", ".join(sorted(os.listdir(os.path.join(ROOT, "figures")))))
