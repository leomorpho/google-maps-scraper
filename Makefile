.PHONY: help venv install dev clean run docker-up docker-down docker-build

# Default target
help:
	@echo "Available targets:"
	@echo "  venv        - Create virtual environment with uv"
	@echo "  install     - Install dependencies with uv"
	@echo "  dev         - Install dependencies and run development server"
	@echo "  run         - Run the FastAPI application with auto-reload"
	@echo "  clean       - Remove virtual environment and cache files"
	@echo "  docker-up   - Start Docker containers"
	@echo "  docker-down - Stop Docker containers"
	@echo "  docker-build- Build and start Docker containers"

# Create virtual environment with uv
venv:
	uv venv

# Install dependencies
install: venv
	uv pip install -r requirements.txt
	uv run playwright install --with-deps

# Development setup and run
dev: install run

# Run the application with uv
run:
	uv run uvicorn gmaps_scraper_server.main_api:app --reload

# Clean up
clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose up --build