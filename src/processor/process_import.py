import json
import traceback
from datetime import datetime

import chardet
import numpy as np
import pandas as pd
from PySide6.QtWidgets import (QFileDialog)

import config.constants as cts
from utils.utils import user_directory_path, normalize_number_format


def import_csv(main_window):
    # Import moved here due to circular import issue when imported as global one
    from gui_elements.widget_assembler import create_pop_up
    from gui_elements.widget_assembler import create_input_dialog

    file_name, _ = QFileDialog.getOpenFileName(main_window, "%s" % cts.OPEN_CSV_DIALOG_WINDOW_NAME, "",
                                               "%s" % cts.OPEN_CSV_DIALOG_DEFAULT_FILE_FORMAT)
    if file_name:
        delimiter, english_decimal_separator, ok = create_input_dialog(main_window)

        if ok and delimiter:
            is_success, message = process_imported_csv(file_name, delimiter, english_decimal_separator)
            create_pop_up(is_success, message)


def process_imported_csv(imported_csv_file_name, delimiter, english_decimal_separator=True):
    print("Starting importing...")
    try:
        # for printing full csv:
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        # pd.set_option('display.max_colwidth', None)

        import_dictionary_path = user_directory_path(f'{cts.DICTIONARY_DIRECTORY_PATH}/{cts.IMPORT_DICTIONARY_NAME}')
        original_csv_path = user_directory_path(f'{cts.CSV_FILE_DIRECTORY_PATH}/{cts.TRANSACTION_CSV_NAME}')

        print("Determining files encodings...")
        import_dictionary_encoding = detect_encoding(import_dictionary_path)
        import_encoding = detect_encoding(imported_csv_file_name)
        original_encoding = detect_encoding(original_csv_path)

        print(f'Original encoding: {original_encoding}')
        print(f'Import encoding: {import_encoding}')
        print(f'Import dictionary encoding: {import_dictionary_encoding}')

        print("Loading import dictionary for columns names mapping...")
        with open(import_dictionary_path, 'r', encoding=import_dictionary_encoding) as file:
            import_dictionary = json.load(file)
            column_mapping = import_dictionary['column_mapping']

            print("Loading imported and original CSVs...")
            rows_to_skip = find_start_row(imported_csv_file_name, import_dictionary_path)

            if rows_to_skip > 0:
                print(f'Skipping first {rows_to_skip} lines due to not parsable content..')

            imported_csv = pd.read_csv(imported_csv_file_name, delimiter=delimiter, encoding=import_encoding,
                                       quotechar='"',
                                       skiprows=rows_to_skip, index_col=False)

            print("Imported csv columns: ", imported_csv.columns)

            original_csv = pd.read_csv(original_csv_path, delimiter=';', encoding=original_encoding)

            print("Finding corresponding columns using mappings...")
            column_indices = create_column_position_map(column_mapping, imported_csv)
            print("Column indices:", column_indices)

            print("Creating new rows with imported cell values...")
            for _, imported_row in imported_csv.iterrows():
                new_row = assign_imported_values_to_new_row(column_indices, column_mapping,
                                                            imported_row, original_csv, english_decimal_separator
                                                            )

                original_csv = append_new_row_to_original_csv(new_row, original_csv)

            print("Recreating original CSV with new rows...")
            original_csv.to_csv(original_csv_path, index=False, sep=';')

            print("Importing finished.")
            return True, ("%s" % cts.IMPORTING_COMPLETED_SUCCESSFULLY_MESSAGE)

    except Exception as e:
        print(f"{cts.ERROR_IMPORTING_CSV} {e}")
        traceback.print_exc()
        return False, f"{cts.ERROR_IMPORTING_CSV} {e}"


def detect_encoding(file_name):
    with open(file_name, 'rb') as file:
        return chardet.detect(file.read())['encoding']


def find_start_row(file_name, import_dictionary_path, delimiter=';'):
    column_names = load_column_mappings(import_dictionary_path)
    import_encoding = detect_encoding(file_name)

    with open(file_name, 'r', encoding=import_encoding) as file:
        for i, line in enumerate(file):
            if any(line.startswith(col_name) for col_name in column_names):
                if not line.endswith(delimiter + '\n') and not line.endswith(delimiter):
                    # Modify the file to add the delimiter at the end of the header
                    adjust_header(file_name, i, line, import_encoding)
                return i
    return 0


def adjust_header(file_name, line_number, line, import_encoding):
    # Read all lines from the file
    with open(file_name, 'r', encoding=import_encoding) as file:
        lines = file.readlines()

    # Adjust the header line
    lines[line_number] = line.strip() + cts.CSV_DELIMITER + '\n'

    # Write the modified lines back to the file
    with open(file_name, 'w', encoding=import_encoding) as file:
        file.writelines(lines)


def load_column_mappings(json_path):
    import_dictionary_encoding = detect_encoding(json_path)

    with open(json_path, 'r', encoding=import_dictionary_encoding) as file:
        data = json.load(file)
        column_mappings = data['column_mapping']
        # Flatten the list of lists into a single list of column names
        all_columns = [col for sublist in column_mappings.values() for col in sublist]
        return all_columns


def append_new_row_to_original_csv(new_row, original_csv):
    return pd.concat([original_csv, pd.DataFrame([new_row])], ignore_index=True)


def assign_imported_values_to_new_row(column_indices, column_mapping,
                                      imported_row, original_csv, english_decimal_separator):
    date_columns = column_mapping.get("Date", [])
    amount_columns = column_mapping.get("Amount", [])

    new_row = {col: np.nan for col in original_csv.columns}

    for orig_col, idx in column_indices.items():
        if not pd.isna(imported_row.iloc[idx]):
            value = imported_row.iloc[idx]

            if orig_col in date_columns:
                new_row[orig_col] = parse_date(value)
            elif orig_col in amount_columns:
                new_row[orig_col] = normalize_number_format(value, english_decimal_separator)
            else:
                new_row[orig_col] = value

    return new_row


def create_column_position_map(column_mapping, imported_csv):
    column_indices = {}
    for orig_col, possible_cols in column_mapping.items():
        for imp_col in possible_cols:
            if imp_col in imported_csv.columns:
                column_indices[orig_col] = imported_csv.columns.get_loc(imp_col)
                break
    return column_indices


def parse_date(date_str):
    date_formats = cts.INPUT_DATE_FORMATS
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime(cts.OUTPUT_DATE_FORMAT)
        except ValueError:
            continue

    print(f'Error parsing date: {date_str}')
    return None
