bw:
	docker build -f worker/Dockerfile -t account-worker --label keep=yes .

mn:
	@docker network inspect assistant_bridge >/dev/null 2>&1 || \
	  docker network create assistant_bridge

localup:
	docker compose -f local.compose.yaml up --build -d
