"""Provides functionality for running and logging pytest results."""

import argparse
import io
import sys
from unittest.mock import MagicMock
import pytest

from klingon_tools.log_msg import log_message, set_default_style
from klingon_tools.log_tools import LogTools


# pylint: disable=R0903
class KTestLogPlugin:
    """A pytest plugin for logging test results."""

    def __init__(self, results):
        """Initialize the KTestLogPlugin.

        Args:
            results: A list to store test results.
        """
        self.log_message = log_message
        self.results = results

    def pytest_runtest_logreport(self, report):
        """Log the result of each test run.

        Args:
            report: A pytest report object containing test information.
        """
        if report.when == "call" or (
            report.when == "setup" and report.outcome == "failed"
        ):
            test_name = report.nodeid

            if report.passed:
                self._log_passed_test(test_name)
            elif report.failed:
                self._log_failed_test(test_name, report)
            elif report.skipped:
                if "no-llm" in report.keywords:
                    self.log_message.info(
                        message=f"{test_name} (skipped due to --no-llm)",
                        status="SKIPPED 🦘"
                    )
                    self.results.append((test_name, "skipped"))
                else:
                    self._log_skipped_test(test_name)

    def _log_passed_test(self, test_name):
        """Log a passed test."""
        self.log_message.info(message=f"{test_name}", status="✅")
        self.results.append((test_name, "passed"))

    def _log_failed_test(self, test_name, report):
        """Log a failed test."""
        if "optional" in report.keywords:
            self.log_message.warning(
                message=f"{test_name} (optional)", status="👾"
            )
            self.results.append((test_name, "optional-failed"))
        else:
            self.log_message.error(message=f"{test_name}", status="❌")
            self.results.append((test_name, "failed"))

        self._log_exception_info(test_name, report)

    def _log_skipped_test(self, test_name):
        """Log a skipped test."""
        self.log_message.info(
            message=f"{test_name}",
            status="SKIPPED 🦘"
        )
        self.results.append((test_name, "skipped"))

    def _log_exception_info(self, test_name, report):
        """Log exception information for a failed test."""
        self.log_message.error(
            message=f"Exception info for {test_name}:",
            status="",
            style="none"
        )
        print(report.longrepr)

        if isinstance(
                self.log_message.logger,
                MagicMock
        ) or self.log_message.logger.getEffectiveLevel() <= 10:
            self._log_debug_info(test_name, report)

    def _log_debug_info(self, test_name, report):
        """Log additional debug information for a failed test."""
        self.log_message.debug(
            message=f"Additional debug info for {test_name}:",
            status="",
            style="none"
        )
        print(report.caplog)
        if hasattr(report, 'captured_stdout'):
            print(report.captured_stdout)
        if hasattr(report, 'captured_stderr'):
            print(report.captured_stderr)


def ktest(
    loglevel="INFO",
    as_entrypoint=False,
    suppress_output=True,
    no_llm=False
):
    """Run pytest and display the results with the specified log level."""
    set_default_style("pre-commit")
    LogTools(debug=False).set_log_level(loglevel.upper())

    results = []
    plugin = KTestLogPlugin(results)

    _setup_output_capture(suppress_output, loglevel)

    pytest_args = _prepare_pytest_args(no_llm)
    exit_code = pytest.main(pytest_args, plugins=[plugin])

    _restore_output(suppress_output)

    results_obj = [
        {"name": test_name, "outcome": outcome}
        for test_name, outcome in results
    ]

    return exit_code if as_entrypoint else results_obj


def _setup_output_capture(suppress_output, loglevel):
    """Set up output capture if suppression is enabled."""
    if suppress_output and loglevel.upper() != "DEBUG":
        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.stderr = captured_output
        return captured_output
    return None


def _prepare_pytest_args(no_llm):
    """Prepare the arguments for pytest."""
    pytest_args = [
        "tests",
        "--tb=short",
        "--import-mode=importlib",
        "-v",
        "-q",
        "--disable-warnings",
    ]
    if no_llm:
        pytest_args.append("--no-llm")
    return pytest_args


def _restore_output(suppress_output, captured_output=None):
    """Restore stdout and stderr if output was suppressed."""
    if suppress_output:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def ktest_entrypoint(args=None):
    """Entrypoint for running ktest as a script."""
    parser = argparse.ArgumentParser(description="Run ktest")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM tests")
    parser.add_argument("--loglevel", default="INFO", help="Set the log level")
    parsed_args = parser.parse_args(args)

    return ktest(
        loglevel=parsed_args.loglevel,
        as_entrypoint=True,
        no_llm=parsed_args.no_llm
    )


if __name__ == "__main__":
    sys.exit(ktest_entrypoint())
