import warnings
from klingon_tools.log_msg import log_message, set_default_style, set_log_level
import pytest
import os


# Filter out specific warnings
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="pydantic"
)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="imghdr")
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="importlib_resources"
)


def ktest(loglevel="INFO"):
    """
    Run pytest and display the results with the specified log level.

    This function runs the tests using pytest and ensures that the logging
    output is displayed.

    Args:
        loglevel (str): The logging level to use. Can be one of:
                        'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
                        Defaults to 'INFO'.

    Entrypoint:
        ktest
    """
    # Set the default logging style
    set_default_style("pre-commit")

    # Set the logging level based on the passed argument
    set_log_level(loglevel.upper())

    try:
        # List to capture test results
        results = []

        class TestLogPlugin:
            def pytest_runtest_logreport(self, report):
                if report.when == "call":
                    test_name = report.nodeid
                    if report.passed:
                        log_message.info(message=f"{test_name}", status="✅")
                        results.append((test_name, "passed"))
                    elif report.failed:
                        # Check if the test is optional and log as warning
                        if "optional" in report.keywords:
                            log_message.warning(
                                message=f"{test_name} (optional)", status="⚠️"
                            )
                            results.append((test_name, "optional-failed"))
                        else:
                            log_message.error(
                                message=f"{test_name}", status="❌"
                            )
                            results.append((test_name, "failed"))
                        # Print debug info after the log messages
                        log_message.debug(
                            message=f"Debug info for {test_name}"
                        )
                        print(report.longrepr)
                    elif report.skipped:
                        log_message.info(message=f"{test_name}", status="⏭️")
                        results.append((test_name, "skipped"))

        # Redirect stdout to suppress pytest output (to prevent double logging)
        with open(os.devnull, "w") as devnull:
            original_stdout = os.dup(1)
            os.dup2(devnull.fileno(), 1)

            try:
                # Run pytest with the custom plugin
                log_message.debug("Running pytest with custom plugin")
                pytest.main(["tests", "--tb=short"], plugins=[TestLogPlugin()])
            finally:
                # Restore stdout
                os.dup2(original_stdout, 1)

        if __name__ == "__main__":
            for result in results:
                print(f"{result['name']}: {result['outcome']}")
        return [
            {"name": test_name, "outcome": outcome}
            for test_name, outcome in results
        ]
    except ImportError as e:
        log_message.error(f"ImportError: {e}", status="❌")
        return []
    except Exception as e:
        log_message.error(f"Unexpected error: {e}", status="❌")
        return []
