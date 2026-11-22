"""Offline validation of submission.yaml with the vendored official kit spec."""

import os
import sys

sys.path.insert(0, ".")

from plekit import spec

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_submission_yaml_loads_with_official_spec():
  sub = spec.load(ROOT)  # raises spec.SpecError on any problem
  assert sub.name == "bnty-0709-harness-v1"
  assert sub.model.provider == "openai-compatible"
  assert sub.model.name == "qwen3.8-flash-next-iq3_s"
  # the committed base url must be a public DNS name (kit rule); the local
  # server is passed with --model-base-url at run time
  assert sub.model.base_url == "https://llm.example.org/v1"


def test_serve_command_references_src_placeholder():
  sub = spec.load(ROOT)
  assert "{src}" in sub.serve and "serve.py" in sub.serve
  assert "{src}" in sub.install
