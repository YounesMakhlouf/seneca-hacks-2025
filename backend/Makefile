# Makefile for Body-to-Behavior Recommender (Docker helpers)

# Fail early if .env missing when needed
ifeq (,$(wildcard .env))
$(warning No .env file found. You can copy .env.example to .env to customize settings.)
endif

PROJECT_NAME := bbr
NETWORK := bbr-net
API_SERVICE := api
MONGO_SERVICE := mongo

.DEFAULT_GOAL := help

# --- Infrastructure ---

build: ## Build docker images
	docker compose build

up: ## Start stack (detached)
	docker compose up --build -d

stop: ## Stop running containers (preserve state)
	docker compose stop

restart: ## Restart containers
	docker compose restart

down: ## Stop and remove containers + network (keep volumes)
	docker compose down

nuke: ## Full teardown including volumes (DANGEROUS)
	docker compose down -v --remove-orphans

logs: ## Follow API logs
	docker compose logs -f $(API_SERVICE)

ps: ## Show service status
	docker compose ps

shell: ## Exec into API container shell
	docker compose exec $(API_SERVICE) /bin/bash || docker compose exec $(API_SERVICE) sh

mongo-shell: ## Open mongosh inside mongo container
	docker compose exec $(MONGO_SERVICE) mongosh

seed-check: ## Show counts in Mongo (quick sanity check)
	@docker compose exec $(MONGO_SERVICE) mongosh --quiet --eval 'db.getSiblingDB("bbr").users.count()' | awk '{print "users:", $$1}'
	@docker compose exec $(MONGO_SERVICE) mongosh --quiet --eval 'db.getSiblingDB("bbr").sleep.count()' | awk '{print "sleep:", $$1}'
	@docker compose exec $(MONGO_SERVICE) mongosh --quiet --eval 'db.getSiblingDB("bbr").nutrition.count()' | awk '{print "nutrition:", $$1}'
	@docker compose exec $(MONGO_SERVICE) mongosh --quiet --eval 'db.getSiblingDB("bbr").activity.count()' | awk '{print "activity:", $$1}'

reset-db: ## Drop Mongo database (bbr) then restart API
	docker compose exec $(MONGO_SERVICE) mongosh --quiet --eval 'db.getSiblingDB("bbr").dropDatabase()'
	docker compose restart $(API_SERVICE)

api-test: ## Run pytest inside container
	docker compose exec $(API_SERVICE) uv run pytest -q || (echo "Tests failed" && exit 1)

format: ## (Placeholder) Format code (add ruff/black later if desired)
	@echo "No formatter configured yet."

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | sort
