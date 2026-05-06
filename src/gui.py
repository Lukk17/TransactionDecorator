import logging
import os
import sys

from PySide6.QtCore import Qt, QObject, QThread, Signal
from PySide6.QtGui import QIcon, QIntValidator
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                QHBoxLayout, QPushButton)

import config.constants as cts
from config.style_config import get_app_style, get_process_button_style
from gui_elements.title_bar import TitleBar
from gui_elements.widget_assembler import (
    create_dir_buttons, create_labeled_input, create_force_update,
    create_english_decimal_separator, create_pop_up,
)
from processor.transactions_decorator import decorate_transactions
from utils.utils import resource_path, change_to_user_directory

logger = logging.getLogger(__name__)


class ProcessingWorker(QObject):
    """Runs decorate_transactions off the GUI thread to keep the window responsive."""
    finished = Signal(bool, str)

    def __init__(self, **kwargs):
        super().__init__()
        self._kwargs = kwargs

    def run(self):
        try:
            is_success, message = decorate_transactions(**self._kwargs)
        except Exception as e:  # surface to GUI; logged in worker thread
            logger.exception("Worker crashed: %s", e)
            is_success, message = False, str(e)
        self.finished.emit(is_success, message)


class FramelessMainWindow(QMainWindow):

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_dragPosition = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.m_dragPosition)
            event.accept()

    def __init__(self):
        super().__init__()
        self.m_dragPosition = None
        self._thread = None
        self._worker = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle(cts.MAIN_WINDOW_TITLE)
        self.setWindowIcon(QIcon(resource_path(cts.APP_ICON)))
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar, alignment=Qt.AlignTop)
        self.main_layout.addWidget(self._build_content())
        self.set_style()

    def _build_content(self):
        self.dir_buttons_widget = self.setup_buttons_widget()
        self.input_fields_widget = self.setup_input_fields_widget()
        self.english_decimal_separator_widget = self.setup_english_decimal_separator_widget()
        self.force_update_widget = self.setup_force_update_widget()
        self.process_button = self.create_process_button()

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.addWidget(self.dir_buttons_widget)
        layout.addWidget(self.input_fields_widget)
        layout.addWidget(self.english_decimal_separator_widget)
        layout.addWidget(self.force_update_widget)
        layout.addWidget(self.process_button)
        return content

    def setup_force_update_widget(self):
        widget = QWidget()
        (self.force_update_layout,
         self.force_update_categories_checkbox,
         self.force_update_labels_checkbox) = create_force_update(widget)
        widget.setLayout(self.force_update_layout)
        return widget

    def setup_english_decimal_separator_widget(self):
        widget = QWidget()
        (self.english_decimal_separator_layout,
         self.dot_decimal_separator_checkbox) = create_english_decimal_separator(widget)
        widget.setLayout(self.english_decimal_separator_layout)
        return widget

    def setup_input_fields_widget(self):
        widget = QWidget()
        self.input_fields_layout = QHBoxLayout()
        self.first_row_input_field, self.first_row_layout = create_labeled_input(cts.FIRST_ROW_LABEL, '1')
        self.first_row_input_field.setValidator(QIntValidator(1, 10_000_000))
        self.input_fields_layout.addLayout(self.first_row_layout)
        self.last_row_input_field, self.last_row_layout = create_labeled_input(cts.LAST_ROW_LABEL, '')
        self.last_row_input_field.setValidator(QIntValidator(1, 10_000_000))
        self.input_fields_layout.addLayout(self.last_row_layout)
        widget.setLayout(self.input_fields_layout)
        return widget

    def setup_buttons_widget(self):
        widget = QWidget()
        self.dir_buttons_layout, self.csv_button = create_dir_buttons(widget)
        widget.setLayout(self.dir_buttons_layout)
        return widget

    def set_style(self):
        style = get_app_style()
        self.setStyleSheet(style)
        self.central_widget.setStyleSheet(style)
        self.process_button.setStyleSheet(get_process_button_style())

    def create_process_button(self):
        button = QPushButton(cts.RUN_PROCESSING_BUTTON_NAME)
        button.clicked.connect(self.run_processing)
        return button

    def _read_row_inputs(self):
        first_text = self.first_row_input_field.text().strip()
        last_text = self.last_row_input_field.text().strip()
        first_row = int(first_text) if first_text else 1
        last_row = int(last_text) if last_text else None
        return first_row, last_row

    def run_processing(self):
        try:
            first_row, last_row = self._read_row_inputs()
        except ValueError:
            create_pop_up(False, "First/Last Row must be integers.")
            return

        self.process_button.setEnabled(False)
        self._thread = QThread()
        self._worker = ProcessingWorker(
            first_row=first_row,
            last_row=last_row,
            update_existing_categories=self.force_update_categories_checkbox.isChecked(),
            update_existing_labels=self.force_update_labels_checkbox.isChecked(),
            dot_decimal_separator=self.dot_decimal_separator_checkbox.isChecked(),
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_processing_finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _on_processing_finished(self, is_success, message):
        self.process_button.setEnabled(True)
        create_pop_up(is_success, message)
        if is_success:
            self.open_csv_directory()

    def open_csv_directory(self):
        self.csv_button.click()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = QApplication(sys.argv)
    window = FramelessMainWindow()
    change_to_user_directory()
    logger.info("sys.path=%s", sys.path)
    logger.info("PYTHONPATH=%s", os.environ.get('PYTHONPATH'))
    logger.info("platform=%s cwd=%s", sys.platform, os.getcwd())
    window.show()
    sys.exit(app.exec())
