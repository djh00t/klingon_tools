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
        "--no-llm", action="store_true", default=False, help="Skip LLM tests"
    )


@pytest.fixture
def no_llm(pytestconfig):
    return pytestconfig.getoption("--no-llm")
