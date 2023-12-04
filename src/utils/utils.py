import sys
import os


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
        base_path = os.path.dirname(src_dir)    # Navigate to the parent of 'src'

    return os.path.join(base_path, relative_path)
