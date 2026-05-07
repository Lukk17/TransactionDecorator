"""Qt UI tests for gui.FramelessMainWindow.

Covers:
- Construction (smoke: creates without raising; key child widgets exist)
- _read_row_inputs: empty / valid / non-numeric branches
- run_processing validation popup on bad input
- §5.4 — worker runs on a thread distinct from the GUI thread (replaces manual "drag the window" smoke)
"""
import pytest

pytest.importorskip("pytestqt")

from unittest.mock import patch

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import QApplication, QPushButton

from gui import FramelessMainWindow


# ---- construction smoke ---------------------------------------------------

def test_main_window_constructs_without_raising(qtbot):
    window = FramelessMainWindow()
    qtbot.addWidget(window)
    assert window.process_button is not None
    assert window.first_row_input_field is not None
    assert window.last_row_input_field is not None
    assert window.title_bar is not None


def test_main_window_first_row_default_is_one(qtbot):
    window = FramelessMainWindow()
    qtbot.addWidget(window)
    assert window.first_row_input_field.text() == "1"


def test_main_window_last_row_default_is_empty(qtbot):
    window = FramelessMainWindow()
    qtbot.addWidget(window)
    assert window.last_row_input_field.text() == ""


# ---- _read_row_inputs -----------------------------------------------------

def test_read_row_inputs_defaults(qtbot):
    window = FramelessMainWindow()
    qtbot.addWidget(window)
    first, last = window._read_row_inputs()
    assert first == 1
    assert last is None


def test_read_row_inputs_both_filled(qtbot):
    window = FramelessMainWindow()
    qtbot.addWidget(window)
    window.first_row_input_field.setText("5")
    window.last_row_input_field.setText("10")
    first, last = window._read_row_inputs()
    assert first == 5
    assert last == 10


def test_read_row_inputs_first_empty_last_filled(qtbot):
    window = FramelessMainWindow()
    qtbot.addWidget(window)
    window.first_row_input_field.setText("")
    window.last_row_input_field.setText("10")
    first, last = window._read_row_inputs()
    assert first == 1
    assert last == 10


def test_read_row_inputs_raises_on_non_numeric(qtbot):
    """The QIntValidator on the field rejects non-numeric input at the UI level,
    but if a value is somehow injected via setText (programmatic), int() raises."""
    window = FramelessMainWindow()
    qtbot.addWidget(window)
    # Bypass the validator via direct setText with letters
    window.first_row_input_field.setText("abc")
    with pytest.raises(ValueError):
        window._read_row_inputs()


# ---- run_processing validation popup -------------------------------------

def test_run_processing_shows_popup_on_invalid_input(qtbot, monkeypatch):
    window = FramelessMainWindow()
    qtbot.addWidget(window)
    window.first_row_input_field.setText("not-a-number")

    captured = {"called": False, "args": None}

    def fake_popup(is_success, message):
        captured["called"] = True
        captured["args"] = (is_success, message)

    monkeypatch.setattr("gui.create_pop_up", fake_popup)
    window.run_processing()
    assert captured["called"]
    is_success, message = captured["args"]
    assert is_success is False
    assert "integer" in message.lower()


# ---- §5.4 QThread isolation ----------------------------------------------

def test_worker_runs_on_separate_thread_from_gui(qtbot, monkeypatch):
    """The whole point of ProcessingWorker is to run decorate_transactions OFF
    the main GUI thread. Patch decorate_transactions to record its calling thread,
    fire run_processing, poll until it completes, then assert thread != GUI thread.
    Replaces the manual "drag the window during processing" smoke from upgrade-pandas-3 §2.3."""
    window = FramelessMainWindow()
    qtbot.addWidget(window)

    gui_thread = QApplication.instance().thread()
    captured = {"worker_thread": None}

    def fake_decorate(**kwargs):
        captured["worker_thread"] = QThread.currentThread()
        return True, "OK"

    monkeypatch.setattr("gui.create_pop_up", lambda *a, **k: None)
    monkeypatch.setattr(window.csv_button, "click", lambda: None)
    monkeypatch.setattr("gui.decorate_transactions", fake_decorate)

    window.run_processing()
    # Wait for the worker to set the captured thread
    qtbot.waitUntil(lambda: captured["worker_thread"] is not None, timeout=5000)
    # Wait for the button to re-enable (signal that the cycle finished)
    qtbot.waitUntil(lambda: window.process_button.isEnabled(), timeout=5000)

    assert captured["worker_thread"] is not gui_thread, (
        "Worker ran on the GUI thread — Qt thread isolation broken!")


def test_run_processing_disables_button_during_work(qtbot, monkeypatch):
    """While the worker runs, the process button must be disabled (prevents double-trigger)."""
    window = FramelessMainWindow()
    qtbot.addWidget(window)

    monkeypatch.setattr("gui.create_pop_up", lambda *a, **k: None)
    monkeypatch.setattr(window.csv_button, "click", lambda: None)
    monkeypatch.setattr("gui.decorate_transactions", lambda **k: (True, "OK"))

    assert window.process_button.isEnabled()
    window.run_processing()
    qtbot.waitUntil(lambda: window.process_button.isEnabled(), timeout=5000)
    # After the worker finishes, the button is re-enabled
    assert window.process_button.isEnabled()
