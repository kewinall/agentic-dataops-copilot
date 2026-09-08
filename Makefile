.PHONY: install lint test eval run docker-build

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest --cov=agentic_dataops_copilot --cov-report=term-missing

eval:
	python -m agentic_dataops_copilot.knowledge.evaluation --top-k 3 --min-hit-rate 0.90

run:
	uvicorn agentic_dataops_copilot.main:app --reload

docker-build:
	docker build -t agentic-dataops-copilot:local .
