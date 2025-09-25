.PHONY: edge edge-down logs ps build-api push-api backup restore cloud cloud-down

edge:
	docker compose -f infra/docker/compose.edge.yml --env-file infra/.env up -d --build

edge-down:
	docker compose -f infra/docker/compose.edge.yml --env-file infra/.env down

cloud:
	docker compose -f infra/docker/compose.cloud.yml --env-file infra/.env up -d --build

cloud-down:
	docker compose -f infra/docker/compose.cloud.yml --env-file infra/.env down

logs:
	docker compose -f infra/docker/compose.edge.yml logs -f --tail 200

ps:
	docker compose -f infra/docker/compose.edge.yml ps

# build image w/ repository/name as leverage/langgraph-api and dev tag
build-api:
	docker build -t leverage/langgraph-api:dev ./infra/services/langgraph-api

push-api:
	docker tag leverage/langgraph-api:dev YOURUSER/leverage-langgraph:dev
	docker push YOURUSER/leverage-langgraph:dev

backup:
	bash infra/scripts/backup.sh

restore:
	bash infra/scripts/restore.sh $(IN)
