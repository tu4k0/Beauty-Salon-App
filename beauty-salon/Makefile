PROJECT_IMAGE ?= barber:develop
PROJECT_CONTAINER ?= data_visualization_web_1
CI_COMMIT_SHORT_SHA ?= $(shell git rev-parse --short HEAD)
GIT_STAMP ?= $(shell git describe)

.EXPORT_ALL_VARIABLES:

run: COMPOSE ?= docker-compose -f compose-dev.yml
run: docker-build
	$(COMPOSE) up

docker-build:
	docker build --build-arg version=$(GIT_STAMP) -t $(PROJECT_IMAGE) .

rm: COMPOSE ?= docker-compose -f compose-dev.yml
rm:
	$(COMPOSE) stop
	$(COMPOSE) rm -f
