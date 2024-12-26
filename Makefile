# MAKEMCMDGOALS is a special variable that contains the list of goals passed to make
# %: @ allows Make to accept any goal without complaint
arg = $(word 2, $(MAKECMDGOALS))

install:
	poetry install

test: 
	poetry run pytest -v -s --tb=long --showlocals --log-cli-level=DEBUG $(arg)

deploy:
	poetry run python deploy.py

load-credentials:
	export GOOGLE_APPLICATION_CREDENTIALS="config/credentials.json"


run-local:
	@echo "Running local entry point"
	PYTHONPATH=$PYTHONPATH:$(pwd) poetry run python $(arg)


%:
	@
