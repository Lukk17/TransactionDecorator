import sys
import os


def resource_path(relative_path):
    """ Get an absolute path to resource, works for dev and for PyInstaller.
        Consistently navigates to the parent directory of 'src' before appending the relative path. """
    # Determine the base directory (parent of 'src')
    script_dir = os.path.abspath(__file__)
    utils_dir = os.path.dirname(script_dir)  # Navigate to 'src'
    src_dir = os.path.dirname(utils_dir)  # Navigate to 'src'
    base_dir = os.path.dirname(src_dir)    # Navigate to the parent of 'src'
    base_path = getattr(sys, '_MEIPASS', base_dir)

    return os.path.join(base_path, relative_path)
