"""Qt UI tests for gui_elements/confirmation_dialog."""
import pytest

pytest.importorskip("pytestqt")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

import config.constants as cts
from gui_elements.confirmation_dialog import ConfirmationDialog


def test_confirmation_dialog_success_uses_success_font_size(qtbot):
    dlg = ConfirmationDialog(is_success=True, message="OK")
    qtbot.addWidget(dlg)
    label = dlg.findChild(QLabel)
    assert label is not None
    assert label.font().pointSize() == cts.SUCCESS_DIALOG_FONT_SIZE


def test_confirmation_dialog_error_uses_error_font_size(qtbot):
    dlg = ConfirmationDialog(is_success=False, message="Error!")
    qtbot.addWidget(dlg)
    label = dlg.findChild(QLabel)
    assert label is not None
    assert label.font().pointSize() == cts.ERROR_DIALOG_FONT_SIZE


def test_confirmation_dialog_message_rendered(qtbot):
    dlg = ConfirmationDialog(is_success=True, message="Hello world")
    qtbot.addWidget(dlg)
    label = dlg.findChild(QLabel)
    assert label.text() == "Hello world"


def test_confirmation_dialog_window_title(qtbot):
    success = ConfirmationDialog(is_success=True, message="m")
    qtbot.addWidget(success)
    error = ConfirmationDialog(is_success=False, message="m")
    qtbot.addWidget(error)
    assert success.windowTitle() == "Success"
    assert error.windowTitle() == "Error"


def test_confirmation_dialog_ok_button_accepts(qtbot):
    dlg = ConfirmationDialog(is_success=True, message="m")
    qtbot.addWidget(dlg)
    ok_button = dlg.findChild(QPushButton)
    assert ok_button is not None
    assert ok_button.text() == cts.CONFIRMATION_BUTTON_TEXT
    # Connect to a recorder to verify accept fires
    accepted = {"v": False}
    dlg.accepted.connect(lambda: accepted.update(v=True))
    qtbot.mouseClick(ok_button, Qt.LeftButton)
    assert accepted["v"] is True
