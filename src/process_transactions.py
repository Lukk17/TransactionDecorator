import json
import os
import shutil
from datetime import datetime

import pandas as pd


def normalize_string(s):
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ż': 'z', 'ź': 'z'
    }
    for original, replacement in replacements.items():
        s = s.replace(original, replacement)
    return s.lower()


def create_backup(original_file_path, backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file_path = os.path.join(backup_dir, f"{os.path.basename(original_file_path)}_{timestamp}.csv")
    shutil.copy(original_file_path, backup_file_path)


def load_dictionary(dictionary_path):
    with open(dictionary_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def update_labels(df, dictionary, first_row, last_row):
    for i in range(first_row - 1, last_row):
        note = normalize_string(df.loc[i, 'Note'])
        labels = df.loc[i, 'Labels'].split(',') if pd.notna(df.loc[i, 'Labels']) else []
        for key, value in dictionary.items():
            if key in note and value not in labels:
                labels.append(value)
        df.loc[i, 'Labels'] = ','.join(labels)


def process_transactions(first_row=2, last_row=0):
    # Define paths relative to the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dictionary_path = os.path.join(script_dir, '..', 'dictionary', 'dictionary.json')
    csv_path = os.path.join(script_dir, '..', 'csv', 'allTransactions.csv')
    backup_dir = os.path.join(script_dir, '..', 'backup')

    create_backup(csv_path, backup_dir)
    dictionary = load_dictionary(dictionary_path)

    df = pd.read_csv(csv_path, delimiter=';')
    last_row = last_row if last_row is not None else len(df) + 1  # Process till the end if not specified

    update_labels(df, dictionary, first_row, last_row)
    df.to_csv(csv_path, sep=';', index=False)


if __name__ == "__main__":
    process_transactions()
