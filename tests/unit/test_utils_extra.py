"""Coverage for utils.py branches not covered by test_path_resolution.py."""
import os
import sys

import pytest

from utils import utils as u
from utils.utils import (
    change_to_user_directory, create_original_csv, normalize_number_format,
    Environment, _detect_environment,
)


# ---- create_original_csv ----------------------------------------------------

def test_create_original_csv_writes_canonical_headers(tmp_path):
    target = tmp_path / "fresh.csv"
    create_original_csv(str(target))
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "Date" in content and "Wallet" in content and "Amount" in content
    assert "Note" in content and "Labels" in content


def test_create_original_csv_overwrites_existing(tmp_path):
    target = tmp_path / "exists.csv"
    target.write_text("garbage", encoding="utf-8")
    create_original_csv(str(target))
    assert "Date" in target.read_text(encoding="utf-8")


# ---- change_to_user_directory ----------------------------------------------

def test_change_to_user_directory_chdirs_home(monkeypatch, tmp_path):
    captured = {}

    def fake_chdir(p):
        captured["path"] = p

    monkeypatch.setattr(os, "chdir", fake_chdir)
    monkeypatch.setattr(os.path, "expanduser", lambda _: str(tmp_path))
    change_to_user_directory()
    assert captured["path"] == str(tmp_path)


def test_change_to_user_directory_swallows_oserror(monkeypatch, caplog):
    def boom(_):
        raise OSError("permission denied")

    monkeypatch.setattr(os, "chdir", boom)
    monkeypatch.setattr(os.path, "expanduser", lambda _: "/whatever")
    with caplog.at_level("WARNING"):
        change_to_user_directory()  # must not raise
    assert any("Failed to change directory" in rec.message for rec in caplog.records)


# ---- _detect_environment branches ------------------------------------------

def test_detect_environment_snap_when_envvars_match(monkeypatch):
    monkeypatch.setenv("TRANSACTION_DECORATOR_SNAP_NAME", "td")
    monkeypatch.setenv("SNAP_NAME", "td")
    assert _detect_environment() == Environment.SNAP


def test_detect_environment_frozen_windows(monkeypatch):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    assert _detect_environment() == Environment.FROZEN_WINDOWS


def test_detect_environment_frozen_other(monkeypatch):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    assert _detect_environment() == Environment.FROZEN_OTHER


def test_detect_environment_ide_when_idea_dir_present(monkeypatch):
    # Default repo state has .idea/ in repo root; clear snap + frozen
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    if hasattr(sys, "frozen"):
        monkeypatch.delattr(sys, "frozen", raising=False)
    assert _detect_environment() == Environment.IDE


def test_detect_environment_linux_package_when_no_idea(monkeypatch, tmp_path):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    if hasattr(sys, "frozen"):
        monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    # Force _is_ide_layout to return False by patching it
    monkeypatch.setattr(u, "_is_ide_layout", lambda _: False)
    assert _detect_environment() == Environment.LINUX_PACKAGE


def test_detect_environment_unknown_when_nothing_matches(monkeypatch):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    if hasattr(sys, "frozen"):
        monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "platform", "freebsd")
    monkeypatch.setattr(u, "_is_ide_layout", lambda _: False)
    assert _detect_environment() == Environment.UNKNOWN


# ---- resource_path branches not covered by test_path_resolution ------------

def test_resource_path_frozen_windows_uses_executable_dir(monkeypatch, tmp_path):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys, "executable", str(tmp_path / "app.exe"))
    result = u.resource_path("icons/logo.png")
    assert result == os.path.join(str(tmp_path), "icons/logo.png")


def test_resource_path_linux_package_uses_fhs_path(monkeypatch):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    if hasattr(sys, "frozen"):
        monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(u, "_is_ide_layout", lambda _: False)
    result = u.resource_path("icons/logo.png")
    assert result == os.path.join("/usr/lib/transaction-decorator", "icons/logo.png")


# ---- user_directory_path branches ------------------------------------------

def test_user_directory_path_frozen_windows_uses_appdata(monkeypatch, tmp_path):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    result = u.user_directory_path("dictionary")
    assert result == os.path.join(str(tmp_path), "TransactionDecorator", "dictionary")


def test_user_directory_path_linux_package(monkeypatch):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    if hasattr(sys, "frozen"):
        monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(u, "_is_ide_layout", lambda _: False)
    result = u.user_directory_path("dictionary")
    assert result == os.path.join("/usr/share", "transaction-decorator", "dictionary")


def test_user_directory_path_ide_uses_repo_root(monkeypatch):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    if hasattr(sys, "frozen"):
        monkeypatch.delattr(sys, "frozen", raising=False)
    result = u.user_directory_path("dictionary")
    assert result.endswith(os.path.join("dictionary"))
    # The repo root must contain .idea/ for this branch to fire
    assert os.path.isabs(result)


# ---- normalize_number_format additional negative paths ---------------------

def test_resource_path_frozen_other_falls_back_to_repo_root(monkeypatch):
    """Frozen on a non-Windows platform (rare but possible): falls through to repo-root style."""
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    result = u.resource_path("icons/logo.png")
    # FROZEN_OTHER falls through to _repo_root() (best-effort dev-style layout)
    assert result.endswith("icons/logo.png") or result.endswith(os.path.join("icons", "logo.png"))
    assert os.path.isabs(result)


def test_resource_path_unknown_falls_back_to_repo_root(monkeypatch):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    if hasattr(sys, "frozen"):
        monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "platform", "freebsd")
    monkeypatch.setattr(u, "_is_ide_layout", lambda _: False)
    result = u.resource_path("icons/logo.png")
    assert result.endswith("icons/logo.png") or result.endswith(os.path.join("icons", "logo.png"))
    assert os.path.isabs(result)


def test_user_directory_path_frozen_other_creates_dir_if_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    # Force resource_path to return a path under tmp_path so makedirs is testable
    monkeypatch.setattr(u, "resource_path", lambda rel: str(tmp_path / rel))
    target = tmp_path / "newly-created-dir"
    assert not target.exists()
    result = u.user_directory_path("newly-created-dir")
    assert result == str(target)
    assert target.exists(), "FROZEN_OTHER branch must auto-create the target directory"


def test_user_directory_path_unknown_falls_back_to_resource_path(monkeypatch):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    if hasattr(sys, "frozen"):
        monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "platform", "freebsd")
    monkeypatch.setattr(u, "_is_ide_layout", lambda _: False)
    monkeypatch.setattr(u, "resource_path", lambda rel: f"/synthetic/{rel}")
    result = u.user_directory_path("dictionary")
    assert result == "/synthetic/dictionary"


@pytest.mark.parametrize("value", ["", "abc", "1.2.3.4", "..,,"])
def test_normalize_number_format_unrecognized_warns(value, caplog):
    with caplog.at_level("WARNING"):
        normalize_number_format(value, dot_decimal_separator=True)
    if value:  # empty string takes a different path (replace is no-op)
        assert any("Unrecognized number format" in rec.message for rec in caplog.records)


def test_normalize_number_format_empty_string_returns_empty():
    assert normalize_number_format("", dot_decimal_separator=True) == ""
    assert normalize_number_format("", dot_decimal_separator=False) == ""


def test_normalize_number_format_zero():
    assert normalize_number_format("0", dot_decimal_separator=True) == "0"
    assert normalize_number_format("0,00", dot_decimal_separator=True) == "0.00"
    assert normalize_number_format("0.00", dot_decimal_separator=False) == "0,00"
