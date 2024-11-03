test:
	docker exec -it chat-web pytest --disable-warnings -v $(path)

start:
	docker compose up --build
