1.1.2 - 2026-09-02
------------------

This release adds support for detecting Grok Build

This release was contributed by [@patrick91](https://github.com/patrick91) in [#6](https://github.com/patrick91/agent-detector/pull/6)

1.1.1 - 2026-09-02
------------------

This release add support for detecting Grok Bot

This release was contributed by [@patrick91](https://github.com/patrick91) in [#4](https://github.com/patrick91/agent-detector/pull/4)

1.1.0 - 2026-08-19
------------------

This release adds `parse_invoking_agent` for parsing an explicit coding-agent
identity propagated through a `User-Agent` value of the form
`<product>/<version> AI-Agent/<agent>`. It returns a `DetectionResult` with the
new `"user-agent"` detection source, and callers can optionally require an
expected client product while continuing to use the package's shared agent
allowlist.

This release was contributed by [@patrick91](https://github.com/patrick91) in [#2](https://github.com/patrick91/agent-detector/pull/2)

1.0.0 - 2026-07-21
------------------

Agent Detector is now available as a dependency-free Python package for
identifying the AI coding agent driving a process.

It recognizes Codex, Claude Code, Amp, Pi, OpenCode, Cursor, Gemini CLI, and
other coding agents using environment evidence. Each result includes a
normalized agent name, confidence, source, and signal without returning
environment values. Callers can also require a minimum confidence level.

This release was contributed by [@patrick91](https://github.com/patrick91) in [#1](https://github.com/patrick91/agent-detector/pull/1)

# Changelog

This file is managed by [AutoPub](https://github.com/patrick91/autopub).