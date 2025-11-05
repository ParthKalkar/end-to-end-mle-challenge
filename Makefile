.DEFAULT_GOAL := help

#help:				@ list available goals
.PHONY: help
help:
	@grep -E '[a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)| sort | tr -d '#'  | awk 'BEGIN {FS = ":.*?@ "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#setup:				@ install dependencies configured in pyproject.toml
.PHONY: setup
setup:
	@echo " install dependencies"
	poetry config virtualenvs.create true
	poetry config virtualenvs.in-project true
	poetry install --no-interaction

#test:				@ run test with docker
.PHONY: test
test:
	@echo " running tests"
	docker-compose down
	docker-compose up --build test
	docker-compose down

#run:				@ run application in docker
.PHONY: run
run:
	@echo " running service"
	docker-compose down
	docker-compose up --build app



#train:				@ run model training procedure
.PHONY: train
train:
	@echo "Running model training pipeline"
	docker-compose down
	docker-compose up --build train
	docker cp mlengineer-train-1:/tmp/model_results.csv ./model_results.csv
	docker cp mlengineer-train-1:/tmp/model.joblib ./model.joblib
	docker-compose down
