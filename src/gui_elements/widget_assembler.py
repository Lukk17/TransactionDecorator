import os
import sys
from subprocess import Popen

from PySide6.QtWidgets import (QHBoxLayout, QPushButton, QLabel, QLineEdit)

from src.gui_elements.confirmation_dialog import ConfirmationDialog
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
