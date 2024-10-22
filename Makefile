install:
	poetry install

test: 
	poetry run pytest -v -s --tb=long --showlocals --log-cli-level=DEBUG 

deploy:
	poetry run python deploy.py

load-credentials:
	export GOOGLE_APPLICATION_CREDENTIALS="config/credentials.json"

arg = $(word 2, $(MAKECMDGOALS))

run:
	@echo "Running local entry point"
	poetry run python local_entry.py $(arg)


%:
	@: