import json
import os
import shutil
import traceback
from datetime import datetime

import pandas as pd

import src.config.constants as cts
from src.utils.utils import user_directory_path


def normalize_string(s):
    if pd.isnull(s):
        return ''
    if not isinstance(s, str):
        s = str(s)
    s = s.strip()
    replacements = cts.CHARACTERS_NORMALIZATION_MAP
    for original, replacement in replacements.items():
        s = s.replace(original, replacement)
    return ' '.join(s.split()).lower()


def create_backup(original_file_path, backup_dir):
    print("Creating backup of CSV file..")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    timestamp = datetime.now().strftime(cts.BACKUP_TIMESTAMP_FORMAT)
    backup_file_path = os.path.join(backup_dir, f"{os.path.basename(original_file_path)}_{timestamp}.csv")
    shutil.copy(original_file_path, backup_file_path)


def load_dictionary(dictionary_path):
    print("Loading dictionary json..")
    with open(dictionary_path, 'r', encoding=('%s' % cts.DEFAULT_ENCODING)) as file:
        dictionary_data = json.load(file)

    # The labeling dictionary is in a human-readable format where each label maps to a list of keywords.
    # For efficient algorithm processing, keys and values need to be swapped.
    inverted_dictionary = invert_dictionary(dictionary_data)

    print("Normalize dictionary keys to lowercase")
    normalized_dictionary = {normalize_string(key): value for key, value in inverted_dictionary.items()}

    return normalized_dictionary


def invert_dictionary(dictionary_data):
    inverted_dictionary = {}
    for label, keys in dictionary_data.items():
        for key in keys:
            normalized_key = normalize_string(key)
            if normalized_key not in inverted_dictionary:
                inverted_dictionary[normalized_key] = []
            normalized_label = normalize_string(label)
            if normalized_label not in inverted_dictionary[normalized_key]:
                inverted_dictionary[normalized_key].append(normalized_label)
    return inverted_dictionary


def update_categories(df, categories_dictionary, first_row, last_row, update_existing_categories=False):
    print("Updating categories...")

    for i in range(first_row - 1, min(last_row, len(df))):
        existing_category = find_existing_category(df, i)
        is_category_empty = pd.isna(existing_category) or existing_category in [None, 'nan', '']

        if (not update_existing_categories and not is_category_empty
                and existing_category and existing_category.lower() != 'other'):

            print("Skip this line")
            continue

        note = normalize_string(df.loc[i, cts.NOTE_COLUMN]) if cts.NOTE_COLUMN in df.columns else ''
        category_assigned = False

        for key, categories in categories_dictionary.items():
            if key in note:
                assign_category(categories, df, i)
                category_assigned = True
                break

        if not category_assigned and not update_existing_categories:
            df.loc[i, cts.CATEGORIES_COLUMN] = 'Other'

    print("Updating categories finished.")


def assign_category(categories, df, row):
    assigned_category = categories[0]
    # Capitalize only the first letter of the first word
    assigned_category = assigned_category.lower()
    assigned_category = assigned_category[0].upper() + assigned_category[1:]
    df.loc[row, cts.CATEGORIES_COLUMN] = assigned_category  # Assign the first matched category


def find_existing_category(df, row):
    return str(df.loc[row, cts.CATEGORIES_COLUMN]).strip().lower() if cts.CATEGORIES_COLUMN in df.columns else None


def update_labels(df, dictionary, first_row, last_row, update_existing_labels=False):
    print("Processing labels if the '%s' column is not NaN" % cts.LABELS_COLUMN)
    for i in range(first_row - 1, min(last_row, len(df))):
        note = normalize_string(df.loc[i, ('%s' % cts.NOTE_COLUMN)])
        existing_labels = set()

        first_update = True
        labels = extract_existing_labels(df, existing_labels, i)

        for key, labels_list in dictionary.items():
            # Normalize the key for case-insensitive comparison
            normalized_key = normalize_string(key)
            if normalized_key in note:
                add_label_if_new(existing_labels, labels, labels_list, update_existing_labels, first_update)

        # Joining the labels with a CSV_DELIMITER to save back to CSV
        df.loc[i, cts.LABELS_COLUMN] = cts.LABELS_DELIMITER.join(labels)

    print("Updating labels finished.")


def extract_existing_labels(df, existing_labels, row_number):
    if pd.notna(df.loc[row_number, ('%s' % cts.LABELS_COLUMN)]):
        labels = df.loc[row_number, cts.LABELS_COLUMN].split(cts.CSV_DELIMITER)
        # Normalize labels for comparison and add to the set
        existing_labels.update(normalize_string(label) for label in labels if label)
    else:
        labels = []
    return labels


def add_label_if_new(existing_labels, labels, labels_list, update_existing_labels, first_update):
    for value in labels_list:
        normalized_value = normalize_string(value)
        # Check if the value, in a normalized form, is not already in labels
        if normalized_value not in existing_labels:
            if update_existing_labels and first_update:
                labels.clear()
                existing_labels.clear()
                first_update = False
            labels.append(value)  # Append the original case value
            existing_labels.add(normalized_value)  # Add to set to prevent duplicates


def replace_multiple_whitespaces(df):
    for column in df.columns:
        if df[column].dtype == object:  # Check if the column is of a string type
            df[column] = df[column].apply(lambda x: ' '.join(x.split()) if isinstance(x, str) else x)
    return df


# by default, last_row is set to '0' to process the whole file
def process_transactions(first_row=1, last_row=None, update_existing_categories=False, update_existing_labels=False):
    print("Starting processing...")
    try:
        # If first_row is less than 1, set it to 1
        first_row = max(int(first_row), 1)

        # Define paths relative to the script file
        categories_dictionary_path = user_directory_path(
            f'{cts.DICTIONARY_DIRECTORY_PATH}/{cts.CATEGORIES_DICTIONARY_NAME}')
        labels_dictionary_path = user_directory_path(f'{cts.DICTIONARY_DIRECTORY_PATH}/{cts.LABELS_DICTIONARY_NAME}')

        csv_path = user_directory_path(f'{cts.CSV_FILE_DIRECTORY_PATH}/{cts.TRANSACTION_CSV_NAME}')
        backup_dir = user_directory_path(f'{cts.FILE_BACKUP_DIRECTORY_PATH}/')

        create_backup(csv_path, backup_dir)
        categories_dictionary = load_dictionary(categories_dictionary_path)
        labels_dictionary = load_dictionary(labels_dictionary_path)

        try:
            df = pd.read_csv(csv_path, delimiter=cts.CSV_DELIMITER)
            df = replace_multiple_whitespaces(df)

            if last_row is None or last_row > len(df):
                last_row = len(df)

            update_categories(df, categories_dictionary, first_row, last_row, update_existing_categories)
            update_labels(df, labels_dictionary, first_row, last_row, update_existing_labels)
            df.to_csv(csv_path, sep=('%s' % cts.CSV_DELIMITER), index=False)

        except pd.errors.ParserError as e:
            print(f"{cts.ERROR_PARSING_CSV} {e}")
            traceback.print_exc()
            return False, f"{cts.ERROR_PARSING_CSV} {e}"

        print("Processing finished.")
        return True, ("%s" % cts.COMPLETED_SUCCESSFULLY_MESSAGE)

    except Exception as e:
        print(f"{cts.ERROR_PARSING_CSV} {e}")
        traceback.print_exc()
        return False, f"{cts.ERROR_PARSING_CSV} {e}"


if __name__ == "__main__":
    process_transactions()
