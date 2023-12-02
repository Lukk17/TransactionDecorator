import src.config.constants as cts


def get_app_style():
    return f"""
            QMainWindow {{
                padding: 0px;
                background-color: {cts.background_color};
            }}
            QPushButton {{
                background-color: {cts.button_background_color};
                border-radius: {cts.border_radius};
                border: none;
                padding: {cts.button_padding};
                icon-size: {cts.folder_icon_size};
            }}
            QPushButton:hover {{
                background-color: {cts.button_hover_color};
            }}
            QPushButton:pressed {{
                background-color: {cts.button_pressed_color};
            }}
            QLineEdit {{
                color: {cts.field_text_color};
                background-color: {cts.field_background_color};
                border-radius: {cts.border_radius};
                padding: 5px;
                border: none;
                outline: none;
                box-shadow: 4px 4px 6px #1a1c1e, -4px -4px 6px #3e4247;
            }}
            QLineEdit:hover {{
                background-color: {cts.field_hover_color};
            }}
            QLineEdit:focus {{
                background-color: {cts.field_focus_color};
            }}
            QLabel {{
                color: {cts.label_text_color};
            }}
        """


def get_process_button_style():
    return f"""
            QPushButton {{
                background-color: {cts.process_button_background_color}; 
                border: none; 
                color: white; 
                padding: 5px; 
            }}
            QPushButton:hover {{
                background-color: {cts.process_button_hover_color}; 
            }}
        """
