# PLE harness v1 — a minimal agent harness for Physical-Engineering's Last Exam

A small, honest agent harness for the Kaggle
[Physical-Engineering's Last Exam](https://www.kaggle.com/competitions/physical-engineerings-last-exam)
harness competition: a WebSocket server that speaks the official serve
protocol and drives each task with **one tool — `exec`** (bash in the task
container), plus the task's MCP tools when the task ships an MCP server.

## Layout

| Path | What it is |
|---|---|
| `submission.yaml` | kit entry (name, model, install, serve) validated by the official spec |
| `serve.py` | the harness: listens on `$PORT`, runs one agent loop per task |
| `agent_core.py` | the agent loop + OpenAI-compatible chat call, free of protocol/transport so it is unit-testable |
| `taskbridge.py` | vendored verbatim from the official kit (`sample_submissions/custom-openai`), Apache-2.0, (c) Google LLC — the serve-protocol bridge the organizers tell you to copy in |
| `plekit/` | vendored `spec.py` + `models.py` from the official kit, used offline by the tests to validate `submission.yaml` |
| `runner_local.py` | runs the same loop against a plain folder (no Docker, no protocol) for the bundled sample tasks |
| `samples/` | the three public smoke tasks the official `kit check` runs, as instructions |
| `tests/` | offline unit tests: mock model + mock exec, no network, no API keys |
| `runs/` | committed evidence: real end-to-end run logs and artifacts |

## How the agent works

System prompt + task instruction → loop of `chat/completions` calls with a
native function-calling schema. The model gets exactly two kinds of tools:

* `exec(command)` — runs `bash -c` in the task workspace via the evaluator,
  output (stdout+stderr, exit code) returned to the model, cut at 24k chars
  around the middle so both ends survive;
* `<server>__<tool>` — one function per tool of each MCP server the task
  declares, connected with the vendored `MCPClient`.

The loop stops on a plain-text reply, on the task deadline reported by the
bridge, or at `MAX_STEPS`, in which case the model is asked for one wrap-up
message so there is always a final answer. Model calls retry on 429/5xx and
transport errors (5/15/30 s), fail fast on other 4xx; a failing tool call is
fed back to the model, never fatal.

## Model endpoint

Any OpenAI-compatible `/chat/completions` server with native tool calling.
The kit injects `MODEL_NAME`, `OPENAI_BASE_URL` and the key per
`docs/models.md`; locally you point at your own server:

```bash
python -m kit check . \
  --model-base-url http://127.0.0.1:8000/v1 \
  --env-file env.txt   # MODEL_API_KEY=... MODEL_NAME=...
```

`submission.yaml` commits a placeholder public base URL because the kit
requires one; `--model-base-url` overrides it for local runs (the same path
the official sample submissions use). The verified runs in `runs/` used a
locally hosted Qwen3-class multimodal model behind llama.cpp.

## Reproduce offline (no keys, no network)

```bash
python3 -m pytest tests/ -q          # 10 unit tests, mock model + mock exec
```

## Reproduce end-to-end (needs a tool-calling OpenAI-compatible endpoint)

```bash
# official kit stages (HELLO / 3000-word memo / MCP secret word):
python -m kit check . --model-base-url <url> --env-file env.txt

# or the bundled samples without Docker:
MODEL_NAME=<model> OPENAI_BASE_URL=<url> \
  python runner_local.py samples/hello /tmp/out-hello
```

## License

Apache-2.0 (see `LICENSE`), matching the competition's required license;
`taskbridge.py` and `plekit/` are vendored unmodified from Google's official
kit under the same license.
