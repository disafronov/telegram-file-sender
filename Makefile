# Python version is pinned via `.python-version` (used by uv and CI).
PYTHON_VERSION := $(shell tr -d '[:space:]' < .python-version)

UV = uv
UV_RUN = $(UV) run --locked

DOCKER_IMAGE = telegram-file-sender

DOCKER_RUN_OPTS = --rm \
	--read-only \
	--tmpfs /tmp \
	$(if $(wildcard env.example),--env-file env.example,) \
	$(if $(wildcard .env),--env-file .env,)

.PHONY: all audit clean dead-code docker docker-build docker-run format help install lint test

help: ## Show this help message
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

install: ## Install dependencies
	@echo "Installing dependencies..."
	$(UV) python install $(PYTHON_VERSION)
	$(UV) sync --locked --python $(PYTHON_VERSION)
	@echo "Installing pre-commit hooks..."
	$(UV_RUN) pre-commit install

format: ## Format code
	@echo "Formatting code..."
	$(UV_RUN) black . && $(UV_RUN) isort .

lint: ## Run linting tools
	@echo "Running linting tools..."
	$(UV_RUN) black --check . && \
	$(UV_RUN) isort --check-only . && \
	$(UV_RUN) flake8 . && \
	$(UV_RUN) mypy && \
	$(UV_RUN) bandit -c pyproject.toml -r telegram_file_sender/

audit: ## Check dependencies for known vulnerabilities
	@echo "Auditing dependencies..."
	$(UV_RUN) pip-audit

dead-code: ## Check for dead code using vulture
	@echo "Checking for dead code..."
	$(UV_RUN) vulture

test: ## Run tests with coverage
	@echo "Running tests with coverage..."
	$(UV_RUN) python -m pytest -v --cov --cov-report=term-missing --cov-report=html

all: lint test dead-code ## Run lint, test, and dead-code check
	@echo "All checks completed successfully!"

docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE) .

docker-run: ## Run Docker container (sends the file, then exits)
	@echo "Running Docker container..."
	docker run $(DOCKER_RUN_OPTS) $(DOCKER_IMAGE)

docker: docker-build docker-run ## Build and run Docker container
	@echo "Docker container built and running!"

clean: ## Clean cache and temporary files
	@echo "Cleaning cache and temporary files..."
	rm -rf .mypy_cache/ .pytest_cache/ .venv/ build/ dist/ htmlcov/ .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
