import logging
import os
import sys
from subprocess import Popen

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QHBoxLayout, QPushButton, QLabel, QLineEdit, QVBoxLayout,
                                QCheckBox, QSpacerItem, QSizePolicy, QDialog, QComboBox, QDialogButtonBox)

import config.constants as cts
from config.style_config import get_checkbox_style, get_import_dialog_style
from gui_elements.confirmation_dialog import ConfirmationDialog
from processor.transactions_importer import import_csv
from utils.utils import user_directory_path, resource_path

logger = logging.getLogger(__name__)


def create_labeled_input(label_text, placeholder):
    layout = QHBoxLayout()
    label = QLabel(label_text)
    label.setStyleSheet(f"color: '{cts.CHECKBOX_LABEL_TEXT_COLOR}';")
    layout.addWidget(label)

    input_field = QLineEdit(placeholder)
    input_field.setStyleSheet(f"color: '{cts.CHECKBOX_INPUT_TEXT_COLOR}';")
    layout.addWidget(input_field)
    return input_field, layout


def open_directory(relative_path):
    directory_path = user_directory_path(relative_path)
    if sys.platform == "win32":
        os.startfile(directory_path)
    else:
        Popen(["xdg-open", directory_path])


def create_pop_up(is_success, message):
    dialog = ConfirmationDialog(is_success=is_success, message=message)
    dialog.exec()


def create_directory_button(button_text, directory_path, icon):
    button = QPushButton()
    button.clicked.connect(lambda: open_directory(directory_path))
    button.setToolTip(button_text)
    button.setIcon(icon)
    return button


def create_import_button(main_window):
    button = QPushButton(cts.IMPORT_CSV_BUTTON_NAME, main_window)
    button.setStyleSheet(f"color: {cts.BUTTON_TEXT_COLOR};")
    button.setToolTip(cts.IMPORT_CSV_BUTTON_NAME)
    button.clicked.connect(lambda: import_csv(main_window))
    return button


def create_input_dialog(main_window):
    dialog = QDialog(main_window)
    dialog.setWindowTitle(cts.IMPORTING_DELIMITER_SELECTION_TITLE)

    layout = QVBoxLayout()
    layout.addWidget(QLabel(cts.IMPORTING_DELIMITER_LABEL_TITLE))

    combo_box = QComboBox()
    combo_box.addItems(cts.DELIMITERS_LIST)
    layout.addWidget(combo_box)

    english_decimal_separator_checkbox = QCheckBox("Convert to english [.] decimal separator")
    english_decimal_separator_checkbox.setChecked(True)
    layout.addWidget(english_decimal_separator_checkbox)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    dialog.setLayout(layout)
    dialog.setStyleSheet(get_import_dialog_style())

    ok = dialog.exec()
    delimiter = combo_box.currentText() if ok else None
    return delimiter, english_decimal_separator_checkbox.isChecked(), ok


def create_force_update(main_window):
    layout = QHBoxLayout(main_window)
    layout.setAlignment(Qt.AlignCenter)
    style = get_checkbox_style()

    force_update_categories_checkbox = QCheckBox("Force categories update")
    force_update_labels_checkbox = QCheckBox("Force labels update")
    force_update_categories_checkbox.setStyleSheet(style)
    force_update_labels_checkbox.setStyleSheet(style)

    layout.addWidget(force_update_categories_checkbox)
    layout.addSpacerItem(QSpacerItem(50, 50, QSizePolicy.Minimum, QSizePolicy.Expanding))
    layout.addWidget(force_update_labels_checkbox)
    return layout, force_update_categories_checkbox, force_update_labels_checkbox


def create_english_decimal_separator(main_window):
    layout = QVBoxLayout(main_window)
    layout.setAlignment(Qt.AlignCenter)

    checkbox = QCheckBox("English [.] decimal separator")
    checkbox.setStyleSheet(get_checkbox_style())
    checkbox.setChecked(True)

    layout.addWidget(checkbox)
    layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
    return layout, checkbox


def create_dir_buttons(main_window):
    layout = QHBoxLayout(main_window)

    dictionary_button = create_directory_button(
        cts.DICTIONARY_DIRECTORY_BUTTON_NAME,
        cts.DICTIONARY_DIRECTORY_PATH,
        QIcon(resource_path(cts.ICON_DICTIONARY_PATH)),
    )
    backup_button = create_directory_button(
        cts.OPEN_BACKUP_DIRECTORY_BUTTON_NAME,
        cts.FILE_BACKUP_DIRECTORY_PATH,
        QIcon(resource_path(cts.ICON_BACKUP_PATH)),
    )
    csv_button = create_directory_button(
        cts.CSV_DIRECTORY_BUTTON_NAME,
        cts.CSV_FILE_DIRECTORY_PATH,
        QIcon(resource_path(cts.ICON_CSV_PATH)),
    )
    import_csv_button = create_import_button(main_window)

    layout.addWidget(dictionary_button)
    layout.addWidget(backup_button)
    layout.addWidget(csv_button)
    layout.addWidget(import_csv_button)
    return layout, csv_button
