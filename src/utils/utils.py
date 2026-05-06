import logging
import os
import re
import sys
from enum import Enum

import config.constants as cts

logger = logging.getLogger(__name__)


class Environment(Enum):
    SNAP = "snap"
    FROZEN_WINDOWS = "frozen_windows"
    FROZEN_OTHER = "frozen_other"
    IDE = "ide"
    LINUX_PACKAGE = "linux_package"
    UNKNOWN = "unknown"


def is_snap():
    return ('TRANSACTION_DECORATOR_SNAP_NAME' in os.environ
            and os.environ.get('SNAP_NAME', '') == os.environ.get('TRANSACTION_DECORATOR_SNAP_NAME', ''))


def _is_ide_layout(start_path):
    return os.path.exists(os.path.join(os.path.abspath(start_path), '.idea'))


def _detect_environment():
    if is_snap():
        return Environment.SNAP
    if getattr(sys, 'frozen', False):
        return Environment.FROZEN_WINDOWS if sys.platform == "win32" else Environment.FROZEN_OTHER
    repo_root_from_utils = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if _is_ide_layout(repo_root_from_utils) or _is_ide_layout(os.path.abspath('..')):
        return Environment.IDE
    if sys.platform == "linux":
        return Environment.LINUX_PACKAGE
    return Environment.UNKNOWN


def _repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def _snap_base_path():
    snap_root = os.environ.get('SNAP', '')
    return os.path.join(snap_root, 'usr', 'share', os.environ.get('TRANSACTION_DECORATOR_SNAP_NAME', ''))


def _snap_user_data_path(relative_path):
    return os.path.join(os.environ.get('SNAP_USER_DATA', ''), relative_path)


# Paths for internal app files like icons (read-only, app-bundled)
def resource_path(relative_path):
    """Return absolute path to a bundled resource. Works in dev, frozen, and snap."""
    env = _detect_environment()
    if env == Environment.SNAP:
        base_path = _snap_base_path()
    elif env == Environment.FROZEN_WINDOWS:
        base_path = os.path.dirname(sys.executable)
    elif env == Environment.IDE:
        base_path = _repo_root()
    elif env == Environment.LINUX_PACKAGE:
        base_path = '/usr/lib/transaction-decorator'
    else:
        # FROZEN_OTHER and UNKNOWN: best-effort dev-style layout
        base_path = _repo_root()

    result = os.path.join(base_path, relative_path)
    logger.debug("[resource_path] env=%s result=%s", env.value, result)
    return result


# Paths for user-writable data: backup, csv, dictionary
def user_directory_path(relative_path):
    env = _detect_environment()
    if env == Environment.SNAP:
        return _snap_user_data_path(relative_path)
    if env == Environment.FROZEN_WINDOWS:
        directory_path = os.path.join(os.environ['APPDATA'], cts.APP_NAME, relative_path)
        logger.debug("[user_directory_path] win32 path=%s", directory_path)
        return directory_path
    if env == Environment.FROZEN_OTHER:
        directory_path = resource_path(relative_path)
        os.makedirs(directory_path, exist_ok=True)
        return directory_path
    if env == Environment.IDE:
        return os.path.join(_repo_root(), relative_path)
    if env == Environment.LINUX_PACKAGE:
        return os.path.join('/usr/share', 'transaction-decorator', relative_path)
    return resource_path(relative_path)


def change_to_user_directory():
    home_directory = os.path.expanduser('~')
    try:
        os.chdir(home_directory)
    except OSError as e:
        logger.warning("Failed to change directory: %s", e)


# Pattern matchers for decimal-separator detection.
# These are intentionally permissive (groups treated as thousand separators) to
# preserve the historical interpretation expected by integration fixtures.
# See ADR-0006 for the rationale and known ambiguities.
_STANDARD_FORMAT = re.compile(r'^-?\d{1,3}(?:\.\d{3})*,?\d*$')
_ENGLISH_FORMAT = re.compile(r'^-?\d{1,3}(?:,\d{3})*\.?\d*$')


def normalize_number_format(s, dot_decimal_separator=True):
    """Normalize a numeric string to dot- or comma-decimal form."""
    if _STANDARD_FORMAT.match(s):
        if dot_decimal_separator:
            return s.replace('.', '').replace(',', '.')
        return s.replace('.', '')
    if _ENGLISH_FORMAT.match(s):
        if dot_decimal_separator:
            return s.replace(',', '')
        return s.replace(',', '').replace('.', ',')

    logger.warning("Unrecognized number format '%s' - applying best-effort conversion", s)
    if dot_decimal_separator:
        return s.replace(',', '.')
    return s.replace('.', ',')


def create_original_csv(file_path):
    logger.info("Creating new CSV at %s", file_path)
    with open(file_path, 'w', encoding=cts.DEFAULT_ENCODING) as f:
        f.write(cts.CSV_HEADERS)
