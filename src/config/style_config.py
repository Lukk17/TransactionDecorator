import src.config.constants as cts


def get_app_style():
    return f"""
            QMainWindow {{
                padding: 0px;
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
                box-shadow: 4px 4px 6px #1a1c1e, -4px -4px 6px #3e4247;
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
                color: white; 
                padding: 5px; 
            }}
            QPushButton:hover {{
                background-color: {cts.PROCESS_BUTTON_HOVER_COLOR}; 
            }}
        """
