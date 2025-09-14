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

infrastructure-build: ## Build docker images
	docker compose build

infrastructure-up: ## Start stack (detached)
	docker compose up --build -d

infrastructure-stop: ## Stop running containers (preserve state)
	docker compose stop

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