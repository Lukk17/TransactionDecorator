import os
import sys
from subprocess import Popen

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QHBoxLayout, QPushButton, QLabel, QLineEdit, QVBoxLayout,
                               QCheckBox, QSpacerItem, QSizePolicy, QDialog, QComboBox, QDialogButtonBox)

import src.config.constants as cts
from src.config.style_config import get_checkbox_style, get_import_dialog_style
from src.gui_elements.confirmation_dialog import ConfirmationDialog
from src.processor.process_import import import_csv
from src.utils.utils import user_directory_path, resource_path


def create_labeled_input(label_text, placeholder):
    layout = QHBoxLayout()
    label = QLabel(label_text)
    label.setStyleSheet(f"""color: '{cts.CHECKBOX_LABEL_TEXT_COLOR}';""")

    layout.addWidget(label)

    input_field = QLineEdit(placeholder)
    input_field.setStyleSheet(f"""color: '{cts.CHECKBOX_INPUT_TEXT_COLOR}';""")

    layout.addWidget(input_field)
    return input_field, layout


def open_directory(relative_path):
    # Open the directory with the default file manager
    directory_path = user_directory_path(relative_path)
    if sys.platform == "win32":
        os.startfile(directory_path)

    elif sys.platform == "darwin":
        Popen(["open", directory_path])

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

    # Main layout
    layout = QVBoxLayout()

    # Label for the combo box
    label = QLabel(cts.IMPORTING_DELIMITER_LABEL_TITLE)
    layout.addWidget(label)

    # Combo box for selecting the delimiter
    combo_box = QComboBox()
    combo_box.addItems(cts.DELIMITERS_LIST)
    layout.addWidget(combo_box)

    # Checkbox for selecting the decimal separator format
    english_decimal_separator_checkbox = QCheckBox("Convert to english [.] decimal separator")
    english_decimal_separator_checkbox.setChecked(True)
    layout.addWidget(english_decimal_separator_checkbox)

    # Dialog buttons
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    # Set the dialog layout
    dialog.setLayout(layout)

    # Style the dialog (optional, based on your application's styling requirements)
    dialog.setStyleSheet(get_import_dialog_style())

    # Execute the dialog and get the result
    ok = dialog.exec_()
    delimiter = combo_box.currentText() if ok else None

    english_decimal_separator = english_decimal_separator_checkbox.isChecked()

    return delimiter, english_decimal_separator, ok


def create_force_update(main_window):
    force_update_layout = QHBoxLayout(main_window)
    force_update_layout.setAlignment(Qt.AlignCenter)
    checkbox_style = get_checkbox_style()

    force_update_categories_checkbox = QCheckBox("Force categories update")
    force_update_labels_checkbox = QCheckBox("Force labels update")

    force_update_categories_checkbox.setStyleSheet(checkbox_style)
    force_update_labels_checkbox.setStyleSheet(checkbox_style)

    force_update_layout.addWidget(force_update_categories_checkbox)
    force_update_layout.addSpacerItem(QSpacerItem(50, 50, QSizePolicy.Minimum, QSizePolicy.Expanding))
    force_update_layout.addWidget(force_update_labels_checkbox)

    return force_update_layout, force_update_categories_checkbox, force_update_labels_checkbox


def create_english_decimal_separator(main_window):
    english_decimal_separator_layout = QVBoxLayout(main_window)
    english_decimal_separator_layout.setAlignment(Qt.AlignCenter)
    checkbox_style = get_checkbox_style()

    english_decimal_separator_checkbox = QCheckBox("English [.] decimal separator")

    english_decimal_separator_checkbox.setStyleSheet(checkbox_style)
    english_decimal_separator_checkbox.setChecked(1)

    english_decimal_separator_layout.addWidget(english_decimal_separator_checkbox)
    english_decimal_separator_layout.addSpacerItem(
        QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

    return english_decimal_separator_layout, english_decimal_separator_checkbox


def create_dir_buttons(main_window):
    dir_buttons_layout = QHBoxLayout(main_window)

    dictionary_button = create_directory_button(
        '%s' % cts.DICTIONARY_DIRECTORY_BUTTON_NAME,
        f'{cts.DICTIONARY_DIRECTORY_PATH}/',
        QIcon(resource_path('%s' % cts.ICON_DICTIONARY_PATH))
    )
    backup_button = create_directory_button(
        '%s' % cts.OPEN_BACKUP_DIRECTORY_BUTTON_NAME,
        f'{cts.FILE_BACKUP_DIRECTORY_PATH}/',
        QIcon(resource_path('%s' % cts.ICON_BACKUP_PATH))
    )
    csv_button = create_directory_button(
        '%s' % cts.CSV_DIRECTORY_BUTTON_NAME,
        f'{cts.CSV_FILE_DIRECTORY_PATH}/',
        QIcon(resource_path('%s' % cts.ICON_CSV_PATH))
    )

    import_csv_button = create_import_button(main_window)

    dir_buttons_layout.addWidget(dictionary_button)
    dir_buttons_layout.addWidget(backup_button)
    dir_buttons_layout.addWidget(csv_button)
    dir_buttons_layout.addWidget(import_csv_button)

    return dir_buttons_layout, csv_button
