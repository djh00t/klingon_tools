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

# Ensure that the latest Node.js and npm are installed
ensure-node: fetch-latest-node-version install-latest-nvm
	@if [ "$$(uname)" = "Linux" ]; then \
		if [ -f /etc/debian_version ]; then \
			echo "Detected Debian-based Linux. Installing Node.js $$(cat .latest_node_version)..."; \
			curl -sL https://deb.nodesource.com/setup_$$(cat .latest_node_version | cut -d'.' -f1).x | sudo bash -; \
			sudo apt-get install -y nodejs; \
		else \
			echo "Unsupported Linux distribution. Exiting..."; \
			exit 1; \
		fi \
	elif [ "$$(uname)" = "Darwin" ]; then \
		log-message $(LOG_MSG_CONF) "Detected macOS. Checking for Homebrew..." --status "🔍"; \
		if ! command -v brew >/dev/null 2>&1; then \
			echo "Homebrew not found. Installing Homebrew..."; \
			/bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; \
		fi; \
		NODE_MAJOR_VERSION=$$(cat .latest_node_version | cut -d'.' -f1 | tr -d 'v'); \
		if brew ls --versions node@$$NODE_MAJOR_VERSION > /dev/null; then \
			echo "Installing Node.js $$NODE_MAJOR_VERSION using Homebrew..."; \
			brew install node@$$NODE_MAJOR_VERSION; \
		else \
			echo "Specific Node.js version not available in Homebrew. Installing using nvm..."; \
			export NVM_DIR="$$HOME/.nvm"; \
			[ -s "$$NVM_DIR/nvm.sh" ] && \. "$$NVM_DIR/nvm.sh"; \
			nvm install $$(cat .latest_node_version); \
			nvm use $$(cat .latest_node_version); \
		fi; \
	else \
		echo "Unsupported OS. Exiting..."; \
		exit 1; \
	fi

# Ensure that semantic-release is installed
ensure-semantic-release:
	@npm list -g --depth=0 | grep semantic-release >/dev/null 2>&1 || { \
		log-message $(LOG_MSG_CONF) "semantic-release is not installed. Installing..." --status "⬇️"; \
		npm install -g semantic-release; \
	}

# Fetch the latest Node.js version
fetch-latest-node-version:
	@curl -s https://nodejs.org/dist/index.json | grep '"version"' | head -1 | awk -F'"' '{print $$4}' > .latest_node_version
	@log-message $(LOG_MSG_CONF) "Latest Node.js version: $$(cat .latest_node_version)" --status "ℹ️"

# Get developer information
get-developer-info:
	@log-message $(LOG_MSG_CONF) "Fetching commit author information..." --status "🔍"
	@COMMIT_AUTHOR=$$(git log -1 --pretty=format:'%an')
	@log-message $(LOG_MSG_CONF) "This code was committed by $$COMMIT_AUTHOR" --status "ℹ️"

# Get first octet of current node version
node-major-version:
	@curl -s https://nodejs.org/dist/index.json | grep '"version"' | head -1 | awk -F'"' '{print $$4}' | sed 's/^v//' | awk -F'.' '{print $$1}'

# Install the package locally
install:
	@poetry install
	@log-message $(LOG_MSG_CONF) "Installing dependencies..." --status "⬇️"

# Install the development dependencies and the package locally
install-dev:
	@log-message $(LOG_MSG_CONF) "Checking for Poetry installation..." --status "🔍"
	@if ! command -v poetry &> /dev/null; then \
		echo "Poetry not found. Installing Poetry."; \
		curl -sSL https://install.python-poetry.org | python3 -; \
	fi
	@log-message $(LOG_MSG_CONF) "Poetry is installed. Checking dependencies..." --status "🔍"
	@poetry install --with dev

# Install the latest version of nvm
install-latest-nvm:
	@log-message $(LOG_MSG_CONF) "Installing the latest version of nvm..." --status "⬇️"
	@LATEST_NVM_VERSION=$$(curl -s https://api.github.com/repos/nvm-sh/nvm/releases/latest | grep -oE '"tag_name": "[^"]+"' | cut -d'"' -f4) && \
	curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/$$LATEST_NVM_VERSION/install.sh | bash

# Perform a semantic release
release: ensure-node ensure-semantic-release
	@log-message $(LOG_MSG_CONF) "Starting semantic release..." --status "🚀"
	@semantic-release

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
