.PHONY: all build build-nocache

build-nocache:
	docker build --pull --no-cache -t boxboat/kubeless-python-fastapi:latest -f Dockerfile .

build:
	docker build -t boxboat/kubeless-python-fastapi:latest -f Dockerfile .

push:
	docker push boxboat/kubeless-python-fastapi:latest
