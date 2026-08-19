from typing import Optional

import pytest

from agent_detector import KNOWN_AGENTS, AgentName, DetectionResult, parse_invoking_agent


@pytest.mark.parametrize("agent", sorted(KNOWN_AGENTS))
def test_parses_known_agent(agent: AgentName) -> None:
    assert parse_invoking_agent(f"example-cli/1.2.3 AI-Agent/{agent}") == DetectionResult(
        agent, "high", "user-agent", "User-Agent"
    )


def test_accepts_matching_expected_product() -> None:
    detection = parse_invoking_agent(
        "example-cli/1.2.3 AI-Agent/codex",
        expected_product="example-cli",
    )

    assert detection is not None
    assert detection.agent == "codex"


@pytest.mark.parametrize(
    "user_agent",
    [
        " example-cli/1.2.3 AI-Agent/codex",
        "example-cli/1.2.3 AI-Agent/codex ",
        "example-cli/1.2.3 AI-Agent/codex\t",
        "example-cli/1.2.3 AI-Agent/codex\r\n",
        "example-cli/1.2.3  AI-Agent/codex",
        "example-cli/1.2.3\tAI-Agent/codex",
        "example-cli/1.2.3+build.7 AI-Agent/codex",
    ],
)
def test_ignores_surrounding_whitespace(user_agent: str) -> None:
    detection = parse_invoking_agent(user_agent, expected_product="example-cli")

    assert detection is not None
    assert detection.agent == "codex"


@pytest.mark.parametrize(
    "user_agent",
    [
        None,
        "",
        "   ",
        "example-cli/1.2.3",
        "example-cli/1.2.3 AI-Agent/codex extra/1",
        "example-cli/1.2.3 (darwin) AI-Agent/codex",
        "example-cli AI-Agent/codex",
        "/1.2.3 AI-Agent/codex",
        "example-cli/ AI-Agent/codex",
        "example-cli/1.2.3/extra AI-Agent/codex",
        "example-cli/1.2(foo) AI-Agent/codex",
        "(example-cli)/1.2.3 AI-Agent/codex",
        "example-cli/1.2.3 ai-agent/codex",
        "example-cli/1.2.3 Agent/codex",
        "example-cli/1.2.3 AI-Agent",
        "example-cli/1.2.3 AI-Agent/",
        "example-cli/1.2.3 AI-Agent/Codex",
        "example-cli/1.2.3 AI-Agent/unknown",
    ],
)
def test_rejects_invalid_or_unsupported_user_agent(user_agent: Optional[str]) -> None:
    assert parse_invoking_agent(user_agent) is None


@pytest.mark.parametrize(
    "user_agent",
    [
        "other-cli/1.2.3 AI-Agent/codex",
        "Example-CLI/1.2.3 AI-Agent/codex",
    ],
)
def test_rejects_unexpected_product(user_agent: str) -> None:
    assert parse_invoking_agent(user_agent, expected_product="example-cli") is None


def test_rejects_empty_expected_product() -> None:
    with pytest.raises(ValueError, match="expected_product"):
        parse_invoking_agent("example-cli/1.2.3 AI-Agent/codex", expected_product="")
