.PHONY: up down engine worker gateway dash test lint bench demo clean

COMPOSE_FILE = deploy/docker-compose.yml

up:
	docker compose -f $(COMPOSE_FILE) up -d

down:
	docker compose -f $(COMPOSE_FILE) down

engine:
	python -m uvicorn app.main:app --app-dir engine --reload --port 8001

worker:
	python -m rq worker agentgate-reviews --url redis://localhost:6379/0

gateway:
	cd gateway && ./mvnw spring-boot:run

dash:
	cd dashboard && npm run dev

test:
	pytest engine/tests
	cd dashboard && npm test -- --run

lint:
	python -m ruff check engine/
	python -m mypy engine/
	cd dashboard && npm run lint

bench:
	python bench/run.py --mode full --repeats 3
	python bench/report.py

demo:
	python scripts/seed_demo.py
