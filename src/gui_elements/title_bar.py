from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
import config.constants as cts
from utils.utils import resource_path


class TitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # No margins
        self.layout.setSpacing(0)  # No spacing between widgets
        self.setStyleSheet(f"background-color: {cts.BACKGROUND_COLOR};")  # Title bar background color

        self.minimize_icon = QIcon(resource_path(cts.MINIMIZE_ICON_PATH))
        self.close_icon = QIcon(resource_path(cts.CLOSE_ICON_PATH))

        # Control Buttons
        button_size = 30  # The fixed size for the buttons
        self.minimalize_button = self.init_button(self.minimize_icon, parent.showMinimized, button_size)
        self.close_button = self.init_button(self.close_icon, parent.close, button_size)

        # Spacer to push buttons to the right
        self.layout.addStretch(1)

        # Add buttons to layout
        self.layout.addWidget(self.minimalize_button, alignment=Qt.AlignTop)
        self.layout.addWidget(self.close_button, alignment=Qt.AlignTop)

        # Set the title bar and its layout margins to zero
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Set the title bar height to match the buttons' height
        self.setFixedHeight(button_size)

    def init_button(self, icon, callback, button_size):
        button = QPushButton()
        button.setFixedSize(button_size, button_size)
        button.clicked.connect(callback)
        button_style = f"""
            QPushButton {{ 
                background-color: {cts.CONTROL_BUTTON_BACKGROUND_COLOR}; 
                border: none; 
                icon-size: {cts.CONTROL_BUTTON_ICON_SIZE};
            }}
            QPushButton:hover {{ 
                background-color: {cts.CONTROL_BUTTON_HOVER_COLOR};
            }}
            QPushButton:pressed {{
            background-color: {cts.BUTTON_PRESSED_COLOR};
            }}
        """
        button.setStyleSheet(button_style)
        button.setIcon(icon)

        return button

    def toggle_maximize_restore(self, button, maximize_icon, restore_icon):
        if self.isMaximized():
            self.showNormal()
            button.setIcon(maximize_icon)  # Change to maximize icon when a window is normal
        else:
            self.showMaximized()
            button.setIcon(restore_icon)

