import pytest


@pytest.fixture(autouse=True)
def _zoo_backend(monkeypatch):
    monkeypatch.setenv("OPENCAD_BACKEND", "zoo")
