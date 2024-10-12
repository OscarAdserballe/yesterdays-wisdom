install:
	poetry install

test: 
	poetry run pytest tests

run-local: 
	poetry run python local_entry.py

deploy:
	poetry run python deploy.py

load-credentials:
	export GOOGLE_APPLICATION_CREDENTIALS="config/credentials.json"