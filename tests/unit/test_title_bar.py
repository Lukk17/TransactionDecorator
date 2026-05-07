"""Qt UI tests for gui_elements/title_bar."""
import pytest

pytest.importorskip("pytestqt")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QPushButton

from gui_elements.title_bar import TitleBar


def test_title_bar_creates_two_buttons(qtbot):
    parent = QMainWindow()
    qtbot.addWidget(parent)
    bar = TitleBar(parent)
    qtbot.addWidget(bar)
    assert isinstance(bar.minimalize_button, QPushButton)
    assert isinstance(bar.close_button, QPushButton)


def test_title_bar_buttons_have_fixed_size(qtbot):
    parent = QMainWindow()
    qtbot.addWidget(parent)
    bar = TitleBar(parent)
    qtbot.addWidget(bar)
    assert bar.minimalize_button.size().width() == 30
    assert bar.minimalize_button.size().height() == 30
    assert bar.close_button.size().width() == 30


def test_title_bar_minimize_button_calls_parent_show_minimized(qtbot, monkeypatch):
    parent = QMainWindow()
    qtbot.addWidget(parent)
    called = {"minimized": False}
    monkeypatch.setattr(parent, "showMinimized", lambda: called.update(minimized=True))
    bar = TitleBar(parent)
    qtbot.addWidget(bar)
    qtbot.mouseClick(bar.minimalize_button, Qt.LeftButton)
    assert called["minimized"] is True


def test_title_bar_close_button_calls_parent_close(qtbot, monkeypatch):
    parent = QMainWindow()
    qtbot.addWidget(parent)
    called = {"closed": False}
    monkeypatch.setattr(parent, "close", lambda: called.update(closed=True) or True)
    bar = TitleBar(parent)
    qtbot.addWidget(bar)
    qtbot.mouseClick(bar.close_button, Qt.LeftButton)
    assert called["closed"] is True
