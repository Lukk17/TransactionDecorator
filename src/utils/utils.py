import os
import re
import sys

import config.constants as cts


# Paths for internal app files like icons
def resource_path(relative_path):
    """ Get an absolute path to resource, works for dev and for PyInstaller.
        Consistently navigates to the parent directory of 'src' before appending the relative path. """

    if getattr(sys, 'frozen', False):
        if is_snap():
            base_path = get_snap_base_path()

        else:
            print("[resource_path] running on Windows")
            # In a bundled app, get the directory of the .exe file
            base_path = os.path.dirname(sys.executable)

    elif os.path.exists('../.idea'):
        print("[resource_path] started by IDE")
        script_dir = os.path.abspath(__file__)
        utils_dir = os.path.dirname(script_dir)
        src_dir = os.path.dirname(utils_dir)
        base_path = os.path.dirname(src_dir)
        # Specific adjustment for Linux deployment via .deb package

    elif sys.platform == "linux":
        script_path = os.path.dirname(__file__)
        if is_snap():
            base_path = get_snap_base_path()
        elif os.path.exists(os.path.join(os.path.abspath(script_path), '../../.idea')):
            base_path = os.path.join(os.path.abspath(script_path), '../../')
            print("[resource_path] IDE linux dev base path: ", base_path)
        else:
            print("[resource_path] running in linux")
            base_path = '/usr/lib/transaction-decorator'

    elif is_snap():
        base_path = get_snap_base_path()

    else:
        print("[resource_path] running on unrecognized platform")
        # Determine the base directory (parent of 'src')
        script_dir = os.path.abspath(__file__)
        utils_dir = os.path.dirname(script_dir)
        src_dir = os.path.dirname(utils_dir)  # Navigate to 'src'
        base_path = os.path.dirname(src_dir)  # Navigate to the parent of 'src'

    result = os.path.join(base_path, relative_path)
    print("[resource_path] result: ", result)

    return result


# Paths for external app files, specific to user like backup, csv, dictionary
def user_directory_path(relative_path):
    base_path = os.path.dirname(__file__)
    # If the application is run as a bundled executable (e.g., using PyInstaller)
    if getattr(sys, 'frozen', False):
        # snap can set frozen attribute
        if is_snap():
            return get_snap_user_directory_path(relative_path)

        elif sys.platform == "win32":
            # For Windows, construct the path within the AppData directory
            directory_path = os.path.join(os.environ['APPDATA'], cts.APP_NAME, relative_path)

            print("[user_directory_path] win32 path: ", directory_path)
            return directory_path

        else:
            # For other platforms, use the resource_path to find the directory
            directory_path = resource_path(relative_path)

            # Ensure the directory exists
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            print("[user_directory_path] unrecognized platform path: ", directory_path)
            return directory_path

    elif sys.platform == "linux":
        # snap can have sys.platform = "linux"
        if is_snap():
            return get_snap_user_directory_path(relative_path)

        elif os.path.exists(os.path.join(os.path.abspath(base_path), '../../.idea')):
            directory_path = os.path.join(os.path.abspath(base_path), '../../')
            # directory_path = resource_path(relative_path)
            print("[user_directory_path] IDE linux dev path: ", directory_path)
            return os.path.join(directory_path, relative_path)

        # For Linux, place user-specific data in the home directory
        directory_path = os.path.join('/usr/share', 'transaction-decorator', relative_path)

        print("[user_directory_path] linux path: ", directory_path)
        return directory_path

    if is_snap():
        return get_snap_user_directory_path(relative_path)

    # If run for development from IDE mostly on Windows
    else:
        directory_path = resource_path(relative_path)

        print("[user_directory_path] IDE dev path: ", directory_path)
        return directory_path


def get_snap_base_path():
    print("[resource_path] running as SNAP")
    snap_root = os.environ.get('SNAP', '')
    base_path = os.path.join(snap_root, 'usr', 'share', os.environ.get('TRANSACTION_DECORATOR_SNAP_NAME', ''))
    return base_path


def get_snap_user_directory_path(relative_path):
    snap_user_data_path = os.environ.get('SNAP_USER_DATA', '')
    directory_path = os.path.join(snap_user_data_path, relative_path)

    print("[user_directory_path] SNAP path: ", directory_path)
    return directory_path


def is_snap():
    return ('TRANSACTION_DECORATOR_SNAP_NAME' in os.environ
            and os.environ.get('SNAP_NAME', '') == os.environ.get('TRANSACTION_DECORATOR_SNAP_NAME', ''))


def change_to_user_directory():
    home_directory = os.path.expanduser('~')
    try:
        os.chdir(home_directory)
    except Exception as e:
        print(f"Failed to change directory: {e}")


def normalize_number_format(s, dot_decimal_separator=True):
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
        if dot_decimal_separator:
            # Convert from standard to dot format
            return s.replace('.', '').replace(',', '.')
        else:
            # Already in Euro format, remove dots if needed
            return s.replace('.', '')

    elif eng_format.match(s):
        if dot_decimal_separator:
            # Already in English format, remove commas if needed
            return s.replace(',', '')
        else:
            # Convert from English format to standard format with comma as decimal separator
            return s.replace(',', '').replace('.', ',')
    else:
        print(f"Warning: weird format of number: '{s}' - trying to convert anyway..")
        if dot_decimal_separator:
            # Convert to English format
            return s.replace(',', '.')
        else:
            # Convert to standard format with comma as decimal separator
            return s.replace('.', ',')


def create_original_csv(file_path):
    print("create_original_csv file_path: " + file_path)
    headers = cts.CSV_HEADERS
    with open(file_path, 'w', encoding=cts.DEFAULT_ENCODING) as f:
        f.write(headers)
