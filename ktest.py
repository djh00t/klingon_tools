from klingon_tools.log_msg import log_tools
import pytest
import os

# Set logging level and style
log_tools.set_default_style("pre-commit")
log_tools.set_log_level("DEBUG")

# Initialize logger
logger = log_tools  # Use the same instance as imported
log_message = logger.log_message


def pytest_run_tests():
    # List to capture test results
    results = []

    class MyPlugin:
        def pytest_runtest_logreport(self, report):
            if report.when == "call":
                test_name = report.nodeid
                if report.passed:
                    log_message.info(message=f"{test_name}", status="✅")
                    results.append((test_name, "passed"))
                elif report.failed:
                    log_message.error(message=f"{test_name}", status="❌")
                    results.append((test_name, "failed"))
                    # Print debug info after the log messages
                    log_message.debug(message=f"Debug info for {test_name}")
                    print(report.longrepr)
                elif report.skipped:
                    log_message.info(message=f"{test_name}", status="⏭️")
                    results.append((test_name, "skipped"))

    # Redirect stdout to suppress pytest output
    with open(os.devnull, "w") as devnull:
        original_stdout = os.dup(1)
        os.dup2(devnull.fileno(), 1)

        try:
            # Run pytest with the custom plugin
            pytest.main(["tests", "--tb=short"], plugins=[MyPlugin()])
        finally:
            # Restore stdout
            os.dup2(original_stdout, 1)

    # Return the results
    return results


if __name__ == "__main__":
    try:
        test_results = pytest_run_tests()
    except Exception as e:
        log_message.error(message=f"An error occurred: {str(e)}")
        raise e
