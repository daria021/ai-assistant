bw:
	docker build -f worker/Dockerfile -t account-worker --label keep=yes .

mn:
	@docker network inspect assistant_bridge >/dev/null 2>&1 || \
	  docker network create assistant_bridge

.PHONY: prepare-dirs
prepare-dirs:
	mkdir -p ./data/loki ./data/grafana ./data/promtail

localup: prepare-dirs
	docker compose -f local.compose.yaml up --build -d
