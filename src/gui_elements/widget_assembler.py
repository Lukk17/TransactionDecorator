import os
import sys
from subprocess import Popen

from PySide6.QtWidgets import (QHBoxLayout, QPushButton, QLabel, QLineEdit, QInputDialog)

import src.config.constants as cts
from src.gui_elements.confirmation_dialog import ConfirmationDialog
from src.processor.process_import import import_csv
from src.utils.utils import user_directory_path


def create_labeled_input(label_text, placeholder):
    layout = QHBoxLayout()
    label = QLabel(label_text)
    layout.addWidget(label)

    input_field = QLineEdit(placeholder)
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
    input_dialog = QInputDialog(main_window)
    input_dialog.setWindowTitle(cts.IMPORTING_DELIMITER_SELECTION_TITLE)
    input_dialog.setLabelText(cts.IMPORTING_DELIMITER_LABEL_TITLE)
    input_dialog.setComboBoxItems(cts.DELIMITERS_LIST)

    input_dialog.setComboBoxEditable(False)
    input_dialog.setStyleSheet(f"""
            QInputDialog {{ 
                background-color: {cts.BACKGROUND_COLOR}; 
                color: {cts.BUTTON_TEXT_COLOR};
            }}
            QLabel {{ color: {cts.BUTTON_TEXT_COLOR}; }}
            QPushButton {{ 
                background-color: {cts.BUTTON_BACKGROUND_COLOR}; 
                color: {cts.BUTTON_TEXT_COLOR}; 
            }}
            QPushButton:hover {{ background-color: {cts.BUTTON_HOVER_COLOR}; }}
            QPushButton:pressed {{ background-color: {cts.BUTTON_PRESSED_COLOR}; }}
            QComboBox {{ 
                background-color: {cts.BACKGROUND_COLOR}; 
                color: {cts.BUTTON_TEXT_COLOR}; 
            }}
            QComboBox QAbstractItemView {{ 
                background-color: {cts.BACKGROUND_COLOR}; 
                color: {cts.BUTTON_TEXT_COLOR}; 
            }}
            QComboBox:focus {{ border: none; }}
        """)
    # Execute the dialog and get the result
    ok = input_dialog.exec_()
    delimiter = input_dialog.textValue() if ok else None
    return delimiter, ok
