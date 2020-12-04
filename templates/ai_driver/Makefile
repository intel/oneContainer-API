DOCKER_BUILD_CMD?=docker build
DOCKER_NAME?=<ai-driver-name>
DOCKER_IMAGE?=<ai-driver-image>
DOCKER_FILE?=./Dockerfile
DOCKER_WS=./

all .DEFAULT:
	$(DOCKER_BUILD_CMD)  -f $(DOCKER_FILE) -t $(DOCKER_IMAGE)  $(DOCKER_WS)

run:
	docker-compose up --build
clean:
	docker rmi $(DOCKER_IMAGE)

.PHONY: $(DEFAULT_TARGETS)
