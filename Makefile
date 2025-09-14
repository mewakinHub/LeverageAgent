SHELL := /bin/bash

.PHONY: up down logs build tunnel edge cloud

edge:
	docker compose -f docker/compose.edge.yml --env-file .env up -d

edge-down:
	docker compose -f docker/compose.edge.yml --env-file .env down

cloud:
	docker compose -f docker/compose.cloud.yml --env-file .env up -d

cloud-down:
	docker compose -f docker/compose.cloud.yml --env-file .env down

logs:
	docker compose -f docker/compose.edge.yml logs -f --tail 100

build-api:
	docker build -t leverage/langgraph-api:dev ./services/langgraph-api

backup:
	./scripts/backup.sh

restore:
	./scripts/restore.sh $(PATH)
