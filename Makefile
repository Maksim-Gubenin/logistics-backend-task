# Переменная для сокращения команд
COMPOSE_T = docker compose -f docker-compose.test.yml --env-file .env.test
RUN_T = $(COMPOSE_T) run --rm app_test poetry run

.PHONY: test test-unit test-int clean help

all: test

test: prepare-db
	@echo "🚀 Running all tests with coverage..."
	$(RUN_T) pytest

test-unit:
	@echo "🧪 Running unit tests..."
	$(RUN_T) pytest tests/unit

test-int:
	@echo "🔗 Running integration tests..."
	$(RUN_T) pytest tests/integration

prepare-db:
	@echo "🛠️ Preparing test environment..."
	$(COMPOSE_T) down -v --remove-orphans
	$(COMPOSE_T) up -d db_test
	@echo "⏳ Waiting for DB..."
	$(COMPOSE_T) exec db_test sh -c 'until pg_isready -U user -d logistic_test; do sleep 1; done'
	@echo "🧬 Running migrations..."
	$(RUN_T) alembic upgrade head
	@echo "🌱 Seeding data..."
	$(COMPOSE_T) run --rm db_seed_test

clean:
	$(COMPOSE_T) down -v --remove-orphans
	@echo "🧹 Cleaned up all test containers and volumes."

cov-html:
	$(RUN_T) pytest --cov-report=html
	@echo "📈 HTML report generated in htmlcov/index.html"

help:
	@echo "Available commands:"
	@echo "  make test       - Run all tests (full cycle)"
	@echo "  make test-unit  - Run only unit tests"
	@echo "  make test-int   - Run only integration tests"
	@echo "  make clean      - Remove test containers and volumes"