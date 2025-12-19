.PHONY: install dev test run clean docker-up docker-down

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term

run:
	python run.py

run-dev:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov dist build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f app

format:
	black src/ tests/

lint:
	ruff check src/ tests/

type-check:
	mypy src/

quality: format lint type-check
	@echo "Code quality checks completed"
