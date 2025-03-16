import pytest
import warnings


@pytest.fixture(autouse=True)
def ignore_warnings():
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="pydantic"
    )
    warnings.filterwarnings(
        "ignore",
        message="Support for class-based `config` is deprecated*",
        category=DeprecationWarning,
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="imghdr"
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="importlib_resources"
    )
    warnings.filterwarnings(
        "ignore",
        message="'imghdr' is deprecated and slated for removal in Python 3.13",
        category=DeprecationWarning,
    )
    warnings.filterwarnings(
        "ignore",
        message="open_text is deprecated. Use files() instead.",
        category=DeprecationWarning,
    )


def pytest_addoption(parser):
    parser.addoption(
        "--run-llm", action="store_true", default=False,
        help="Run LLM tests (skipped by default)"
    )


@pytest.fixture
def no_llm(pytestconfig):
    """
    Fixture to determine if LLM tests should be skipped.
    Returns True if LLM tests should be skipped (default).
    For backward compatibility, keeps the name 'no_llm'.
    """
    return not pytestconfig.getoption("--run-llm")


@pytest.fixture
def run_llm(pytestconfig):
    """
    Fixture to determine if LLM tests should be run.
    Returns True if LLM tests should be run, False otherwise.
    This is the inverse of no_llm for better readability in new tests.
    """
    return pytestconfig.getoption("--run-llm")
