import os
import re
import sys

import src.config.constants as cts


# Paths for internal app files like icons
def resource_path(relative_path):
    """ Get an absolute path to resource, works for dev and for PyInstaller.
        Consistently navigates to the parent directory of 'src' before appending the relative path. """

    if getattr(sys, 'frozen', False):
        # In a bundled app, get the directory of the .exe file
        base_path = os.path.dirname(sys.executable)

    else:
        # Determine the base directory (parent of 'src')
        script_dir = os.path.abspath(__file__)
        utils_dir = os.path.dirname(script_dir)
        src_dir = os.path.dirname(utils_dir)  # Navigate to 'src'
        base_path = os.path.dirname(src_dir)  # Navigate to the parent of 'src'

    return os.path.join(base_path, relative_path)


# Paths for external app files, specific to user like backup, csv, dictionary
def user_directory_path(relative_path):
    # If the application is run as a bundled executable (e.g., using PyInstaller)
    if getattr(sys, 'frozen', False):
        # Determine the directory path based on the operating system
        if sys.platform == "win32":
            # For Windows, construct the path within the AppData directory
            directory_path = os.path.join(os.environ['APPDATA'], cts.APP_NAME, relative_path)

            # Ensure the directory exists
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            return directory_path

        elif sys.platform == "darwin":
            # For macOS, use the resource_path to find the directory - to be changed
            directory_path = resource_path(relative_path)

            # Ensure the directory exists
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            return directory_path

        else:
            # For Linux or other platforms, use the resource_path to find the directory - to be changed
            directory_path = resource_path(relative_path)

            # Ensure the directory exists
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            return directory_path

    # If run for development from IDE
    else:
        return resource_path(relative_path)


def normalize_number_format(s, english_decimal_separator=True):
    """
    Normalizes mixed number formats to a consistent format.

    Parameters:
    - s: The string representing the number to normalize.
    - english_decimal_separator: If True, normalizes to English format (dot as decimal separator).
                                 If False, retains or converts to a comma as the decimal separator.

    Returns:
    - The normalized number as a string.
    """
    # Pattern to identify standard format (e.g., 1.234,56)
    standard_format = re.compile(r'^-?\d{1,3}(?:\.\d{3})*,?\d*$')

    # Pattern to identify English format (e.g., 1,234.56)
    eng_format = re.compile(r'^-?\d{1,3}(?:,\d{3})*\.?\d*$')

    if standard_format.match(s):
        if english_decimal_separator:
            # Convert from standard to English format
            return s.replace('.', '').replace(',', '.')
        else:
            # Already in Euro format, remove dots if needed
            return s.replace('.', '')

    elif eng_format.match(s):
        if english_decimal_separator:
            # Already in English format, remove commas if needed
            return s.replace(',', '')
        else:
            # Convert from English format to standard format with comma as decimal separator
            return s.replace(',', '').replace('.', ',')
    else:
        print(f"Warning: weird format of number: '{s}' - trying to convert anyway..")
        if english_decimal_separator:
            # Convert to English format
            return s.replace(',', '.')
        else:
            # Convert to standard format with comma as decimal separator
            return s.replace('.', ',')
