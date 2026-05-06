import json
import logging
import os
import shutil
import traceback
from datetime import datetime

import pandas as pd
from pandas.api.types import is_string_dtype

import config.constants as cts
from utils.utils import user_directory_path, normalize_number_format, create_original_csv

logger = logging.getLogger(__name__)

_NORMALIZATION_TABLE = str.maketrans(cts.CHARACTERS_NORMALIZATION_MAP)


def normalize_string(s):
    if pd.isnull(s):
        return ''
    if not isinstance(s, str):
        s = str(s)
    return ' '.join(s.strip().translate(_NORMALIZATION_TABLE).split()).lower()


def create_backup(original_file_path, backup_dir):
    logger.info("Creating backup of CSV file...")
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime(cts.BACKUP_TIMESTAMP_FORMAT)
    backup_file_path = os.path.join(backup_dir, f"{os.path.basename(original_file_path)}_{timestamp}.csv")

    if not os.path.exists(original_file_path) or os.path.getsize(original_file_path) == 0:
        logger.info("Original file missing or empty. Initializing %s.", original_file_path)
        create_original_csv(original_file_path)

    shutil.copy(original_file_path, backup_file_path)


def load_dictionary(dictionary_path):
    logger.info("Loading dictionary %s", dictionary_path)
    with open(dictionary_path, 'r', encoding=cts.DEFAULT_ENCODING) as file:
        dictionary_data = json.load(file)

    inverted_dictionary = invert_dictionary(dictionary_data)
    return {normalize_string(key): value for key, value in inverted_dictionary.items()}


def invert_dictionary(dictionary_data):
    """Swap label→keywords mapping into keyword→labels for fast lookup."""
    inverted_dictionary = {}
    for label, keys in dictionary_data.items():
        for key in keys:
            normalized_key = normalize_string(key)
            inverted_dictionary.setdefault(normalized_key, [])
            normalized_label = normalize_string(label)
            if normalized_label not in inverted_dictionary[normalized_key]:
                inverted_dictionary[normalized_key].append(normalized_label)
    return inverted_dictionary


def update_categories(df, categories_dictionary, first_row, last_row, update_existing_categories=False):
    """See ADR-0005 for "Other" overwrite semantics under force-update."""
    logger.info("Updating categories...")

    for i in range(first_row - 1, min(last_row, len(df))):
        existing_category = find_existing_category(df, i)
        is_category_empty = pd.isna(existing_category) or existing_category in (None, 'nan', '')

        if (not update_existing_categories and not is_category_empty
                and existing_category and existing_category.lower() != 'other'):
            continue

        note = normalize_string(df.loc[i, cts.NOTE_COLUMN]) if cts.NOTE_COLUMN in df.columns else ''
        category_assigned = False

        for key, categories in categories_dictionary.items():
            if key in note:
                assign_category(categories, df, i)
                category_assigned = True
                break

        newly_added_category = find_existing_category(df, i)
        is_category_still_empty = (pd.isna(newly_added_category)
                                   or newly_added_category in (None, 'nan', '')
                                   or newly_added_category.strip() == '')

        if not category_assigned and (not update_existing_categories or is_category_still_empty):
            df.loc[i, cts.CATEGORIES_COLUMN] = 'Other'

    logger.info("Updating categories finished.")


def assign_category(categories, df, row):
    assigned_category = categories[0].lower()
    assigned_category = assigned_category[0].upper() + assigned_category[1:]
    df.loc[row, cts.CATEGORIES_COLUMN] = assigned_category


def find_existing_category(df, row):
    if cts.CATEGORIES_COLUMN not in df.columns:
        return None
    return str(df.loc[row, cts.CATEGORIES_COLUMN]).strip().lower()


def initialize_labels_column(df):
    if cts.LABELS_COLUMN not in df.columns:
        df[cts.LABELS_COLUMN] = pd.Series(dtype='object')
    elif df[cts.LABELS_COLUMN].dtype != 'object':
        df[cts.LABELS_COLUMN] = df[cts.LABELS_COLUMN].astype('object')


def update_labels(df, dictionary, first_row, last_row, update_existing_labels=False):
    logger.info("Updating labels...")
    initialize_labels_column(df)

    for i in range(first_row - 1, min(last_row, len(df))):
        note = normalize_string(df.loc[i, cts.NOTE_COLUMN])
        existing_labels = set()
        first_update = True
        labels = extract_existing_labels(df, existing_labels, i)

        for key, labels_list in dictionary.items():
            normalized_key = normalize_string(key)
            if normalized_key in note:
                first_update = add_label_if_new(
                    existing_labels, labels, labels_list, update_existing_labels, first_update)

        joined_labels = cts.LABELS_DELIMITER.join(labels)
        df.loc[i, cts.LABELS_COLUMN] = joined_labels if joined_labels else ''

    logger.info("Updating labels finished.")


def extract_existing_labels(df, existing_labels, row_number):
    if pd.notna(df.loc[row_number, cts.LABELS_COLUMN]):
        labels = df.loc[row_number, cts.LABELS_COLUMN].split(cts.LABELS_DELIMITER)
        existing_labels.update(normalize_string(label) for label in labels if label)
    else:
        labels = []
    return labels


def add_label_if_new(existing_labels, labels, labels_list, update_existing_labels, first_update):
    """Returns the (possibly toggled) first_update flag — booleans are pass-by-value in Python."""
    for value in labels_list:
        normalized_value = normalize_string(value)
        if normalized_value in existing_labels:
            continue
        if update_existing_labels and first_update:
            labels.clear()
            existing_labels.clear()
            first_update = False
        labels.append(value)
        existing_labels.add(normalized_value)
    return first_update


def replace_multiple_whitespaces(df):
    for column in df.columns:
        if is_string_dtype(df[column]):
            df[column] = df[column].apply(lambda x: ' '.join(x.split()) if isinstance(x, str) else x)
    return df


def sort_dataframe_by_date(df):
    if cts.DATE_COLUMN not in df.columns:
        logger.warning("Date column '%s' not found in DataFrame.", cts.DATE_COLUMN)
        return df
    df[cts.DATE_COLUMN] = pd.to_datetime(df[cts.DATE_COLUMN], dayfirst=True)
    df = df.sort_values(by=cts.DATE_COLUMN, ascending=False)
    df[cts.DATE_COLUMN] = df[cts.DATE_COLUMN].dt.strftime(cts.OUTPUT_DATE_FORMAT)
    return df


def convert_decimal_separator(df, column_name, dot_decimal_separator=True):
    if column_name not in df.columns:
        logger.warning("Column '%s' not found in DataFrame.", column_name)
        return
    df[column_name] = df[column_name].apply(
        lambda x: normalize_number_format(x, dot_decimal_separator) if isinstance(x, str) else x)


def decorate_transactions(first_row=1, last_row=None,
                          update_existing_categories=False, update_existing_labels=False,
                          dot_decimal_separator=True):
    logger.info("Starting processing...")
    try:
        first_row = max(int(first_row), 1)

        categories_dictionary_path = user_directory_path(
            os.path.join(cts.DICTIONARY_DIRECTORY_PATH, cts.CATEGORIES_DICTIONARY_NAME))
        labels_dictionary_path = user_directory_path(
            os.path.join(cts.DICTIONARY_DIRECTORY_PATH, cts.LABELS_DICTIONARY_NAME))
        csv_path = user_directory_path(
            os.path.join(cts.CSV_FILE_DIRECTORY_PATH, cts.TRANSACTION_CSV_NAME))
        backup_dir = user_directory_path(cts.FILE_BACKUP_DIRECTORY_PATH)

        create_backup(csv_path, backup_dir)
        categories_dictionary = load_dictionary(categories_dictionary_path)
        labels_dictionary = load_dictionary(labels_dictionary_path)

        df = pd.read_csv(csv_path, delimiter=cts.CSV_DELIMITER)
        df = replace_multiple_whitespaces(df)

        if last_row is None or last_row > len(df):
            last_row = len(df)

        update_categories(df, categories_dictionary, first_row, last_row, update_existing_categories)
        update_labels(df, labels_dictionary, first_row, last_row, update_existing_labels)
        df = sort_dataframe_by_date(df)
        convert_decimal_separator(df, cts.AMOUNT_COLUMN, dot_decimal_separator)

        df.to_csv(csv_path, sep=cts.CSV_DELIMITER, index=False)
        logger.info("Processing finished.")
        return True, cts.COMPLETED_SUCCESSFULLY_MESSAGE

    except (pd.errors.ParserError, pd.errors.EmptyDataError) as e:
        logger.error("%s %s", cts.ERROR_PARSING_CSV, e)
        traceback.print_exc()
        return False, f"{cts.ERROR_PARSING_CSV} {e}"
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError, KeyError) as e:
        logger.error("%s %s", cts.ERROR_PARSING_CSV, e)
        traceback.print_exc()
        return False, f"{cts.ERROR_PARSING_CSV} {e}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    decorate_transactions()
