.PHONY: install lint test run docker-build

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest --cov=agentic_dataops_copilot --cov-report=term-missing

run:
	uvicorn agentic_dataops_copilot.main:app --reload

docker-build:
	docker build -t agentic-dataops-copilot:local .
