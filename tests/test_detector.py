from dataclasses import FrozenInstanceError

import pytest

from agent_detector import DetectionResult, detect_agent


@pytest.mark.parametrize(
    ("environment", "expected"),
    [
        ({"AI_AGENT": "codex"}, DetectionResult("codex", "high", "environment", "AI_AGENT")),
        ({"AGENT": "amp"}, DetectionResult("amp", "high", "environment", "AGENT")),
        (
            {"AMP_CURRENT_THREAD_ID": "secret"},
            DetectionResult("amp", "medium", "environment", "AMP_CURRENT_THREAD_ID"),
        ),
        (
            {"CODEX_THREAD_ID": "secret"},
            DetectionResult("codex", "high", "environment", "CODEX_THREAD_ID"),
        ),
        ({"CODEX_CI": "1"}, DetectionResult("codex", "high", "environment", "CODEX_CI")),
        (
            {"CODEX_SANDBOX": "seatbelt"},
            DetectionResult("codex", "high", "environment", "CODEX_SANDBOX"),
        ),
        (
            {"GEMINI_CLI": "1"},
            DetectionResult("gemini-cli", "high", "environment", "GEMINI_CLI"),
        ),
        (
            {"COPILOT_CLI": "1"},
            DetectionResult("copilot-cli", "medium", "environment", "COPILOT_CLI"),
        ),
        (
            {"OPENCODE": "1"},
            DetectionResult("opencode", "high", "environment", "OPENCODE"),
        ),
        (
            {"ANTIGRAVITY_AGENT": "1"},
            DetectionResult("antigravity", "medium", "environment", "ANTIGRAVITY_AGENT"),
        ),
        (
            {"AUGMENT_AGENT": "1"},
            DetectionResult("augment-cli", "medium", "environment", "AUGMENT_AGENT"),
        ),
        (
            {"CLAUDE_CODE_IS_COWORK": "1"},
            DetectionResult("cowork", "high", "environment", "CLAUDE_CODE_IS_COWORK"),
        ),
        (
            {"CLAUDE_CODE_CHILD_SESSION": "1"},
            DetectionResult("claude-code", "high", "environment", "CLAUDE_CODE_CHILD_SESSION"),
        ),
        (
            {"CLAUDECODE": "1"},
            DetectionResult("claude-code", "medium", "environment", "CLAUDECODE"),
        ),
        (
            {"CLAUDE_CODE": "1"},
            DetectionResult("claude-code", "medium", "environment", "CLAUDE_CODE"),
        ),
        (
            {"CURSOR_TRACE_ID": "secret"},
            DetectionResult("cursor", "medium", "environment", "CURSOR_TRACE_ID"),
        ),
        (
            {"CURSOR_AGENT": "1"},
            DetectionResult("cursor-cli", "high", "environment", "CURSOR_AGENT"),
        ),
        (
            {"CURSOR_EXTENSION_HOST_ROLE": "agent-exec"},
            DetectionResult("cursor-cli", "medium", "environment", "CURSOR_EXTENSION_HOST_ROLE"),
        ),
        ({"TERM_PROGRAM": "kiro"}, DetectionResult("kiro", "low", "environment", "TERM_PROGRAM")),
        (
            {"PATH": "/usr/bin:/home/user/.pi/agent/bin"},
            DetectionResult("pi", "medium", "path", "PATH"),
        ),
        (
            {"PATH": r"C:\Windows;C:\Users\user\.pi\agent\bin"},
            DetectionResult("pi", "medium", "path", "PATH"),
        ),
        ({"REPL_ID": "secret"}, DetectionResult("replit", "low", "environment", "REPL_ID")),
        (
            {"GOOSE_PROVIDER": "anthropic"},
            DetectionResult("goose", "low", "environment", "GOOSE_PROVIDER"),
        ),
    ],
)
def test_detects_agent(environment: dict[str, str], expected: DetectionResult) -> None:
    assert detect_agent(environment) == expected


@pytest.mark.parametrize(
    "environment",
    [
        {},
        {"GEMINI_CLI": ""},
        {"AI_AGENT": ""},
        {"AI_AGENT": "bad agent"},
        {"AI_AGENT": "bad\nagent"},
        {"AI_AGENT": "a" * 65},
        {"AI_AGENT": "custom-agent"},
        {"AGENT": "other"},
        {"OPENCODE_CLIENT": "opencode"},
        {"OPENCODE_CALLER": "vscode"},
        {"CURSOR_EXTENSION_HOST_ROLE": "worker"},
        {"TERM_PROGRAM": "kirostudio"},
        {"PATH": "/usr/bin:/home/user/x.pi/agent/bin"},
        {"PATH": "/usr/bin:/home/user/.pi/agentic/bin"},
    ],
)
def test_ignores_unsupported_or_unsafe_signals(environment: dict[str, str]) -> None:
    assert detect_agent(environment) is None


def test_explicit_agent_takes_priority() -> None:
    detection = detect_agent(
        {
            "AI_AGENT": "pi",
            "AGENT": "amp",
            "CODEX_THREAD_ID": "secret",
        }
    )

    assert detection == DetectionResult("pi", "high", "environment", "AI_AGENT")


def test_unknown_explicit_agent_falls_through() -> None:
    detection = detect_agent({"AI_AGENT": "custom-agent", "GEMINI_CLI": "1"})

    assert detection == DetectionResult("gemini-cli", "high", "environment", "GEMINI_CLI")


def test_minimum_confidence_high_returns_high_confidence_detection() -> None:
    detection = detect_agent({"CODEX_CI": "1"}, minimum_confidence="high")

    assert detection == DetectionResult("codex", "high", "environment", "CODEX_CI")


def test_minimum_confidence_high_ignores_medium_confidence_detection() -> None:
    assert detect_agent({"AMP_CURRENT_THREAD_ID": "secret"}, minimum_confidence="high") is None


def test_minimum_confidence_medium_returns_medium_confidence_detection() -> None:
    detection = detect_agent({"AMP_CURRENT_THREAD_ID": "secret"}, minimum_confidence="medium")

    assert detection == DetectionResult("amp", "medium", "environment", "AMP_CURRENT_THREAD_ID")


def test_minimum_confidence_medium_ignores_low_confidence_detection() -> None:
    assert detect_agent({"GOOSE_PROVIDER": "anthropic"}, minimum_confidence="medium") is None


def test_minimum_confidence_skips_weaker_signal_for_stronger_signal() -> None:
    detection = detect_agent(
        {"AMP_CURRENT_THREAD_ID": "secret", "CODEX_CI": "1"},
        minimum_confidence="high",
    )

    assert detection == DetectionResult("codex", "high", "environment", "CODEX_CI")


def test_invalid_minimum_confidence_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="minimum_confidence must be 'high', 'medium', or 'low'",
    ):
        detect_agent({}, minimum_confidence="invalid")  # type: ignore[arg-type]


def test_amp_takes_priority_over_claude_code() -> None:
    detection = detect_agent({"AGENT": "amp", "CLAUDECODE": "1"})

    assert detection is not None
    assert detection.agent == "amp"


def test_cowork_takes_priority_over_claude_code() -> None:
    detection = detect_agent({"CLAUDE_CODE_IS_COWORK": "1", "CLAUDECODE": "1"})

    assert detection is not None
    assert detection.agent == "cowork"


def test_specific_signal_takes_priority_over_broad_signal() -> None:
    detection = detect_agent({"GOOSE_PROVIDER": "anthropic", "CODEX_CI": "1"})

    assert detection is not None
    assert detection.agent == "codex"


def test_cursor_ide_takes_priority_over_cursor_cli() -> None:
    detection = detect_agent({"CURSOR_TRACE_ID": "secret", "CURSOR_AGENT": "1"})

    assert detection is not None
    assert detection.agent == "cursor"


def test_detection_is_immutable() -> None:
    detection = DetectionResult("codex", "high", "environment", "CODEX_CI")

    with pytest.raises(FrozenInstanceError):
        detection.agent = "other"  # type: ignore[misc]


def test_uses_process_environment_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_AGENT", "codex")

    assert detect_agent() == DetectionResult("codex", "high", "environment", "AI_AGENT")
