.DEFAULT_GOAL := compile

## help: print this help message
help:
	@echo 'Usage: (default update-schema fmt lint test build)'
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'

## lint: Perform code linting
lint:
	pipenv run ruff check

## fmt: Perform formatting of the code
fmt:
	pipenv run ruff format

## build: Build docker image
build:
	docker build -t coverflex-actual .

## run: Build docker image
run:
	pipenv run python coverflex-actual/coverflex.py