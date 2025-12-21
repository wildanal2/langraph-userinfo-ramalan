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

# LangWatch Integration
install-langwatch:
	@echo "Installing LangWatch..."
	uv pip install langwatch
	@echo "✅ LangWatch installed"
	@echo ""
	@echo "Next steps:"
	@echo "1. Get API key from https://langwatch.ai"
	@echo "2. Add to .env: LANGWATCH_API_KEY=lw_xxxxx"
	@echo "3. Set LANGWATCH_ENABLED=true"
	@echo "4. Run: make run-dev"
	@echo "5. Check traces at https://app.langwatch.ai"

verify-langwatch:
	@echo "Verifying LangWatch setup..."
	@python -c "import langwatch; print('✅ LangWatch package installed')" || echo "❌ LangWatch not installed"
	@python -c "from src.core.config import settings; print(f'✅ API Key configured: {bool(settings.langwatch_api_key)}'); print(f'✅ Enabled: {settings.langwatch_enabled}')"
	@echo ""
	@echo "Run 'make run-dev' and send a test message to generate traces"
