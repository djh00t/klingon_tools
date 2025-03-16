# Makefile for klingon-tools Python package

# Variables
APP_NAME = "klingon-tools"
PYPI_USER_AGENT ?= __token__
LOG_MSG_CONF = --level INFO --style pre-commit --message

# Clean the repository
clean:
	@log-message $(LOG_MSG_CONF) "Cleaning up repo" --status "🧹"
	@make push-prep
	@pre-commit clean
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '.aider*' ! -path './.aider_logs/*' -delete
	@find . -type d -name '.aider*' ! -path './.aider_logs' -exec rm -rf {} +
	@rm -rf .coverage
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf .tox
	@rm -rf *.egg-info
	@rm -rf build
	@rm -rf dist
	@rm -rf htmlcov
	@rm -rf node_modules
	@log-message $(LOG_MSG_CONF) "Repo cleaned up" --status "✅"

# Get developer information
get-developer-info:
	@log-message $(LOG_MSG_CONF) "Fetching commit author information..." --status "🔍"
	@COMMIT_AUTHOR=$$(git log -1 --pretty=format:'%an')
	@log-message $(LOG_MSG_CONF) "This code was committed by $$COMMIT_AUTHOR" --status "ℹ️"

# Install the package locally
install:
	@pip install -e .
	@log-message $(LOG_MSG_CONF) "Installing dependencies..." --status "⬇️"
	@poetry install

# Install the development dependencies and the package locally
install-dev:
	@log-message $(LOG_MSG_CONF) "Checking for Poetry installation..." --status "🔍"
	@if ! command -v poetry &> /dev/null; then \
		echo "Poetry not found. Installing Poetry."; \
		curl -sSL https://install.python-poetry.org | python3 -; \
	fi
	@log-message $(LOG_MSG_CONF) "Poetry is installed. Checking dependencies..." --status "🔍"
	@poetry install --with dev

# Pre-push cleanup target
push-prep:
	@log-message $(LOG_MSG_CONF) "Running Poetry Lock" --status "🔒"
	@poetry lock
	@log-message $(LOG_MSG_CONF) "Removing Temporary Files" --status "🧹"
	@find . -type f -name '*.pyc' -delete
	@log-message $(LOG_MSG_CONF) "Removed Temporary Files" --status "✅"

# Create a source distribution package
sdist: clean
	@log-message $(LOG_MSG_CONF) "Creating source distribution..."
	@poetry build --format sdist

# Run tests
test:
	@log-message $(LOG_MSG_CONF) "Running unit tests..." --status "🧪"
	@poetry run pytest -vvv --ignore=tests/test_litellm_model_cache.py --ignore=tests/test_litellm_tools.py --ignore=tests/test_openai_tools.py --ignore=tests/test_pr_context_generate.py --ignore=tests/test_pr_summary_generate.py --ignore=tests/test_pr_title_generate.py

# Run all tests including LLM tests
test-with-llm:
	@log-message $(LOG_MSG_CONF) "Running all unit tests including LLM tests..." --status "🧪"
	@poetry run pytest -vvv

# Uninstall the local package
uninstall:
	@log-message $(LOG_MSG_CONF) "Uninstalling $(APP_NAME)..." --status "❌"
	@poetry remove $(APP_NAME)

# Upload to PyPI
upload: test wheel
	@log-message $(LOG_MSG_CONF) "Uploading Version to PyPI..." --status "⬆️"
	@TWINE_USER_AGENT="$(PYPI_USER_AGENT)" poetry publish --build --no-interaction

# Upload to TestPyPI
upload-test: test wheel
	@log-message $(LOG_MSG_CONF) "Uploading Version to TestPyPI..." --status "⬆️"
	@poetry publish --repository testpypi --username $(PYPI_USER_AGENT) --password $(PYPI_USER_AGENT)

# Create a wheel distribution package
wheel: clean
	@log-message $(LOG_MSG_CONF) "Creating wheel distribution..." --status "📦"
	@poetry build --format wheel

# Commit changes after auto-fix
commit-auto-fix:
	@log-message $(LOG_MSG_CONF) "Auto-fix detected. Re-staging and reprocessing changes..." --status "🔄"
	@git add .
	@python klingon_tools/push.py --repo-path . --file-name .

.PHONY: clean check-packages sdist wheel upload-test upload install uninstall test push-prep get-developer-info release commit-auto-fix
