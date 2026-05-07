"""Coverage for ProcessingWorker — runs without QThread/QApplication.

Signal.emit synchronously invokes connected callables when there is no event loop,
so we can verify worker behavior by connecting a Python callable and inspecting
the captured args. This avoids needing pytest-qt as a dependency.
"""
import pytest

# Importing PySide6 requires a working install but no QApplication for QObject + Signal.
pytest.importorskip("PySide6")

from unittest.mock import patch

from gui import ProcessingWorker


class _SignalCapture:
    def __init__(self):
        self.calls = []

    def __call__(self, *args):
        self.calls.append(args)


def test_processing_worker_emits_decorate_result_on_success():
    capture = _SignalCapture()
    with patch("gui.decorate_transactions", return_value=(True, "OK")) as mock_dec:
        worker = ProcessingWorker(first_row=1, last_row=None,
                                  update_existing_categories=False,
                                  update_existing_labels=False,
                                  dot_decimal_separator=True)
        worker.finished.connect(capture)
        worker.run()

    mock_dec.assert_called_once_with(
        first_row=1, last_row=None,
        update_existing_categories=False,
        update_existing_labels=False,
        dot_decimal_separator=True)
    assert capture.calls == [(True, "OK")]


def test_processing_worker_emits_failure_on_decorate_returning_false():
    capture = _SignalCapture()
    with patch("gui.decorate_transactions", return_value=(False, "parse error")):
        worker = ProcessingWorker(first_row=1)
        worker.finished.connect(capture)
        worker.run()

    assert capture.calls == [(False, "parse error")]


def test_processing_worker_catches_exception_and_emits_failure():
    """If decorate_transactions raises, the worker must emit (False, str(exc)),
    not crash the GUI thread."""
    capture = _SignalCapture()
    with patch("gui.decorate_transactions", side_effect=RuntimeError("boom!")):
        worker = ProcessingWorker(first_row=1)
        worker.finished.connect(capture)
        worker.run()

    assert len(capture.calls) == 1
    is_success, message = capture.calls[0]
    assert is_success is False
    assert "boom!" in message


def test_processing_worker_passes_all_kwargs_to_decorate():
    capture = _SignalCapture()
    with patch("gui.decorate_transactions", return_value=(True, "")) as mock_dec:
        worker = ProcessingWorker(
            first_row=5, last_row=10,
            update_existing_categories=True,
            update_existing_labels=True,
            dot_decimal_separator=False)
        worker.finished.connect(capture)
        worker.run()

    mock_dec.assert_called_once_with(
        first_row=5, last_row=10,
        update_existing_categories=True,
        update_existing_labels=True,
        dot_decimal_separator=False)
