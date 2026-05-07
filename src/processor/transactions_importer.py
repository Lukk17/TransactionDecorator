import io
import json
import logging
import os
import traceback
from datetime import datetime

import chardet
import numpy as np
import pandas as pd
from PySide6.QtWidgets import QFileDialog

import config.constants as cts
from utils.utils import user_directory_path, normalize_number_format, create_original_csv

logger = logging.getLogger(__name__)


def import_csv(main_window):
    # Local imports avoid circular dependency between widget_assembler and this module.
    from gui_elements.widget_assembler import create_pop_up, create_input_dialog

    file_name, _ = QFileDialog.getOpenFileName(
        main_window, cts.OPEN_CSV_DIALOG_WINDOW_NAME, "", cts.OPEN_CSV_DIALOG_DEFAULT_FILE_FORMAT)
    if not file_name:
        return

    delimiter, dot_decimal_separator, ok = create_input_dialog(main_window)
    if ok and delimiter:
        is_success, message = process_imported_csv(file_name, delimiter, dot_decimal_separator)
        create_pop_up(is_success, message)


def process_imported_csv(imported_csv_file_name, delimiter, dot_decimal_separator=True):
    logger.info("Starting importing...")
    try:
        ignore_dict_path = user_directory_path(
            os.path.join(cts.DICTIONARY_DIRECTORY_PATH, cts.IGNORE_DICTIONARY_NAME))
        import_dictionary_path = user_directory_path(
            os.path.join(cts.DICTIONARY_DIRECTORY_PATH, cts.IMPORT_DICTIONARY_NAME))
        original_csv_path = os.path.join(
            user_directory_path(cts.CSV_FILE_DIRECTORY_PATH), cts.TRANSACTION_CSV_NAME)

        ignore_rules = _load_ignore_rules(ignore_dict_path)
        column_mapping = _load_column_mapping(import_dictionary_path)

        import_encoding = detect_encoding(imported_csv_file_name)
        original_encoding = detect_encoding(original_csv_path)
        logger.info("Encodings — original=%s import=%s", original_encoding, import_encoding)

        rows_to_skip, header_fix = find_start_row(imported_csv_file_name, import_dictionary_path)
        if rows_to_skip > 0:
            logger.info("Skipping %d non-parsable header lines", rows_to_skip)

        imported_csv = _read_imported_csv(
            imported_csv_file_name, delimiter, import_encoding, rows_to_skip, header_fix)
        imported_csv = _apply_ignore_rules(imported_csv, ignore_rules)

        if not os.path.exists(original_csv_path) or os.path.getsize(original_csv_path) == 0:
            logger.info("Initializing CSV at %s", original_csv_path)
            create_original_csv(original_csv_path)

        original_csv = pd.read_csv(str(original_csv_path), delimiter=cts.CSV_DELIMITER, encoding=original_encoding)
        column_indices = create_column_position_map(column_mapping, imported_csv)
        logger.info("Column indices: %s", column_indices)

        new_rows = [
            assign_imported_values_to_new_row(
                column_indices, column_mapping, imported_row, original_csv, dot_decimal_separator)
            for _, imported_row in imported_csv.iterrows()
        ]
        if new_rows:
            original_csv = pd.concat([original_csv, pd.DataFrame(new_rows)], ignore_index=True)

        original_csv.to_csv(str(original_csv_path), index=False, sep=cts.CSV_DELIMITER)
        logger.info("Importing finished.")
        return True, cts.IMPORTING_COMPLETED_SUCCESSFULLY_MESSAGE

    except FileNotFoundError as e:
        logger.error("File not found: %s", e)
        return False, "File not found."
    except json.JSONDecodeError as e:
        logger.error("JSON decode error: %s", e)
        return False, "Invalid JSON format."
    except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError, KeyError) as e:
        logger.error("%s %s", cts.ERROR_IMPORTING_CSV, e)
        traceback.print_exc()
        return False, f"{cts.ERROR_IMPORTING_CSV} {e}"


def _load_ignore_rules(path):
    with open(path, 'r', encoding=cts.DEFAULT_ENCODING) as file:
        return json.load(file)[cts.IGNORE_IGNORE_RULES_PARAM_NAME]


def _load_column_mapping(path):
    encoding = detect_encoding(path)
    with open(path, 'r', encoding=encoding) as file:
        return json.load(file)[cts.IMPORT_COLUMN_MAPPING_PARAM_NAME]


def _read_imported_csv(file_name, delimiter, encoding, rows_to_skip, header_fix):
    """Read the imported CSV. If header_fix is set, splice it in-memory rather than mutating the source file."""
    if header_fix is None:
        return pd.read_csv(file_name, delimiter=delimiter, encoding=encoding,
                           quotechar='"', skiprows=rows_to_skip, index_col=False)

    with open(file_name, 'r', encoding=encoding) as f:
        lines = f.readlines()
    lines[header_fix['line_number']] = header_fix['fixed_line']
    buffer = io.StringIO(''.join(lines))
    return pd.read_csv(buffer, delimiter=delimiter, quotechar='"',
                       skiprows=rows_to_skip, index_col=False)


def _apply_ignore_rules(df, ignore_rules):
    for rule in ignore_rules:
        condition = True
        for cond in rule[cts.IGNORE_CONDITION_PARAM_NAME]:
            column_name = cond[cts.IGNORE_COLUMN_PARAM_NAME]
            if column_name in df.columns:
                condition &= (df[column_name] == cond[cts.IGNORE_VALUE_PARAM_NAME])
            else:
                logger.warning("Ignore rule references missing column '%s'", column_name)
                condition = pd.Series(False, index=df.index)
                break
        if isinstance(condition, pd.Series) and condition.any():
            df = df[~condition]
    return df


def detect_encoding(file_name):
    if not os.path.exists(file_name):
        logger.info("File not found: %s. Using default encoding '%s'.", file_name, cts.DEFAULT_ENCODING)
        return cts.DEFAULT_ENCODING

    with open(file_name, 'rb') as file:
        detected_encoding = chardet.detect(file.read())['encoding']

    if detected_encoding is None:
        logger.info("Failed to detect encoding for %s. Using '%s'.", file_name, cts.DEFAULT_ENCODING)
        return cts.DEFAULT_ENCODING
    return detected_encoding


def find_start_row(file_name, import_dictionary_path, delimiter=cts.CSV_DELIMITER):
    """Locate the header row in a possibly-noisy CSV.

    Returns (rows_to_skip, header_fix) where header_fix is None if no fix is needed,
    otherwise a dict {line_number, fixed_line} for in-memory header repair.
    """
    column_names = load_column_mappings(import_dictionary_path)
    import_encoding = detect_encoding(file_name)

    with open(file_name, 'r', encoding=import_encoding) as file:
        for i, line in enumerate(file):
            if any(line.startswith(col_name) for col_name in column_names):
                if not line.endswith(delimiter + '\n') and not line.endswith(delimiter):
                    fixed = line.rstrip('\n') + cts.CSV_DELIMITER + '\n'
                    return i, {'line_number': i, 'fixed_line': fixed}
                return i, None
    return 0, None


def load_column_mappings(json_path):
    encoding = detect_encoding(json_path)
    with open(json_path, 'r', encoding=encoding) as file:
        data = json.load(file)
        return [col for sublist in data['column_mapping'].values() for col in sublist]


def assign_imported_values_to_new_row(column_indices, column_mapping,
                                      imported_row, original_csv, dot_decimal_separator):
    """Build a new row dict from imported values.

    Date/amount routing compares the canonical column name against constants
    (`cts.DATE_COLUMN`, `cts.AMOUNT_COLUMN`) directly. The previous implementation
    checked alias-list membership (`column_mapping.get("Date", [])`), which only
    worked when the user's `import-dictionary.json` happened to list the canonical
    name as one of the aliases. See ADR / `upgrade-pytest-9` §5.2.
    """
    del column_mapping  # retained for backward compatibility / future use; intentionally unused

    new_row = {col: np.nan for col in original_csv.columns}
    for orig_col, idx in column_indices.items():
        if pd.isna(imported_row.iloc[idx]):
            continue
        value = imported_row.iloc[idx]
        if orig_col == cts.DATE_COLUMN:
            new_row[orig_col] = parse_date(value)
        elif orig_col == cts.AMOUNT_COLUMN:
            new_row[orig_col] = normalize_number_format(str(value), dot_decimal_separator)
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
    for fmt in cts.INPUT_DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).strftime(cts.OUTPUT_DATE_FORMAT)
        except ValueError:
            continue
    logger.error("Error parsing date: %s", date_str)
    return None
