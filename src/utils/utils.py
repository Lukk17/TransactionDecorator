import os
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
