DOCKER_BUILD_CMD?=docker build
DOCKER_NAME?=dlrs-pytorch-classify
DOCKER_IMAGE?=dlrs-pytorch-classify
DOCKER_FILE?=./Dockerfile
DOCKER_WS=./

all .DEFAULT:
	$(DOCKER_BUILD_CMD)  -f $(DOCKER_FILE) -t $(DOCKER_IMAGE)  $(DOCKER_WS)

run:
	docker run --rm  -p 5059:5059 $(DOCKER_IMAGE)
clean:
	docker rmi $(DOCKER_IMAGE)

.PHONY: $(DEFAULT_TARGETS)
