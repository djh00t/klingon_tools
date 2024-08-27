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
                # Check if the test is optional and log as warning
                if "optional" in report.keywords:
                    self.log_message.warning(
                        message=f"{test_name} (optional)", status="⚠️"
                    )
                    self.results.append((test_name, "optional-failed"))
                else:
                    self.log_message.error(message=f"{test_name}", status="❌")
                    self.results.append((test_name, "failed"))
                # Only print debug info if in debug mode
                if self.log_message.logger.getEffectiveLevel() <= 10:
                    self.log_message.debug(
                        message=f"Debug info for {test_name}"
                        )
                    print(report.longrepr)
            elif report.skipped:
                self.log_message.info(message=f"{test_name}", status="⏭️")
                self.results.append((test_name, "skipped"))


def ktest(loglevel="INFO", as_entrypoint=True, suppress_output=True):
    """
    Run pytest and display the results with the specified log level.

    This function runs the tests using pytest and ensures that the logging
    output is displayed.

    Args:
        loglevel (str): The logging level to use. Can be one of:
                        'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
                        Defaults to 'INFO'.
        as_entrypoint (bool): Whether the function is being run as an
        entrypoint. suppress_output (bool): Whether to suppress pytest output
        and only show TestLogPlugin output.

    Returns:
        int: The exit code (0 for success, 1 for failure) when run as an
        entrypoint. list: A list of test results when not run as an entrypoint.
    """
    # Set the default logging style
    set_default_style("pre-commit")

    # Set the logging level based on the passed argument
    set_log_level(loglevel.upper())

    # List to capture test results
    results = []

    # Create an instance of TestLogPlugin
    plugin = TestLogPlugin(log_message, results)

    # Run pytest with the custom plugin
    import pytest
    import io
    import sys

    if suppress_output:
        # Capture stdout and stderr
        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.stderr = captured_output

    exit_code = pytest.main(
        [
            "tests",
            "--tb=short",
            "--import-mode=importlib",
            "-v"
        ],
        plugins=[plugin]
        )

    if suppress_output:
        # Restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # Process the results
    results_obj = [
        {"name": test_name, "outcome": outcome}
        for test_name, outcome in results
    ]

    if as_entrypoint:
        return exit_code
    else:
        return results_obj


def ktest_entrypoint():
    """
    Entrypoint for running ktest as a script.
    """
    import sys
    # Run ktest as an entrypoint
    sys.exit(ktest(as_entrypoint=True))


if __name__ == "__main__":
    ktest_entrypoint()
