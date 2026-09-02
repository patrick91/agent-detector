from __future__ import annotations

import pytest

from agent_detector import DetectionResult
from agent_detector._cli import main


def test_cli_prints_detection(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        "agent_detector._cli.detect_agent",
        lambda **kwargs: DetectionResult("grok", "high", "environment", "GROK_SESSION_ID"),
    )

    assert main([]) == 0
    assert capsys.readouterr().out == (
        "DetectionResult(agent='grok', confidence='high', source='environment', "
        "signal='GROK_SESSION_ID')\n"
    )


def test_cli_prints_unattributed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("agent_detector._cli.detect_agent", lambda **kwargs: None)

    assert main([]) == 1
    assert capsys.readouterr().out == "unattributed\n"


def test_cli_forwards_minimum_confidence(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    def fake_detect(
        environ: object | None = None,
        *,
        minimum_confidence: str = "low",
    ) -> None:
        seen["minimum_confidence"] = minimum_confidence
        return None

    monkeypatch.setattr("agent_detector._cli.detect_agent", fake_detect)

    assert main(["--minimum-confidence", "high"]) == 1
    assert seen["minimum_confidence"] == "high"


def test_cli_rejects_invalid_minimum_confidence() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--minimum-confidence", "nope"])

    assert excinfo.value.code == 2
