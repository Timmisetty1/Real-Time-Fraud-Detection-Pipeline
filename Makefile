.PHONY: help install test run-api run-pipeline generate-data docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make run-api       - Start the REST API server"
	@echo "  make run-pipeline  - Start the streaming pipeline"
	@echo "  make generate-data - Generate test transactions"
	@echo "  make docker-up     - Start Kafka infrastructure"
	@echo "  make docker-down   - Stop Kafka infrastructure"
	@echo "  make clean         - Clean temporary files"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=html

run-api:
	cd src && python api.py

run-pipeline:
	cd src && python pipeline.py

generate-data:
	python scripts/generate_transactions.py --num 50 --fraud-rate 0.2 --delay 0.5

docker-up:
	docker-compose up -d
	@echo "Waiting for Kafka to be ready..."
	@sleep 30
	@echo "Kafka is ready!"

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage .pytest_cache/
	@echo "Cleaned up temporary files"
