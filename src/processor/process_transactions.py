import json
import os
import shutil
from datetime import datetime

import pandas as pd

from src.config.constants import *
from src.utils.utils import resource_path


def normalize_string(s):
    if pd.isnull(s):
        return ''
    if not isinstance(s, str):
        s = str(s)
    s = s.strip()
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ż': 'z', 'ź': 'z'
    }
    for original, replacement in replacements.items():
        s = s.replace(original, replacement)
    return ' '.join(s.split()).lower()


def create_backup(original_file_path, backup_dir):
    print("Creating backup of CSV file..")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file_path = os.path.join(backup_dir, f"{os.path.basename(original_file_path)}_{timestamp}.csv")
    shutil.copy(original_file_path, backup_file_path)


def load_dictionary(dictionary_path):
    print("Loading dictionary json..")
    with open(dictionary_path, 'r', encoding='utf-8') as file:
        dictionary_data = json.load(file)
    print("Normalize dictionary keys to lowercase")
    normalized_dictionary = {normalize_string(key): value for key, value in dictionary_data.items()}
    return normalized_dictionary


def update_labels(df, dictionary, first_row, last_row):
    print("ProcessING labels if the '%s' column is not NaN" % LABELS_COLUMN)
    for i in range(first_row - 1, min(last_row, len(df))):
        note = normalize_string(df.loc[i, ('%s' % NOTE_COLUMN)])

        if pd.notna(df.loc[i, ('%s' % LABELS_COLUMN)]):
            labels = df.loc[i, LABELS_COLUMN].split(CSV_DELIMITER)
            # Normalize labels for comparison but keep the original case for output
            normalized_labels = [normalize_string(label) for label in labels if label]
        else:
            labels = []
            normalized_labels = []

        for key, values in dictionary.items():
            # Normalize the key for case-insensitive comparison
            normalized_key = normalize_string(key)

            if normalized_key in note:
                for value in values.split(LABELS_DELIMITER):
                    # Check if the value, in a normalized form, is not already in labels
                    if normalize_string(value) not in normalized_labels:
                        labels.append(value)  # Append the original case value

        # Joining the labels with a CSV_DELIMITER to save back to CSV
        df.loc[i, LABELS_COLUMN] = ';'.join(labels)


# by default, last_row is set to '0' to process the whole file
def process_transactions(first_row=2, last_row=None):
    print("Starting processing...")
    # If first_row is less than 2, set it to 2
    first_row = max(int(first_row), 2)

    # Define paths relative to the script file
    dictionary_path = resource_path(f'{dictionary_directory_path}/dictionary.json')
    csv_path = resource_path(f'{csv_file_directory_path}/allTransactions.csv')
    backup_dir = resource_path(f'{file_backup_directory_path}/')

    create_backup(csv_path, backup_dir)
    dictionary = load_dictionary(dictionary_path)

    try:
        df = pd.read_csv(csv_path, delimiter=CSV_DELIMITER)
        if last_row is None or last_row > len(df):
            last_row = len(df)

        update_labels(df, dictionary, first_row, last_row)
        df.to_csv(csv_path, sep=('%s' % CSV_DELIMITER), index=False)

    except pd.errors.ParserError as e:
        print(f"Error parsing CSV file in line: {e}")
        return False, f"Error parsing CSV file in line: {e}"

    print("Processing finished.")
    return True, "Processing completed successfully."


if __name__ == "__main__":
    process_transactions()
