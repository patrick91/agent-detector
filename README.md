# Agent Detector

`agent-detector` is a small, dependency-free Python package for detecting which
AI coding agent is driving the current process.

It returns evidence rather than only a boolean, so callers can distinguish an
explicit identity from a broad environmental hint.

## Installation

```bash
pip install agent-detector
```

## Usage

```python
from agent_detector import detect_agent

detection = detect_agent()

if detection:
    print(detection.agent)       # "codex"
    print(detection.confidence)  # "high"
    print(detection.signal)      # "CODEX_THREAD_ID"
```

The returned `DetectionResult` contains:

- `agent`: an `AgentName` literal containing a supported agent name
- `confidence`: `high`, `medium`, or `low`
- `source`: `environment` or `path`
- `signal`: the name of the matched signal, never its value

Pass a mapping to make detection deterministic in tests:

```python
assert detect_agent({"OPENCODE": "1"}).agent == "opencode"
```

## Supported agents

| Agent | Signals | Confidence |
| --- | --- | --- |
| Explicit override | `AI_AGENT` containing a supported agent name | high |
| Amp | `AGENT=amp`, `AMP_CURRENT_THREAD_ID` | high / medium |
| Codex | `CODEX_THREAD_ID`, `CODEX_CI`, `CODEX_SANDBOX` | high |
| Gemini CLI | `GEMINI_CLI` | high |
| Copilot CLI | `COPILOT_CLI` | medium |
| OpenCode | `OPENCODE` | high |
| Antigravity | `ANTIGRAVITY_AGENT` | medium |
| Augment CLI | `AUGMENT_AGENT` | medium |
| Cowork | `CLAUDE_CODE_IS_COWORK` | high |
| Claude Code | `CLAUDE_CODE_CHILD_SESSION`, `CLAUDECODE`, `CLAUDE_CODE` | high / medium |
| Cursor | `CURSOR_TRACE_ID` | medium |
| Cursor CLI | `CURSOR_AGENT`, `CURSOR_EXTENSION_HOST_ROLE=agent-exec` | high / medium |
| Kiro | `TERM_PROGRAM=kiro` | low |
| Pi | `.pi/agent` entry in `PATH` | medium |
| Replit | `REPL_ID` | low |
| Goose | `GOOSE_PROVIDER` | low |

`AI_AGENT` takes precedence over inferred signals when its value is one of the
supported agent names. Unknown values are ignored.

The detector is deliberately ordered. For example, Amp is checked before
Claude Code because Amp also sets `CLAUDECODE`.

## Important limitations

Detection is best-effort. `None` means **unattributed**, not "human". Some
signals can also be present in an integrated terminal where a person typed the
command manually.

This package detects the execution harness. It cannot determine whether a
particular skill, plugin, prompt, or model caused the command. Use a separate
explicit marker when that attribution matters.

## Privacy

Environment values such as thread IDs are never returned. A result contains
only a normalized agent name and the name and category of the matched signal.

## Development

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv build
```
