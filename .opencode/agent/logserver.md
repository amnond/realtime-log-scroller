---
description: Use for the FastAPI + watchdog SSE backend in logserver.py — file monitoring, streaming framing, lifespan, and server/dependency setup.
mode: subagent
temperature: 0.2
---

# logserver.py agent

`logserver.py` is a FastAPI app that tails files under `MONITORED_PATHS`
(default `logs/`) using watchdog and pushes new lines to browsers over SSE.

## Key points

- `LogMonitor` tracks a byte offset per file and reads only appended bytes.
  Handle truncation (reset the offset) and files that disappear.
- SSE events MUST use `data: <line>\n\n` framing; keep-alive uses
  `: keep-alive\n\n`.
- The watchdog observer starts and stops in the FastAPI `lifespan` context
  manager; do not leak the observer thread.
- `/` serves `logviewer.html`; `/stream` is the EventSource endpoint.
- `python logserver.py` launches uvicorn with reload using the `module:app`
  import string.

## Verify changes

- Syntax: `python -c "import ast; ast.parse(open('logserver.py').read())"`.
- Runtime: `python logserver.py`, then `curl http://127.0.0.1:8000/stream` to
  confirm the stream opens.
