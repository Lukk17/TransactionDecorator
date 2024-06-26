import os
import shutil
from unittest.mock import patch  # adjust import as necessary

import pandas as pd
import pytest

import config.constants as cts
from processor.transactions_decorator import decorate_transactions

# for printing full csv:
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


def read_csv_for_test(path):
    return pd.read_csv(path, delimiter=';', encoding=cts.DEFAULT_ENCODING)


@pytest.mark.parametrize(
    "expected_csv, first_row, last_row, update_existing_categories, update_existing_labels,dot_decimal_separator", [
        ('./decorator/expected/correctly-noforce-english-decimal-processed.csv', 1, None, False, False, True),
        ('./decorator/expected/correctly-force-categories-processed.csv', 1, None, True, False, True),
        ('./decorator/expected/correctly-force-labels-processed.csv', 1, None, False, True, True),
        ('./decorator/expected/correctly-force-all-processed.csv', 1, None, True, True, True),
        ('./decorator/expected/correctly-force-all-processed-latest-skipped.csv', 5, None, True, True, True),
        ('./decorator/expected/correctly-force-all-processed-only-latest-changed.csv', 1, 5, True, True, True),
        ('./decorator/expected/correctly-force-all-processed-middle-changed.csv', 3, 7, True, True, True),
        ('./decorator/expected/correctly-force-all-processed-only-latest-changed.csv', 1, 5, True, True, True),
        ('./decorator/expected/correctly-noforce-standard-decimal-processed.csv', 1, None, False, False, False),
    ])
def test_process_imported_csv(expected_csv, first_row, last_row, update_existing_categories, update_existing_labels,
                              dot_decimal_separator):
    base_path = os.path.dirname(__file__)
    expected_output_path = os.path.abspath(os.path.join(base_path, expected_csv))

    if (first_row > 1) or last_row is not None:
        original_csv = os.path.abspath(os.path.join(base_path, './decorator/decoratorTestData-chronological.csv'))
    elif dot_decimal_separator:
        original_csv = os.path.abspath(os.path.join(base_path, './decorator/decoratorTestData.csv'))
    else:
        original_csv = os.path.abspath(
            os.path.join(base_path, './decorator/decoratorTestData-commaDecimalSeparator.csv'))

    tested_csv = os.path.abspath(os.path.join(base_path, './decorator/testCopy_decoratorTestData.csv'))

    # remove old test data if exists for clear run
    remove_test_file(tested_csv)

    shutil.copyfile(original_csv, tested_csv)

    categories_dictionary = os.path.abspath(os.path.join(base_path, '../../dictionary/categories-dictionary.json'))
    labels_dictionary = os.path.abspath(os.path.join(base_path, '../../dictionary/labels-dictionary.json'))

    # Mock `user_directory_path` to return the path for test output instead of the normal output
    with patch('processor.transactions_decorator.user_directory_path') as mock_user_directory_path:
        def side_effect(arg):
            if arg.endswith(cts.TRANSACTION_CSV_NAME):
                return tested_csv
            elif arg.endswith(cts.CATEGORIES_DICTIONARY_NAME):
                return categories_dictionary
            elif arg.endswith(cts.LABELS_DICTIONARY_NAME):
                return labels_dictionary
            return arg

        mock_user_directory_path.side_effect = side_effect

        try:
            # Run the processing function
            decorate_transactions(first_row=first_row, last_row=last_row,
                                  update_existing_categories=update_existing_categories,
                                  update_existing_labels=update_existing_labels,
                                  dot_decimal_separator=dot_decimal_separator)

            # Read the processed file and the expected file
            processed_df = read_csv_for_test(tested_csv)
            # print(processed_df)
            expected_df = read_csv_for_test(expected_output_path)

            # Assert that the two dataframes are the same
            pd.testing.assert_frame_equal(processed_df, expected_df)

        finally:
            remove_test_file(tested_csv)
            print("Test completed.")


def remove_test_file(tested_csv):
    if os.path.exists(tested_csv):
        os.remove(tested_csv)
        print("Test output file removed.")
    else:
        print("No test output file found to remove.")
