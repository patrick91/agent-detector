---
release type: major
---

Agent Detector is now available as a dependency-free Python package for
identifying the AI coding agent driving a process.

It recognizes Codex, Claude Code, Amp, Pi, OpenCode, Cursor, Gemini CLI, and
other coding agents using environment evidence. Each result includes a
normalized agent name, confidence, source, and signal without returning
environment values. Callers can also require a minimum confidence level.
