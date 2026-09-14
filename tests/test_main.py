"""Tests for the telegram_file_sender entry point."""

import runpy
from pathlib import Path

import pytest
import requests

from telegram_file_sender import __main__ as main_module

REQUIRED_ENV = {
    "TELEGRAM_BOT_TOKEN": "test-token",
    "TELEGRAM_FILE_NAME": "test.txt",
    "TELEGRAM_CHAT_ID": "123",
    "TELEGRAM_CHAT_MESSAGE": "hello",
}


class FakeResponse:
    """Minimal stand-in for a requests.Response that can fail status checks."""

    def __init__(self, ok: bool) -> None:
        self.ok = ok

    def raise_for_status(self) -> None:
        if not self.ok:
            raise requests.HTTPError("401 Client Error")


def fake_post(response: FakeResponse):
    def post(*args, **kwargs):
        return response

    return post


@pytest.fixture
def env(monkeypatch, tmp_path: Path):
    """Set the required environment variables and create the file to send."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("content")
    for key, value in REQUIRED_ENV.items():
        if key == "TELEGRAM_FILE_NAME":
            value = str(file_path)
        monkeypatch.setenv(key, value)
    return file_path


@pytest.fixture
def clear_env(monkeypatch):
    """Remove all required environment variables."""
    for key in REQUIRED_ENV:
        monkeypatch.delenv(key, raising=False)


class TestGetEnvVar:
    def test_returns_value(self, monkeypatch):
        monkeypatch.setenv("SOME_VAR", "value")
        assert main_module.get_env_var("SOME_VAR") == "value"

    def test_missing_raises(self, clear_env):
        with pytest.raises(ValueError):
            main_module.get_env_var("SOME_VAR")

    def test_empty_raises(self, monkeypatch):
        monkeypatch.setenv("SOME_VAR", "")
        with pytest.raises(ValueError):
            main_module.get_env_var("SOME_VAR")


class TestMain:
    def test_success_returns_zero(self, env, monkeypatch):
        monkeypatch.setattr("requests.post", fake_post(FakeResponse(ok=True)))
        assert main_module.main() == 0

    def test_api_error_returns_one(self, env, monkeypatch):
        monkeypatch.setattr("requests.post", fake_post(FakeResponse(ok=False)))
        assert main_module.main() == 1

    def test_missing_file_returns_one(self, env, monkeypatch):
        monkeypatch.delenv("TELEGRAM_FILE_NAME")
        assert main_module.main() == 1

    def test_missing_env_returns_one(self, clear_env):
        assert main_module.main() == 1

    def test_invalid_chat_id_returns_one(self, env, monkeypatch):
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "abc")
        assert main_module.main() == 1

    def test_entrypoint_exits_with_code(self, env, monkeypatch):
        monkeypatch.setattr("requests.post", fake_post(FakeResponse(ok=True)))
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("telegram_file_sender.__main__", run_name="__main__")
        assert exc_info.value.code == 0
