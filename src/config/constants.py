APP_NAME = 'TransactionDecorator'

# Processing constants
CSV_DELIMITER = ';'
LABELS_DELIMITER = ','
DEFAULT_ENCODING = 'UTF-8'
NOTE_COLUMN = 'Note'
LABELS_COLUMN = 'Labels'
CATEGORIES_COLUMN = 'Category name'

CHARACTERS_NORMALIZATION_MAP = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
    'ó': 'o', 'ś': 's', 'ż': 'z', 'ź': 'z'
}

IMPORTING_DELIMITER_LABEL_TITLE = "Choose the CSV delimiter:"
IMPORTING_DELIMITER_SELECTION_TITLE = "Select Delimiter"
DELIMITERS_LIST = [";", ","]

ERROR_PARSING_CSV = "Error parsing CSV file in line:"
ERROR_IMPORTING_CSV = ("There was error during parsing - try different delimiter when importing. "
                       "\nError importing CSV file in line:")

INPUT_DATE_FORMATS = [
    "%d.%m.%Y", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M", "%Y-%m-%dT%H:%M:%S+00:00",
    "%Y-%m-%d", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"
]

OUTPUT_DATE_FORMAT = "%d.%m.%Y %H:%M"
BACKUP_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

# Internal constants paths ----------------------------------------
APP_ICON = 'icons/logo.png'

MAXIMIZE_ICON_PATH = 'icons/maximize.png'
RESTORE_ICON_PATH = 'icons/restore.png'
MINIMIZE_ICON_PATH = 'icons/minimize.png'
CLOSE_ICON_PATH = 'icons/close.png'

ICON_CSV_PATH = './icons/csv-file.png'
ICON_BACKUP_PATH = './icons/file-backup.png'
ICON_DICTIONARY_PATH = './icons/dictionary.png'

# External / User constants paths
DICTIONARY_DIRECTORY_PATH = './dictionary'
FILE_BACKUP_DIRECTORY_PATH = './backup'
CSV_FILE_DIRECTORY_PATH = './csv'

CATEGORIES_DICTIONARY_NAME = 'categories-dictionary.json'
LABELS_DICTIONARY_NAME = 'labels-dictionary.json'
IMPORT_DICTIONARY_NAME = 'import-dictionary.json'
TRANSACTION_CSV_NAME = 'allTransactions.csv'

# UI setup ----------------------------------------------------------
MAIN_WINDOW_TITLE = "CSV Processing"
IMPORT_CSV_BUTTON_NAME = "Import CSV"
RUN_PROCESSING_BUTTON_NAME = 'Run Processing'
LAST_ROW_LABEL = 'Last Row (optional):'
FIRST_ROW_LABEL = 'First Row:'
CSV_DIRECTORY_BUTTON_NAME = 'Open CSV Directory'
OPEN_BACKUP_DIRECTORY_BUTTON_NAME = 'Open Backup Directory'
DICTIONARY_DIRECTORY_BUTTON_NAME = 'Open Dictionary Directory'
CONFIRMATION_BUTTON_TEXT = 'OK'
OPEN_CSV_DIALOG_DEFAULT_FILE_FORMAT = "CSV Files (*.csv)"
OPEN_CSV_DIALOG_WINDOW_NAME = "Open CSV"
COMPLETED_SUCCESSFULLY_MESSAGE = "Processing completed successfully."
IMPORTING_COMPLETED_SUCCESSFULLY_MESSAGE = "Importing completed successfully."

# UI size
CONTROL_BUTTON_ICON_SIZE = '15px'
FOLDER_ICON_SIZE = '30px'
BORDER_RADIUS = '10px'
BUTTON_PADDING = '10px'

SUCCESS_DIALOG_FONT_SIZE = 12
ERROR_DIALOG_FONT_SIZE = 6

# Colors
BACKGROUND_COLOR = '#2e2e2e'

BUTTON_BACKGROUND_COLOR = '#333'
BUTTON_HOVER_COLOR = '#35393d'
BUTTON_PRESSED_COLOR = '#e78450'

FIELD_BACKGROUND_COLOR = '#333'
FIELD_HOVER_COLOR = '#35393d'
FIELD_FOCUS_COLOR = '#414449'

LABEL_TEXT_COLOR = '#e0e2e4'
FIELD_TEXT_COLOR = '#e0e2e4'
PROCESS_BUTTON_TEXT_COLOR = '#2e2e2e'
BUTTON_TEXT_COLOR = '#d77337'

CONTROL_BUTTON_BACKGROUND_COLOR = '#2e2e2e'
CONTROL_BUTTON_HOVER_COLOR = '#35393d'

PROCESS_BUTTON_BACKGROUND_COLOR = '#d77337'
PROCESS_BUTTON_HOVER_COLOR = '#e78450'
PROCESS_BUTTON_PRESSED_COLOR = '#e78450'

CHECKBOX_BACKGROUND_COLOR = '#2e2e2e'
CHECKBOX_LABEL_TEXT_COLOR = '#d77337'
CHECKBOX_NOT_PRESSED_COLOR = '#35393d'
CHECKBOX_PRESSED_COLOR = '#d77337'
