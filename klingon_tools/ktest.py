from klingon_tools.log_msg import log_message, set_default_style, set_log_level


class TestLogPlugin:
    def __init__(self, log_message, results):
        self.log_message = log_message
        self.results = results

    def pytest_runtest_logreport(self, report):
        if report.when == "call" or (
            report.when == "setup" and report.outcome == "failed"
        ):
            test_name = report.nodeid

            if report.passed:
                self.log_message.info(message=f"{test_name}", status="✅")
                self.results.append((test_name, "passed"))

            elif report.failed:
                # Check if the test is optional and log as a warning
                if "optional" in report.keywords:
                    self.log_message.warning(
                        message=f"{test_name} (optional)", status="⚠️"
                    )
                    self.results.append((test_name, "optional-failed"))
                else:
                    self.log_message.error(message=f"{test_name}", status="❌")
                    self.results.append((test_name, "failed"))

                # Always print exception info for failed tests
                self.log_message.error(
                    message=f"Exception info for {test_name}:",
                    status="",
                    style=None
                )
                print(report.longrepr)

                # Print additional debug info if in debug mode
                if self.log_message.logger.getEffectiveLevel() <= 10:
                    self.log_message.debug(
                        message=f"Additional debug info for {test_name}:",
                        status="",
                        style=None
                    )
                    print(report.caplog)
                    if hasattr(report, 'captured_stdout'):
                        print(report.captured_stdout)
                    if hasattr(report, 'captured_stderr'):
                        print(report.captured_stderr)

            elif report.skipped:
                # Handle skipped tests and log them with "SKIPPED" in yellow as
                # status
                self.log_message.info(message=f"{test_name}", status="SKIPPED")
                self.results.append((test_name, "skipped"))


def ktest(
        loglevel="INFO",
        as_entrypoint=False,
        suppress_output=True,
        no_llm=False):
    """
    Run pytest and display the results with the specified log level.

    Args:
        loglevel (str): The logging level to use.
        as_entrypoint (bool): Whether the function is being run as an
        entrypoint.
        suppress_output (bool): Whether to suppress pytest output and only show
                                TestLogPlugin output.
        no_llm (bool): Whether to skip LLM tests.

    Returns:
        int: The exit code (0 for success, 1 for failure).
        list: A list of test results when not run as an entrypoint.
    """
    # Set the default logging style
    set_default_style("pre-commit")

    # Set the logging level based on the passed argument
    set_log_level(loglevel.upper())

    # List to capture test results
    results = []

    # Create an instance of TestLogPlugin
    plugin = TestLogPlugin(log_message, results)

    import pytest
    import io
    import sys

    # Only suppress output if suppress_output is True and we're not in debug
    # mode
    if suppress_output and loglevel.upper() != "DEBUG":
        # Capture stdout and stderr
        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.stderr = captured_output
    else:
        captured_output = None

    # Prepare pytest arguments
    pytest_args = [
        "tests",
        "--tb=short",  # Short traceback format
        "--import-mode=importlib",  # Import mode
        "-v",  # Verbose mode
        "-q",  # Quiet mode to suppress most pytest output
        "--disable-warnings",  # Disable pytest warnings
    ]

    # Add the --no-llm flag to pytest_args if no_llm is True
    if no_llm:
        pytest_args.append("--no-llm")

    # Run pytest with the custom plugin and suppress its output
    exit_code = pytest.main(pytest_args, plugins=[plugin])

    if suppress_output:
        # Restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # Process the results
    results_obj = [
        {
            "name": test_name,
            "outcome": outcome
        } for test_name, outcome in results
    ]

    if as_entrypoint:
        return exit_code
    else:
        return results_obj


def ktest_entrypoint(args=None):
    """
    Entrypoint for running ktest as a script.
    """
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Run ktest")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM tests")
    parser.add_argument("--loglevel", default="INFO", help="Set the log level")
    parsed_args = parser.parse_args(args)

    # Run ktest as an entrypoint with parsed arguments
    exit_code = ktest(
        loglevel=parsed_args.loglevel,
        as_entrypoint=True,
        no_llm=parsed_args.no_llm
    )

    # Exit with the appropriate exit code
    sys.exit(exit_code)


if __name__ == "__main__":
    ktest_entrypoint()
