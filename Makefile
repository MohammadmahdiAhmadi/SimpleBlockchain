.PHONY: build
build: build-frontend build-backend

.PHONY: build-frontend
build-frontend:
	docker build -t simple-blockchain-frontend -f Dockerfile.frontend .

.PHONY: build-backend
build-backend:
	docker build -t simple-blockchain-backend -f Dockerfile.backend .

.PHONY: up
up:
	docker-compose up -d

.PHONY: down
down:
	docker-compose down

.PHONY: restart
restart: down
	docker-compose up -d

.PHONY: rebuild-up
rebuild-up: down build
	docker-compose up -d
