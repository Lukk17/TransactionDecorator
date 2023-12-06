from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
import src.config.constants as cts
from src.utils.utils import resource_path


class TitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # No margins
        self.layout.setSpacing(0)  # No spacing between widgets
        self.setStyleSheet("background-color: #2e2e2e;")  # Title bar background color

        self.maximize_icon = QIcon(resource_path('./icons/maximize.png'))
        self.restore_icon = QIcon(resource_path('./icons/restore.png'))
        self.minimize_icon = QIcon(resource_path('./icons/minimize.png'))
        self.close_icon = QIcon(resource_path('./icons/close.png'))

        # Control Buttons
        button_size = 30  # The fixed size for the buttons
        self.minimalize_button = self.init_button(self.minimize_icon, parent.showMinimized, button_size)
        self.maximize_button = self.init_maxi_resto_button(button_size, parent)
        self.close_button = self.init_button(self.close_icon, parent.close, button_size)

        # Spacer to push buttons to the right
        self.layout.addStretch(1)

        # Add buttons to layout
        self.layout.addWidget(self.minimalize_button, alignment=Qt.AlignTop)
        self.layout.addWidget(self.maximize_button, alignment=Qt.AlignTop)
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

    def init_maxi_resto_button(self, button_size, parent):
        button = self.init_button(self.maximize_icon, None, button_size)

        if parent.isMaximized():
            button.setIcon(self.restore_icon)
        else:
            button.setIcon(self.maximize_icon)

        button.clicked.connect(lambda: self.toggle_maximize_restore(button, self.maximize_icon, self.restore_icon))

        return button

    def toggle_maximize_restore(self, button, maximize_icon, restore_icon):
        if self.isMaximized():
            self.showNormal()
            button.setIcon(maximize_icon)  # Change to maximize icon when a window is normal
        else:
            self.showMaximized()
            button.setIcon(restore_icon)
