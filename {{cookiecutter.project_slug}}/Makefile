#
# CONVENTIONS:
#
# - targets shall be ordered such that help list rensembles a typical workflow, e.g. 'make devenv tests'
# - add doc to relevant targets
# - internal targets shall start with '.'
# - KISS
#
# author: {{ cookiecutter.author_name }}

SHELL = /bin/bash
.DEFAULT_GOAL := help

ifeq (,$(wildcard .git))
# NOTE: will prevent failure of recipes when not in git repo
$(info WARNING: not running in a git repository!!!)
export git=echo
endif
export VCS_URL:=$(shell $(git) config --get remote.origin.url)
export VCS_REF:=$(shell $(git) rev-parse --short HEAD)
export VCS_STATUS_CLIENT:=$(if $(shell $(git) status -s),'modified/untracked','clean')
export BUILD_DATE:=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

KERNEL_VERSION=$(shell cat VERSION)

export DOCKER_REGISTRY ?= {{ cookiecutter.default_docker_registry }}
export DOCKER_IMAGE_NAME ?= simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}
export DOCKER_IMAGE_TAG ?= $(KERNEL_VERSION)

export COMPOSE_INPUT_DIR := ./validation/input
export COMPOSE_OUTPUT_DIR := .tmp/output

metatada = metadata/metadata.yml

#-----------------------------------
.PHONY: devenv
.venv:
	python3 -m venv $@
	# upgrading package managers
	$@/bin/pip3 install --upgrade \
		pip \
		wheel \
		setuptools
	# tooling
	$@/bin/pip3 install pip-tools

requirements.txt: requirements.in
	# freezes requirements
	.venv/bin/pip-compile -v --output-file $@ $<

devenv: .venv requirements.txt ## create a python virtual environment with tools to dev, run and tests cookie-cutter
	# installing extra tools
	@$</bin/pip3 install -r  $(word 2,$^)
	# your dev environment contains
	@$</bin/pip3 list
	@echo "To activate the virtual environment, run 'source $</bin/activate'"


#-----------------------------------
service.cli/run: $(metatada)
	# Updates adapter script from metadata in $<
	@.venv/bin/python3 tools/run_creator.py --metadata $< --runscript $@

docker-compose-meta.yml: $(metatada)
	# Injects metadata from $< as labels
	@.venv/bin/python3 tools/update_compose_labels.py --compose $@ --metadata $<

define _docker_compose_build
export DOCKER_BUILD_TARGET=$(if $(findstring -devel,$@),development,$(if $(findstring -cache,$@),cache,production)); \
docker-compose -f docker-compose-build.yml -f docker-compose-meta.yml build $(if $(findstring -nc,$@),--no-cache,)
endef

#----------------------------------- images
.PHONY: build build-devel
build build-devel: docker-compose-build.yml docker-compose-meta.yml service.cli/run ## builds images
	# building image local/${DOCKER_IMAGE_NAME}...
	$(_docker_compose_build) --parallel
	# built local/${DOCKER_IMAGE_NAME}

define show-meta
	$(foreach iid,$(shell docker images */$(1):* -q | sort | uniq),\
		docker image inspect $(iid) | jq '.[0] | .RepoTags, .ContainerConfig.Labels';)
endef

info-build: ## displays info on the built image
	# Built images
	@docker images */$(DOCKER_IMAGE_NAME):*
	# Tags and labels
	@$(call show-meta,$(DOCKER_IMAGE_NAME))

#-----------------------------------
.PHONY: tests tests-unit tests-integration

#----------------------------------- testing
tests-unit tests-integration:
	@.venv/bin/pytest -vv \
		--basetemp=$(CURDIR)/tmp \
		--exitfirst \
		--failed-first \
		--pdb \
		--junitxml=pytest_$(subst tests-,,$@)test.xml \
		$(CURDIR)/tests/$(subst tests-,,$@)

tests: tests-unit tests-integration ## runs unit and integration tests

#----------------------------------- versioning
.PHONY: version-kernel-patch version-kernel-minor version-kernel-major
version-kernel-patch version-kernel-minor version-kernel-major: versioning/kernel.cfg ## kernel/service versioning as patch
	@bump2version --verbose  --list --config-file $< $(subst version-kernel-,,$@)

.PHONY: version-integration-patch version-integration-minor version-integration-major
version-integration-patch version-integration-minor version-integration-major: versioning/integration.cfg ## integration versioning as patch (bug fixes not affecting API/handling), minor/major (backwards-compatible/INcompatible API changes)
	@bump2version --verbose  --list --config-file $< $(subst version-integration-,,$@)




#---------------------------------------- running
# NOTE: since using docker-compose would create the folders automatically but as root user, which is inconvenient
define _clean_output_dirs
	# cleaning output directory
	rm -rf $(COMPOSE_OUTPUT_DIR)/*
endef
$(COMPOSE_OUTPUT_DIR):
	@$(_clean_output_dirs)
	mkdir -p $@
	# created output directory $(COMPOSE_OUTPUT_DIR)

docker-compose-configs = $(wildcard docker-compose.*yml)

.compose-production.yml .compose-development.yml: $(docker-compose-configs)
	# creating config for stack with 'local/$(DOCKER_IMAGE_NAME):$(patsubst .compose-%.yml,%,$@)' to $@
	@export DOCKER_REGISTRY=local; \
	export DOCKER_IMAGE_TAG=$(patsubst .compose-%.yml,%,$@); \
	docker-compose -f docker-compose.yml $(if $(findstring -development,$@), -f docker-compose.devel.yml,) --log-level=ERROR config > $@

.PHONY: down up up-devel shell shell-devel
up up-devel: $(COMPOSE_INPUT_DIR) $(COMPOSE_OUTPUT_DIR) down ## Starts the service for testing. Devel mode mounts the folders for direct development.
	$(MAKE) $(if $(findstring devel,$@),.compose-development.yml,.compose-production.yml)
	# starting service...
	@docker-compose -f $(if $(findstring devel,$@),.compose-development.yml,.compose-production.yml) up

shell shell-devel: $(COMPOSE_INPUT_DIR) $(COMPOSE_OUTPUT_DIR) down ## Starts a shell instead of running the container. Useful for development.
	$(MAKE) $(if $(findstring devel,$@),.compose-development.yml,.compose-production.yml)
	# starting service and go in...
	@docker-compose -f $(if $(findstring devel,$@),.compose-development.yml,.compose-production.yml) run {{ cookiecutter.project_slug }} /bin/sh

down: .compose-development.yml ## stops the service
	@docker-compose -f $< down
#----------------------------------------

.PHONY: push-release push
# target: push-release, push: – Pushes services to the registry if service not available in registry. push overwrites.
push-release: check-release check-pull push
	@$(call check-version-exists,$(DOCKER_IMAGE_TAG))

define check-version-exists
	$(shell docker pull "$(DOCKER_REGISTRY)"/"$(DOCKER_IMAGE_NAME)":"$(1)")
	if docker pull "$(DOCKER_REGISTRY)"/"$(DOCKER_IMAGE_NAME)":"$(1)"; then\
		echo "version $(1) does not exist";\
	else\
		echo "version $(1) already exists;\
	fi
endef

check-pull:
	# check if the service is already online
	@SERVICE_VERSION=$$(cat VERSION);\
	if docker pull \
		"${DOCKER_REGISTRY}"/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:"$$SERVICE_VERSION"; then\
		echo "image already in registry ${DOCKER_REGISTRY}";\
		false;\
	else \
		echo "no image available"; \
	fi;

check-release:
	# check if this is a releasable version number. Major shall be > 0
	@MAJOR_VERSION=$$(cut -f 1 -d '.' VERSION);\
	echo "$$MAJOR_VERSION";\
	if [ "$$MAJOR_VERSION" -eq 0 ] ; then \
		echo "Service major is below 1!!"; \
		false; \
	else\
		echo "Service is releasable";\
	fi

.PHONY: push-version push-latest pull-latest pull-version tag-latest
tag-latest:
	docker tag $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):latest

push-version:
	# pushing '$(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)'...
	@docker push $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)
	# pushed '$(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)'

push-latest: tag-latest ## tags service $(DOCKER_IMAGE_TAG) as latest and pushes
	@export DOCKER_IMAGE_TAG=latest;\
	$(MAKE) push-version

pull-latest: ## pull latest service version
	@docker pull $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):latest

pull-version: ## tries pull service $(DOCKER_IMAGE_TAG) if available
	-@docker pull $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)

# compatibility with gitlab CI
.PHONY: push pull
push: push-version push-latest ## publish service:latest and :$(DOCKER_IMAGE_TAG) tags
pull: pull-latest

#-----------------------------------
.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## this colorful help
	@echo "Recipes for '$(notdir $(CURDIR))':"
	@echo ""
	@awk --posix 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

git_clean_args = -dxf -e .vscode/ -e TODO.md -e .venv

.PHONY: clean clean-force
clean: ## cleans all unversioned files in project and temp files create by this makefile
	# Cleaning unversioned
	@$(git) clean -n $(git_clean_args)
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo -n "$(shell whoami), are you REALLY sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@$(git) clean $(git_clean_args)
