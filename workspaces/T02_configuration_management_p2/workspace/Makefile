# T02: Configuration Management — Docker Compose Full Stack
#
# Quick commands:
#   make compose-check     — validate docker-compose.yml
#   make test              — run all tests
#   make lint              — check Python files with ruff
#   make build             — docker compose build (dry mode)
#

.PHONY: compose-check test lint build stop clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

compose-check: ## Validate docker-compose.yml syntax
	docker compose -f docker-compose.yml config --quiet

test: ## Run pytest suite
	@echo "=== Running tests ==="
	python -m pytest tests/ -v --tb=short
	@echo "=== All tests passed ==="

lint: ## Lint Python files with ruff
	ruff check app/ tests/ --fix
	ruff format app/ tests/ --check

docker-test: ## Validate compose file with docker compose config
	docker compose -f docker-compose.yml config 1>/dev/null

build: ## Docker compose build (no cache)
	docker compose -f docker-compose.yml build --no-cache

start: ## Start the stack
	docker compose -f docker-compose.yml up -d

stop: ## Stop the stack
	docker compose -f docker-compose.yml down -v

clean: ## Remove volumes and orphans
	docker compose -f docker-compose.yml down -v --remove-orphans
