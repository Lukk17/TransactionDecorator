from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

import src.config.constants as cts


def get_main_stylesheet():
    return f"""
        QDialog {{
            background-color: {cts.BACKGROUND_COLOR};
            border-radius: {cts.BORDER_RADIUS};
            padding: 0px;
        }}
        QLabel {{
            color: {cts.FIELD_TEXT_COLOR};
        }}
    """


def get_button_stylesheet():
    return f"""
        QPushButton {{
            background-color: {cts.PROCESS_BUTTON_BACKGROUND_COLOR};
            border-radius: 10px;
            padding: 10px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: {cts.PROCESS_BUTTON_HOVER_COLOR};
        }}
        QPushButton:pressed {{
            background-color: {cts.PROCESS_BUTTON_PRESSED_COLOR};
        }}
    """


class ConfirmationDialog(QDialog):
    def __init__(self, is_success, message, parent=None):
        super().__init__(parent)
        self.m_dragPosition = None
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon(cts.APP_ICON))
        self.setFixedSize(300, 200)

        if is_success:
            self.setWindowTitle("Success")
            font_size = cts.SUCCESS_DIALOG_FONT_SIZE
        else:
            self.setWindowTitle("Error")
            font_size = cts.ERROR_DIALOG_FONT_SIZE

        # Use QVBoxLayout for vertical layout
        layout = QVBoxLayout()

        # Create a label with the success message
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)  # Center the text
        font = label.font()
        font.setPointSize(font_size)
        label.setFont(font)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {cts.FIELD_TEXT_COLOR};")

        # Create an OK button with the appropriate styling
        ok_button = QPushButton(cts.CONFIRMATION_BUTTON_TEXT)
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
