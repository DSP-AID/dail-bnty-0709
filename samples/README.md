The three sample tasks are the public smoke stages of the official kit's
`kit check` command (`SMOKE`, `LONG`, `MCP_TASK` in `kit/check.py` of
Google's Physical-Engineering's Last Exam evaluation kit, Apache-2.0),
copied verbatim as `instruction.md`. They are what "runs end-to-end on
public sample tasks" means for this repo: the full dev/holdout task inputs
live in an auto-gated Hugging Face dataset that needs a token to download.

`kit check` runs these inside a sandboxed task container and starts an MCP
stub itself; `runner_local.py` can replay HELLO and the long memo against a
plain folder (the MCP stage needs the kit's MCP server, so replay it with
`kit check`).
