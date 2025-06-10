bw:
	docker build -f worker/Dockerfile -t account-worker .

mn:
	@docker network inspect ai_network >/dev/null 2>&1 || \
	  docker network create ai_network

localup:
	docker compose -f local.compose.yml up --build -d
