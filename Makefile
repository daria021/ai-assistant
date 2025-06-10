bw:
	docker build -f worker/Dockerfile -t account-worker .

mn:
	docker network create assistant_bridge

localup:
	docker compose -f local.compose.yml up --build -d
