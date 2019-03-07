# author: {{ cookiecutter.author_name }}

OS_VERSION := $(shell uname -a)
ifneq (,$(findstring Microsoft,$(OS_VERSION)))
$(info    detected WSL)
export DOCKER_COMPOSE=docker-compose
export DOCKER=docker
else ifeq ($(OS), Windows_NT)
$(info    detected Powershell/CMD)
export DOCKER_COMPOSE=docker-compose.exe
export DOCKER=docker.exe
else ifneq (,$(findstring Darwin,$(OS_VERSION)))
$(info    detected OSX)
export DOCKER_COMPOSE=docker-compose
export DOCKER=docker
else
$(info    detected native linux)
export DOCKER_COMPOSE=docker-compose
export DOCKER=docker
endif

export VCS_URL:=$(shell git config --get remote.origin.url)
export VCS_REF:=$(shell git rev-parse --short HEAD)
export VCS_STATUS_CLIENT:=$(if $(shell git status -s),'modified/untracked','clean')
export BUILD_DATE:=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
export DOCKER_REGISTRY=masu.speag.com


## Tools ------------------------------------------------------------------------------------------------------
#
tools =

ifeq ($(shell uname -s),Darwin)
	SED = gsed
else
	SED = sed
endif

ifeq ($(shell which ${SED}),)
	tools += $(SED)
endif


## ------------------------------------------------------------------------------------------------------
.PHONY: all
all: help info
ifdef tools
	$(error "Can't find tools:${tools}")
endif


.PHONY: build
# target: build: – Builds all service images.
build: update_compose_labels
	${DOCKER_COMPOSE} -f docker-compose.yml build --parallel

.PHONY: up down
# target: up, down: – Starts/Stops services.
up: .env down
	${DOCKER_COMPOSE} -f docker-compose.yml up

down:
	${DOCKER_COMPOSE} -f docker-compose.yml down

## -------------------------------
# Testing.

.PHONY: unit-test integration-test
# target: unit-test – Runs unit tests [w/ fail fast]
unit-test:
	"pytest" -x -v --log-level=warning tests/unit

# target: integration-test – Runs integration tests [w/ fail fast] (needs built container)
integration-test:
	"pytest" -x -v --log-level=warning tests/integration

.PHONY: push-release push-staging
# target: push: – Pushes services to the registry.
push-release:
	${DOCKER} login ${DOCKER_REGISTRY};\
	SERVICE_VERSION=$$(cat VERSION);\
	${DOCKER} tag \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:latest \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:$$SERVICE_VERSION;\
	${DOCKER} push \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:$$SERVICE_VERSION;

push-staging:
	${DOCKER} login ${DOCKER_REGISTRY};\
	${DOCKER} tag \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:latest \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:staging-latest;\
	${DOCKER} push \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:staging-latest;

# basic checks -------------------------------------
.env: .env-devel
	# first check if file exists, copies it
	@if [ ! -f $@ ]	; then \
		echo "##### $@ does not exist, copying $< ############"; \
		cp $< $@; \
	else \
		echo "#####  $< is newer than $@ ####"; \
		diff -uN $@ $<; \
		false; \
	fi

update_compose_labels:
	pip install -r tools/requirements.txt
	python3 tools/update_compose_labels.py --compose docker-compose.yml --input docker/labels

.PHONY: info
# target: info – Displays some parameters of makefile environments
info:
	@echo '+ VCS_* '
	@echo '  - ULR                : ${VCS_URL}'
	@echo '  - REF                : ${VCS_REF}'
	@echo '  - (STATUS)REF_CLIENT : (${VCS_STATUS_CLIENT})'
	@echo '+ BUILD_DATE           : ${BUILD_DATE}'
	@echo '+ OS_VERSION           : ${OS_VERSION}'
	@echo '+ DOCKER_REGISTRY      : ${DOCKER_REGISTRY}'


## -------------------------------
# Virtual Environments
.venv:
# target: .venv – Creates a python virtual environment with dev tools (pip, pylint, ...)
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip wheel setuptools
	.venv/bin/pip3 install pylint autopep8 virtualenv
	@echo "To activate the venv, execute 'source .venv/bin/activate' or '.venv/bin/activate.bat' (WIN)"

## -------------------------------
# Auxiliary targets.

.PHONY: clean
# target: clean – Cleans all unversioned files in project
clean:
	@git clean -dxf -e .vscode/


.PHONY: help
# target: help – Display all callable targets
help:
	@echo "Make targets in osparc-simcore:"
	@echo
	@egrep "^\s*#\s*target\s*:\s*" [Mm]akefile \
	| $(SED) -r "s/^\s*#\s*target\s*:\s*//g"
	@echo
