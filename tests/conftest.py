import pytest


@pytest.fixture(autouse=True)
def _telemetry_isolated(monkeypatch, tmp_path):
    """Tests never write into results/_campaign: campaign telemetry and worker state go to the test's tmp dir."""
    from opencad import telemetry
    from opencad.truth import runner
    from opencad.worker import state

    monkeypatch.setattr(telemetry, "CAMPAIGN_FILE", tmp_path / "_campaign" / "telemetry.jsonl")
    monkeypatch.setattr(state, "CAMPAIGN_STATE", tmp_path / "_campaign" / "worker-state.json")
    monkeypatch.setattr(runner, "VAULT", tmp_path / "_vault")
    yield
