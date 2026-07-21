import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, Optional, cast

AgentConfidence = Literal["high", "medium", "low"]
DetectionSource = Literal["environment", "path"]
AgentName = Literal[
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
]

KNOWN_AGENTS: frozenset[AgentName] = frozenset(
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

_PI_AGENT_PATH = re.compile(r"(?:^|[\\/])\.pi[\\/]agent(?:[\\/]|$)")


@dataclass(frozen=True)
class DetectionResult:
    """Evidence that an AI coding agent is driving the current process."""

    agent: AgentName
    confidence: AgentConfidence
    source: DetectionSource
    signal: str


def detect_agent(
    environ: Optional[Mapping[str, str]] = None,
    *,
    minimum_confidence: AgentConfidence = "low",
) -> Optional[DetectionResult]:
    """Detect the AI coding agent driving the current process, if any.

    Detection is best-effort. A ``None`` result means "unattributed", not "human".

    Values from the environment are inspected locally but are never included in
    the returned result.
    """

    values = os.environ if environ is None else environ

    if minimum_confidence not in ("high", "medium", "low"):
        raise ValueError("minimum_confidence must be 'high', 'medium', or 'low'")

    allow_medium = minimum_confidence in ("medium", "low")
    allow_low = minimum_confidence == "low"

    # An explicit known identity is checked before inferred signals.
    explicit_agent = values.get("AI_AGENT", "")
    if explicit_agent in KNOWN_AGENTS:
        return DetectionResult(cast(AgentName, explicit_agent), "high", "environment", "AI_AGENT")

    # Amp sets CLAUDECODE too, so its more specific signals must win.
    if values.get("AGENT") == "amp":
        return DetectionResult("amp", "high", "environment", "AGENT")
    if allow_medium and values.get("AMP_CURRENT_THREAD_ID"):
        return DetectionResult("amp", "medium", "environment", "AMP_CURRENT_THREAD_ID")

    # OpenAI Codex CLI.
    for signal in ("CODEX_THREAD_ID", "CODEX_CI", "CODEX_SANDBOX"):
        if values.get(signal):
            return DetectionResult("codex", "high", "environment", signal)

    # Google Gemini CLI.
    if values.get("GEMINI_CLI"):
        return DetectionResult("gemini-cli", "high", "environment", "GEMINI_CLI")

    # GitHub Copilot CLI. This signal is observed but not publicly documented.
    if allow_medium and values.get("COPILOT_CLI"):
        return DetectionResult("copilot-cli", "medium", "environment", "COPILOT_CLI")

    # OpenCode sets OPENCODE for the running agent. OPENCODE_CLIENT and
    # OPENCODE_CALLER identify its launcher, so they are intentionally ignored.
    if values.get("OPENCODE"):
        return DetectionResult("opencode", "high", "environment", "OPENCODE")

    if allow_medium and values.get("ANTIGRAVITY_AGENT"):
        return DetectionResult("antigravity", "medium", "environment", "ANTIGRAVITY_AGENT")

    if allow_medium and values.get("AUGMENT_AGENT"):
        return DetectionResult("augment-cli", "medium", "environment", "AUGMENT_AGENT")

    # Cowork and Claude Code share ambient Claude markers. Check Cowork first.
    if values.get("CLAUDE_CODE_IS_COWORK"):
        return DetectionResult("cowork", "high", "environment", "CLAUDE_CODE_IS_COWORK")

    # This specifically marks commands spawned by Claude Code.
    if values.get("CLAUDE_CODE_CHILD_SESSION"):
        return DetectionResult("claude-code", "high", "environment", "CLAUDE_CODE_CHILD_SESSION")

    # These can also exist in Claude's integrated terminal, so they carry less
    # confidence than the child-session signal.
    for signal in ("CLAUDECODE", "CLAUDE_CODE"):
        if allow_medium and values.get(signal):
            return DetectionResult("claude-code", "medium", "environment", signal)

    # Cursor IDE and Cursor CLI are distinguishable when both signals exist.
    if allow_medium and values.get("CURSOR_TRACE_ID"):
        return DetectionResult("cursor", "medium", "environment", "CURSOR_TRACE_ID")

    if values.get("CURSOR_AGENT"):
        return DetectionResult("cursor-cli", "high", "environment", "CURSOR_AGENT")

    if allow_medium and values.get("CURSOR_EXTENSION_HOST_ROLE") == "agent-exec":
        return DetectionResult("cursor-cli", "medium", "environment", "CURSOR_EXTENSION_HOST_ROLE")

    # The following signals are broader or have less first-party evidence, so
    # they are checked only after the more specific agent signals above.
    if allow_low and values.get("TERM_PROGRAM") == "kiro":
        return DetectionResult("kiro", "low", "environment", "TERM_PROGRAM")

    path = values.get("PATH", "")
    if allow_medium and _PI_AGENT_PATH.search(path):
        return DetectionResult("pi", "medium", "path", "PATH")

    if allow_low and values.get("REPL_ID"):
        return DetectionResult("replit", "low", "environment", "REPL_ID")

    if allow_low and values.get("GOOSE_PROVIDER"):
        return DetectionResult("goose", "low", "environment", "GOOSE_PROVIDER")

    return None
