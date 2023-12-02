from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout)

import config.constants as cts
from config.style_config import get_app_style, get_process_button_style
from gui_elements.title_bar import TitleBar
from gui_elements.widget_assembler import *
from processor.process_transactions import *


class FramelessMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.m_dragPosition = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle("CSV Processing")
        self.setWindowIcon(QIcon(cts.app_icon))

        # Central Widget and Layouts
        self.central_widget = QWidget()
        # Creates an object that will manage the layout within self.central_widget
        self.main_layout = QVBoxLayout(self.central_widget)
        # Sets the layout manager for central_widget to main_layout
        self.central_widget.setLayout(self.main_layout)
        # sets central_widget as the central widget of the QMainWindow.
        self.setCentralWidget(self.central_widget)

        # Custom Title Bar
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar, alignment=Qt.AlignTop)

        # Content Widget and Layout
        self.content_widget = QWidget()
        # Placing content_widget (which will contain other widgets or layouts)
        # within the space managed by the content_layout.
        # Widgets and layouts that are added to content_layout will appear within content_widget.
        self.content_layout = QVBoxLayout(self.content_widget)

        # Directory Buttons
        self.dir_buttons_layout = QHBoxLayout()

        self.dictionary_button = create_directory_button(
            "Open Dictionary Directory",
            "./dictionary",
            QIcon('icons/dictionary.png')
        )
        self.backup_button = create_directory_button(
            "Open Backup Directory",
            "./backup",
            QIcon('icons/file-backup.png')
        )
        self.csv_button = create_directory_button(
            "Open CSV Directory",
            "./csv",
            QIcon('icons/csv-file.png')
        )

        self.dir_buttons_layout.addWidget(self.dictionary_button)
        self.dir_buttons_layout.addWidget(self.backup_button)
        self.dir_buttons_layout.addWidget(self.csv_button)

        self.content_layout.addLayout(self.dir_buttons_layout)

        # QVBoxLayout for vertical, QHBoxLayout for horizontal
        self.input_fields_layout = QHBoxLayout()

        # First Row Input
        self.first_row_input_field, self.first_row_layout = create_labeled_input("First Row:", "2")
        # self.content_layout.addLayout(self.first_row_layout)

        self.input_fields_layout.addLayout(self.first_row_layout)

        # Last Row Input
        self.last_row_input_field, self.last_row_layout = create_labeled_input("Last Row (optional):", "")
        # self.content_layout.addLayout(self.last_row_layout)
        self.input_fields_layout.addLayout(self.last_row_layout)

        self.content_layout.addLayout(self.input_fields_layout)

        # Process Button
        self.process_button = self.create_process_button()
        self.content_layout.addWidget(self.process_button)

        # Add content to the main layout
        # Widget needs to be added to the layout to be visible,
        # adding content_layout to main_layout will not show widgets in it
        self.main_layout.addWidget(self.content_widget)

        self.set_style()

    def set_style(self):
        self.setStyleSheet(get_app_style())
        self.process_button.setStyleSheet(get_process_button_style())

    def create_process_button(self):
        button = QPushButton("Run Processing")
        button.clicked.connect(self.run_processing)
        return button

    def run_processing(self):
        first_row = int(self.first_row_input_field.text())
        last_row = int(self.last_row_input_field.text()) if self.last_row_input_field.text() else None
        process_transactions(first_row, last_row)
        create_pop_up()

    # Window movement methods
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_dragPosition = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.m_dragPosition)
            self.m_dragPosition = event.globalPosition().toPoint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FramelessMainWindow()
    window.show()
    sys.exit(app.exec())
