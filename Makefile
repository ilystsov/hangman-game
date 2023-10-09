lint:
	poetry run isort src tests
	poetry run flake8 src tests
	poetry run mypy src
	poetry run mypy tests

test:
	poetry run pytest --cov=src --cov-report html

build:
	poetry build

run:
	python3 src/hangman/game.py
