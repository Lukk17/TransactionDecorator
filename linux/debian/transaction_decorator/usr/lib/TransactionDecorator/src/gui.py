from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget)

from src.config.style_config import get_app_style, get_process_button_style
from src.gui_elements.title_bar import TitleBar
from src.gui_elements.widget_assembler import *
from src.processor.process_transactions import *
from src.utils.utils import resource_path


class FramelessMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.m_dragPosition = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle("%s" % cts.MAIN_WINDOW_TITLE)
        self.setWindowIcon(QIcon(resource_path(cts.APP_ICON)))

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
        self.dir_buttons_layout, self.csv_button = create_dir_buttons(self)

        self.content_layout.addLayout(self.dir_buttons_layout)

        # QVBoxLayout for vertical, QHBoxLayout for horizontal
        self.input_fields_layout = QHBoxLayout()

        # First Row Input
        self.first_row_input_field, self.first_row_layout = create_labeled_input('%s' % cts.FIRST_ROW_LABEL, '1')

        self.input_fields_layout.addLayout(self.first_row_layout)

        # Last Row Input
        self.last_row_input_field, self.last_row_layout = create_labeled_input('%s' % cts.LAST_ROW_LABEL, '')
        self.input_fields_layout.addLayout(self.last_row_layout)

        self.content_layout.addLayout(self.input_fields_layout)

        (self.english_decimal_separator_layout,
         self.english_decimal_separator_checkbox) = create_english_decimal_separator(self)

        (self.force_update_layout,
         self.force_update_categories_checkbox,
         self.force_update_labels_checkbox) = create_force_update(self)

        self.content_layout.addLayout(self.force_update_layout)
        self.content_layout.addLayout(self.english_decimal_separator_layout)

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
        button = QPushButton('%s' % cts.RUN_PROCESSING_BUTTON_NAME)
        button.clicked.connect(self.run_processing)
        return button

    def run_processing(self):
        first_row = int(self.first_row_input_field.text())
        last_row = int(self.last_row_input_field.text()) if self.last_row_input_field.text() else None

        update_existing_categories = self.force_update_categories_checkbox.isChecked()
        update_existing_labels = self.force_update_labels_checkbox.isChecked()
        english_decimal_separator = self.english_decimal_separator_checkbox.isChecked()

        is_success, message = process_transactions(first_row=first_row, last_row=last_row,
                                                   update_existing_categories=update_existing_categories,
                                                   update_existing_labels=update_existing_labels,
                                                   english_decimal_separator=english_decimal_separator
                                                   )
        create_pop_up(is_success, message)

        if is_success:
            self.open_csv_directory()

    def open_csv_directory(self):
        # Programmatically trigger a click on the csv_button
        self.csv_button.click()

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
