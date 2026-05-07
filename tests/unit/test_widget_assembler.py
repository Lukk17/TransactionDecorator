"""Qt UI tests for gui_elements/widget_assembler — uses pytest-qt's qtbot fixture."""
import pytest

pytest.importorskip("pytestqt")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QCheckBox, QLineEdit, QPushButton, QWidget

import config.constants as cts
from gui_elements.widget_assembler import (
    create_dir_buttons,
    create_english_decimal_separator,
    create_force_update,
    create_labeled_input,
    create_pop_up,
)


def test_create_labeled_input_returns_lineedit_and_layout(qtbot):
    field, layout = create_labeled_input("Row:", "5")
    assert isinstance(field, QLineEdit)
    assert isinstance(layout, QHBoxLayout)
    assert field.text() == "5"


def test_create_labeled_input_layout_has_label_and_field(qtbot):
    _, layout = create_labeled_input("Test:", "")
    assert layout.count() == 2  # label + input


def test_create_force_update_returns_layout_and_two_checkboxes(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    layout, cat_cb, lbl_cb = create_force_update(parent)
    assert isinstance(layout, QHBoxLayout)
    assert isinstance(cat_cb, QCheckBox)
    assert isinstance(lbl_cb, QCheckBox)
    assert cat_cb.text() == "Force categories update"
    assert lbl_cb.text() == "Force labels update"
    # Default: not checked
    assert cat_cb.isChecked() is False
    assert lbl_cb.isChecked() is False


def test_create_english_decimal_separator_defaults_checked(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    layout, checkbox = create_english_decimal_separator(parent)
    assert isinstance(layout, QVBoxLayout)
    assert isinstance(checkbox, QCheckBox)
    assert checkbox.isChecked() is True
    assert "English" in checkbox.text()


def test_create_force_update_checkbox_state_responds_to_setChecked(qtbot):
    """Verify the checkbox honors setChecked. Toggle-by-click is Qt's standard
    behavior and not what we're testing here — we're verifying our wiring exposes
    a working checkbox."""
    parent = QWidget()
    qtbot.addWidget(parent)
    _, cat_cb, _ = create_force_update(parent)
    cat_cb.setChecked(True)
    assert cat_cb.isChecked() is True
    cat_cb.setChecked(False)
    assert cat_cb.isChecked() is False


def test_create_dir_buttons_creates_four_buttons(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    layout, csv_button = create_dir_buttons(parent)
    # 3 directory buttons + 1 import button
    assert layout.count() == 4
    assert isinstance(csv_button, QPushButton)


def test_create_dir_buttons_csv_button_is_returned_for_external_use(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    _, csv_button = create_dir_buttons(parent)
    # The csv_button must be the third widget in the layout (dictionary, backup, csv, import)
    assert csv_button.toolTip() == cts.CSV_DIRECTORY_BUTTON_NAME


def test_create_pop_up_success_dialog(qtbot, monkeypatch):
    """create_pop_up calls dialog.exec(); patch exec to avoid blocking."""
    monkeypatch.setattr("gui_elements.widget_assembler.ConfirmationDialog.exec", lambda self: 0)
    # Just ensure it doesn't raise
    create_pop_up(True, "Done!")


def test_create_pop_up_error_dialog(qtbot, monkeypatch):
    monkeypatch.setattr("gui_elements.widget_assembler.ConfirmationDialog.exec", lambda self: 0)
    create_pop_up(False, "Something went wrong")


# ---- open_directory (Gap #4) ----------------------------------------------

def test_open_directory_uses_startfile_on_windows(monkeypatch):
    from gui_elements import widget_assembler
    import os as os_real

    captured = {"startfile_path": None, "popen_called": False}

    monkeypatch.setattr("gui_elements.widget_assembler.user_directory_path",
                        lambda rel: f"/resolved/{rel}")
    monkeypatch.setattr("gui_elements.widget_assembler.sys.platform", "win32")
    monkeypatch.setattr(os_real, "startfile",
                        lambda p: captured.update(startfile_path=p), raising=False)
    monkeypatch.setattr("gui_elements.widget_assembler.Popen",
                        lambda *a, **k: captured.update(popen_called=True))

    widget_assembler.open_directory("dictionary")
    assert captured["startfile_path"] == "/resolved/dictionary"
    assert captured["popen_called"] is False


def test_open_directory_uses_xdg_open_on_linux(monkeypatch):
    from gui_elements import widget_assembler

    captured = {"popen_args": None}

    monkeypatch.setattr("gui_elements.widget_assembler.user_directory_path",
                        lambda rel: f"/resolved/{rel}")
    monkeypatch.setattr("gui_elements.widget_assembler.sys.platform", "linux")
    monkeypatch.setattr("gui_elements.widget_assembler.Popen",
                        lambda args: captured.update(popen_args=args))

    widget_assembler.open_directory("backup")
    assert captured["popen_args"] == ["xdg-open", "/resolved/backup"]


# ---- create_input_dialog (Gap #5) -----------------------------------------

def test_create_input_dialog_returns_selection_on_ok(qtbot, monkeypatch):
    from gui_elements import widget_assembler

    # Patch QDialog.exec to return Accepted (1) without showing the dialog
    monkeypatch.setattr("gui_elements.widget_assembler.QDialog.exec", lambda self: 1)
    parent = None
    delimiter, dot_decimal, ok = widget_assembler.create_input_dialog(parent)
    assert ok == 1
    # First item in DELIMITERS_LIST is the default
    assert delimiter == cts.DELIMITERS_LIST[0]
    # English decimal separator checkbox defaults to True
    assert dot_decimal is True


def test_create_input_dialog_returns_none_on_cancel(qtbot, monkeypatch):
    from gui_elements import widget_assembler

    monkeypatch.setattr("gui_elements.widget_assembler.QDialog.exec", lambda self: 0)
    delimiter, dot_decimal, ok = widget_assembler.create_input_dialog(None)
    assert ok == 0
    assert delimiter is None
    # The checkbox state is still readable; ok=0 is the gating signal
    assert dot_decimal is True


# ---- import_csv (Gap #6) — GUI wrapper around process_imported_csv -------

def test_import_csv_calls_process_imported_csv_on_ok(qtbot, monkeypatch, tmp_path):
    from processor import transactions_importer

    csv_path = tmp_path / "bank.csv"
    csv_path.write_text("Date;Note\n01.01.2024;hi\n", encoding="utf-8")

    # Mock the QFileDialog to return our path without showing UI
    monkeypatch.setattr(
        "processor.transactions_importer.QFileDialog.getOpenFileName",
        staticmethod(lambda *a, **k: (str(csv_path), "")),
    )

    # Mock the input dialog to return delimiter=";", dot=True, ok=1
    monkeypatch.setattr(
        "gui_elements.widget_assembler.create_input_dialog",
        lambda mw: (";", True, 1),
    )

    captured = {"args": None}
    monkeypatch.setattr(
        "processor.transactions_importer.process_imported_csv",
        lambda f, delimiter, dot_decimal_separator: captured.update(
            args=(f, delimiter, dot_decimal_separator)) or (True, "OK"),
    )

    popup_called = {"v": False}
    monkeypatch.setattr(
        "gui_elements.widget_assembler.create_pop_up",
        lambda is_success, msg: popup_called.update(v=True),
    )

    transactions_importer.import_csv(main_window=None)

    assert captured["args"] == (str(csv_path), ";", True)
    assert popup_called["v"] is True


def test_import_csv_does_nothing_when_user_cancels_file_dialog(qtbot, monkeypatch):
    from processor import transactions_importer

    monkeypatch.setattr(
        "processor.transactions_importer.QFileDialog.getOpenFileName",
        staticmethod(lambda *a, **k: ("", "")),  # empty path -> user cancelled
    )

    process_called = {"v": False}
    monkeypatch.setattr(
        "processor.transactions_importer.process_imported_csv",
        lambda *a, **k: process_called.update(v=True) or (True, "OK"),
    )

    transactions_importer.import_csv(main_window=None)
    assert process_called["v"] is False, "process_imported_csv must NOT run when user cancels"


def test_import_csv_does_nothing_when_user_cancels_delimiter_dialog(qtbot, monkeypatch, tmp_path):
    from processor import transactions_importer

    csv_path = tmp_path / "bank.csv"
    csv_path.write_text("Date;Note\n01.01.2024;hi\n", encoding="utf-8")

    monkeypatch.setattr(
        "processor.transactions_importer.QFileDialog.getOpenFileName",
        staticmethod(lambda *a, **k: (str(csv_path), "")),
    )

    # User cancels the delimiter dialog -> ok=0
    monkeypatch.setattr(
        "gui_elements.widget_assembler.create_input_dialog",
        lambda mw: (None, True, 0),
    )

    process_called = {"v": False}
    monkeypatch.setattr(
        "processor.transactions_importer.process_imported_csv",
        lambda *a, **k: process_called.update(v=True) or (True, "OK"),
    )

    transactions_importer.import_csv(main_window=None)
    assert process_called["v"] is False, "process_imported_csv must NOT run when delimiter dialog cancelled"
