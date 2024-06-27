import config.constants as cts


def get_app_style():
    return f"""
            QWidget {{ 
                border-radius: 15px;
                background-color: {cts.BACKGROUND_COLOR};
            }}
            QPushButton {{
                background-color: {cts.BUTTON_BACKGROUND_COLOR};
                border-radius: {cts.BORDER_RADIUS};
                border: none;
                padding: {cts.BUTTON_PADDING};
                icon-size: {cts.FOLDER_ICON_SIZE};
            }}
            QPushButton:hover {{
                background-color: {cts.BUTTON_HOVER_COLOR};
            }}
            QPushButton:pressed {{
                background-color: {cts.BUTTON_PRESSED_COLOR};
            }}
            QLineEdit {{
                color: {cts.FIELD_TEXT_COLOR};
                background-color: {cts.FIELD_BACKGROUND_COLOR};
                border-radius: {cts.BORDER_RADIUS};
                padding: 5px;
                border: none;
                outline: none;
            }}
            QLineEdit:hover {{
                background-color: {cts.FIELD_HOVER_COLOR};
            }}
            QLineEdit:focus {{
                background-color: {cts.FIELD_FOCUS_COLOR};
            }}
            QLabel {{
                color: {cts.LABEL_TEXT_COLOR};
            }}
        """


def get_process_button_style():
    return f"""
            QPushButton {{
                background-color: {cts.PROCESS_BUTTON_BACKGROUND_COLOR}; 
                border: none; 
                color: {cts.PROCESS_BUTTON_TEXT_COLOR}; 
                padding: 5px; 
            }}
            QPushButton:hover {{
                background-color: {cts.PROCESS_BUTTON_HOVER_COLOR}; 
            }}
        """


def get_checkbox_style():
    return f"""
            QCheckBox {{
                background-color: {cts.CHECKBOX_BACKGROUND_COLOR};
                color: {cts.CHECKBOX_LABEL_TEXT_COLOR};
            }}
            QCheckBox::indicator {{
                background-color: {cts.CHECKBOX_NOT_PRESSED_COLOR};
            }}
            QCheckBox::indicator:checked {{
                background-color: {cts.CHECKBOX_PRESSED_COLOR};
            }}
        """


def get_import_dialog_style():
    return f"""
            QDialog {{ 
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
            
            QCheckBox {{
                background-color: {cts.CHECKBOX_BACKGROUND_COLOR};
                color: {cts.CHECKBOX_LABEL_TEXT_COLOR};
            }}
            QCheckBox::indicator {{
                background-color: {cts.CHECKBOX_NOT_PRESSED_COLOR};
            }}
            QCheckBox::indicator:checked {{
                background-color: {cts.CHECKBOX_PRESSED_COLOR};
            }}
        """
