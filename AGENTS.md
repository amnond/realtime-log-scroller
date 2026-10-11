# Project guidance

A dependency-free, single-file virtual scroller for real-time log viewing.

## Layout

- `logviewer.html` — the entire component plus demo UI and page script. No build
  step and no npm dependencies; it must run by opening the file or being served
  directly, so keep everything inline.
- `logserver.py` — FastAPI app serving `logviewer.html` at `/` and streaming log
  lines over SSE at `/stream`.
- `logs/` — watched directory; `logs/generate_log.py` produces sample lines.
- `README.md` — architecture explainer; keep it consistent with behavior.

## Invariants — do not break these

- Only the visible range plus `OVERSCAN_COUNT` items are in the DOM.
- The content window is positioned with `contentWindow.style.top` (layout), NOT
  `translateY`; transforms break native text selection.
- Highlighting is applied to TEXT NODES only (`_applyTextHighlights`,
  `_buildHighlightedItem`). Never run `String.replace` on item HTML.
- Scroll math happens in logical content pixels; the viewport reports physical
  pixels. Convert with `physicalToLogical` / `logicalToPhysical`. Compression
  (`scrollFactor() < 1`) must activate only when `totalHeight > maxScrollHeight`.
- Auto-follow is governed by `paused` + `atBottom` and reported via
  `onFollowChange`. Scrolling up and pressing Pause must both read as
  "not following".
- The component injects its own scoped CSS and must not add global (html/body)
  resets.

## Verify changes

- Syntax-check the embedded script (PowerShell):
  `$raw = Get-Content -Raw logviewer.html; ([regex]::Match($raw,'(?s)<script>(.*?)</script>').Groups[1].Value) | Set-Content $env:TEMP\lv.js; node --check $env:TEMP\lv.js`
- Syntax-check the server:
  `python -c "import ast; ast.parse(open('logserver.py').read())"`
- Functional check: run `python logserver.py`, open http://127.0.0.1:8000, and
  append lines to `logs/app.log` to confirm live streaming and follow/pause.

## Style

- Match the existing code: vanilla ES6 classes, no frameworks.
- Do not add comments unless they explain non-obvious intent.
- Keep changes minimal and preserve existing behavior unless asked otherwise.
