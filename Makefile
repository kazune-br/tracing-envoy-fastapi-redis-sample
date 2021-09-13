.PHONY: update-dependency build up down logs lint

BASE_DOCKER_COMPOSE = docker-compose.yaml
COMPOSE_OPTS        = -f "$(BASE_DOCKER_COMPOSE)"
ID := a

update-dependency:
	poetry install && \
    poetry export -f requirements.txt --without-hashes --output requirements.txt

build: update-dependency lint
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose $(COMPOSE_OPTS) build --parallel

up: build
	docker compose $(COMPOSE_OPTS) up -d

down:
	docker compose $(COMPOSE_OPTS) down

logs:
	docker compose $(COMPOSE_OPTS) logs -f

login:
	docker exec -it app bash

health:
	curl localhost:9000/healthcheck | jq .

insert:
	curl -i -X POST localhost:9000/v1/data -H "Content-Type: application/json" -d $$(./scripts/datum_generator.sh)

select:
	@curl localhost:9000/v1/data/${ID}

select-by-cli:
	redis-cli --pass password --no-auth-warning zrange ${ID} 0 -1

flush:
	redis-cli --pass password --no-auth-warning FLUSHALL

lint: sort autoflake black

sort:
	poetry run isort . --profile black

autoflake:
	poetry run autoflake -r --check \
		--remove-all-unused-imports \
		--ignore-init-module-imports \
		--remove-unused-variables .
black:
	poetry run black ./
