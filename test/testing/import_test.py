import os
from unittest.mock import patch  # adjust import as necessary

import pandas as pd
import pytest

import config.constants as cts
from processor.transactions_importer import process_imported_csv

# for printing full csv:
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


def read_csv_for_test(path):
    return pd.read_csv(path, delimiter=';', encoding=cts.DEFAULT_ENCODING)


@pytest.mark.parametrize("input_csv,expected_csv,delimiter,dot_decimal_separator", [
    # ('./import/importerTestData.csv', './import/expected/expected-importerTestData.csv', ";", True),
    # ('./import/importerTestData.csv', './import/expected/expected-testData-processing-comma-decimal-separator.csv',
    #  ";", False),
    # ('./import/testData-comma-with-artefacts-importing.csv',
    #  './import/expected/expected-testData-comma-with-artefacts-importing.csv', ',', True),
    ('./import/testData-semicolon-with-artefacts-importing.csv',
     './import/expected/expected-testData-semicolon-with-artefacts-importing.csv', ';', True)
])
def test_process_imported_csv(input_csv, expected_csv, delimiter, dot_decimal_separator):
    base_path = os.path.dirname(__file__)
    test_input_path = os.path.abspath(os.path.join(base_path, input_csv))
    expected_output_path = os.path.abspath(os.path.join(base_path, expected_csv))
    test_output_path = os.path.abspath(os.path.join(base_path, './import/test.csv'))

    # remove old test data if exists for clear run
    remove_test_file(test_output_path)

    import_dictionary = os.path.abspath(os.path.join(base_path, '../../dictionary/import-dictionary.json'))
    ignore_dictionary = os.path.abspath(os.path.join(base_path, '../../dictionary/ignore-dictionary.json'))

    # Mock `user_directory_path` to return the path for test output instead of the normal output
    with patch('processor.transactions_importer.user_directory_path') as mock_user_directory_path:
        def side_effect(arg):
            if arg.endswith(cts.TRANSACTION_CSV_NAME):
                return test_output_path
            elif arg.endswith(cts.IGNORE_DICTIONARY_NAME):
                return ignore_dictionary
            elif arg.endswith(cts.IMPORT_DICTIONARY_NAME):
                return import_dictionary
            return arg

        mock_user_directory_path.side_effect = side_effect

        try:
            # Run the processing function
            process_imported_csv(test_input_path, delimiter=delimiter,
                                 dot_decimal_separator=dot_decimal_separator)

            # Read the processed file and the expected file
            processed_df = read_csv_for_test(test_output_path)
            # print(processed_df)
            expected_df = read_csv_for_test(expected_output_path)

            # Assert that the two dataframes are the same
            pd.testing.assert_frame_equal(processed_df, expected_df)

        finally:
            remove_test_file(test_output_path)
            print("Test completed.")


def remove_test_file(test_output_path):
    if os.path.exists(test_output_path):
        os.remove(test_output_path)
        print("Test output file removed.")
    else:
        print("No test output file found to remove.")
