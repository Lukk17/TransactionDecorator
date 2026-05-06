import os

import pytest

from utils import utils as u


def test_is_snap_true_when_env_matches(monkeypatch):
    monkeypatch.setenv("TRANSACTION_DECORATOR_SNAP_NAME", "td")
    monkeypatch.setenv("SNAP_NAME", "td")
    assert u.is_snap() is True


def test_is_snap_false_when_names_differ(monkeypatch):
    monkeypatch.setenv("TRANSACTION_DECORATOR_SNAP_NAME", "td")
    monkeypatch.setenv("SNAP_NAME", "other")
    assert u.is_snap() is False


def test_is_snap_false_when_unset(monkeypatch):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    monkeypatch.delenv("SNAP_NAME", raising=False)
    assert u.is_snap() is False


def test_resource_path_snap_branch(monkeypatch):
    monkeypatch.setenv("TRANSACTION_DECORATOR_SNAP_NAME", "td")
    monkeypatch.setenv("SNAP_NAME", "td")
    monkeypatch.setenv("SNAP", "/snap/td/x1")
    result = u.resource_path("icons/logo.png")
    assert result == os.path.join("/snap/td/x1", "usr", "share", "td", "icons/logo.png")


def test_user_directory_path_snap_branch(monkeypatch):
    monkeypatch.setenv("TRANSACTION_DECORATOR_SNAP_NAME", "td")
    monkeypatch.setenv("SNAP_NAME", "td")
    monkeypatch.setenv("SNAP_USER_DATA", "/home/u/snap/td/current")
    assert u.user_directory_path("dictionary") == os.path.join("/home/u/snap/td/current", "dictionary")


def test_resource_path_ide_branch_uses_repo_root(monkeypatch):
    monkeypatch.delenv("TRANSACTION_DECORATOR_SNAP_NAME", raising=False)
    monkeypatch.delenv("SNAP_NAME", raising=False)
    # Not frozen by default; the repo root contains .idea/ in this checkout.
    result = u.resource_path("README.md")
    assert result.endswith(os.path.join("README.md"))
    assert os.path.exists(result), "IDE branch should resolve to existing repo root"
