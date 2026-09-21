.PHONY: format dev migration migrate


format:
	uv run ruff check --fix
	uv run ruff format

dev:
	uv run manage.py runserver

migration:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate
