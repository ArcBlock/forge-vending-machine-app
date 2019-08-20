TOP_DIR=.
VERSION=$(strip $(shell cat version))
VENV=vending-machine

PROTOS=$(TOP_DIR)/src/protos/aggregate
SIMULATOR_APP=$(TOP_DIR)/src/simulator
PROTO_OUTPUT=$(SIMULATOR_APP)/protos
VENDOR_PROTOS=$(SIMULATOR_APP)/_vendors/lib/protobuf/


init: install create_env
	@echo "Initializing the repo..."
	@git submodule update --init --recursive

install:
	@pip install virtualenv
	@pip install virtualenvwrapper


create_env:
	( \
		source /usr/local/bin/virtualenvwrapper.sh; \
		mkvirtualenv $(VENV); \
		make dep; \
		pre-commit install; \
	)


travis-init: dep
	@echo "Initialize software required for travis (normally ubuntu software)"

travis-deploy:
	@echo "Deploy the software by travis"
	@make release

precommit: pre-build build post-build test

travis: precommit

pre-build: dep
	@echo "Running scripts before the build..."

post-build:
	@echo "Running scripts after the build is done..."

build: build-proto
	@echo "Building the software..."
	
build-proto:
	@(git clone https://github.com/arcblock/forge_abi $(SIMULATOR_APP)/_vendors --depth 1) || true
	@protoc -I=$(PROTOS) -I=$(VENDOR_PROTOS) -I=$(SIMULATOR_APP)/_vendors/vendors --python_out=$(PROTO_OUTPUT) $(PROTOS)/aggregate.proto
	@sed 's/type_pb2/forge_sdk.protos.protos.type_pb2/g' $(PROTO_OUTPUT)/aggregate_pb2.py > $(PROTO_OUTPUT)/aggregate.py
	@mv $(PROTO_OUTPUT)/aggregate.py $(PROTO_OUTPUT)/aggregate_pb2.py

format:
	@echo "Format code..."

dep:
	@echo "Install dependencies required for this repo..."
	pip3 install -r $(SIMULATOR_APP)/requirements.txt;

test:
	@echo "Running test suites..."

run-sim:
	@python3 $(SIMULATOR_APP)/aggregate_simulator.py

include .makefiles/*.mk

.PHONY: build init travis-init install dep pre-build post-build all test dialyzer doc precommit travis run