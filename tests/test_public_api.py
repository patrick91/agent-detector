from typing import get_args

import agent_detector


def test_public_api() -> None:
    assert agent_detector.__all__ == [
        "KNOWN_AGENTS",
        "AgentConfidence",
        "AgentName",
        "DetectionResult",
        "DetectionSource",
        "detect_agent",
        "parse_invoking_agent",
    ]


def test_known_agents_are_stable() -> None:
    assert agent_detector.KNOWN_AGENTS == frozenset(
        {
            "amp",
            "antigravity",
            "augment-cli",
            "claude-code",
            "codex",
            "copilot-cli",
            "cowork",
            "cursor",
            "cursor-cli",
            "gemini-cli",
            "goose",
            "kiro",
            "opencode",
            "pi",
            "replit",
        }
    )


def test_known_agents_match_literal_values() -> None:
    assert agent_detector.KNOWN_AGENTS == frozenset(get_args(agent_detector.AgentName))


def test_confidence_literal_values() -> None:
    assert get_args(agent_detector.AgentConfidence) == ("high", "medium", "low")
