from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

import src.config.constants as cts


def get_main_stylesheet():
    return f"""
        QDialog {{
            background-color: {cts.background_color};
            border-radius: {cts.border_radius};
            padding: 0px;
        }}
        QLabel {{
            color: {cts.field_text_color};
        }}
    """


def get_button_stylesheet():
    return f"""
        QPushButton {{
            background-color: {cts.process_button_background_color};
            border-radius: 10px;
            padding: 10px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: {cts.process_button_hover_color};
        }}
        QPushButton:pressed {{
            background-color: {cts.process_button_pressed_color};
        }}
    """


class ConfirmationDialog(QDialog):
    def __init__(self, is_success, message, parent=None):
        super().__init__(parent)
        self.m_dragPosition = None
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowTitle("Success" if is_success else "Error")
        self.setFixedSize(300, 200)
        self.setWindowIcon(QIcon(cts.app_icon))

        # Use QVBoxLayout for vertical layout
        layout = QVBoxLayout()

        # Create a label with the success message
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)  # Center the text
        font = label.font()
        font.setPointSize(cts.dialog_font_size)
        label.setFont(font)
        label.setStyleSheet(f"color: {cts.field_text_color};")

        # Create an OK button with the appropriate styling
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet(get_button_stylesheet())
        ok_button.clicked.connect(self.accept)  # Connect the button click to QDialog's accept slot

        # Add widgets to the layout
        layout.addWidget(label)
        layout.addWidget(ok_button)

        # Set the layout on the QDialog
        self.setLayout(layout)

        # Apply the main window style to the QDialog
        self.setStyleSheet(get_main_stylesheet())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_dragPosition = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.m_dragPosition)
            self.m_dragPosition = event.globalPosition().toPoint()
            event.accept()
