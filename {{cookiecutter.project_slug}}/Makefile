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

export VCS_URL:=$(shell git config --get remote.origin.url)
export VCS_REF:=$(shell git rev-parse --short HEAD)
export VCS_STATUS_CLIENT:=$(if $(shell git status -s),'modified/untracked','clean')
export BUILD_DATE:=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

export DOCKER_REGISTRY?={{ cookiecutter.default_docker_registry }}
export DOCKER_IMAGE_NAME?=simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}

INTEGRATION_VERSION=$(shell cat VERSION)
KERNEL_VERSION=$(shell cat src/{{cookiecutter.project_package_name}}/VERSION)

export DOCKER_IMAGE_TAG?=$(KERNEL_VERSION)-$(INTEGRATION_VERSION)

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
	pip-compile -v --output-file $@ $<

devenv: .venv requirements.txt ## create a python virtual environment with tools to dev, run and tests cookie-cutter
	# installing extra tools
	@$</bin/pip3 install -r  $(word 2,$^)
	# your dev environment contains
	@$</bin/pip3 list
	@echo "To activate the virtual environment, run 'source $</bin/activate'"


#-----------------------------------
.PHONY: build build-devel

metatada_dir = docker/labels
metadata_files = $(shell find $(metatada_dir) -type f -name '*.json')

service.cli/do_run: $(metatada_dir) $(metadata_files)
	# Updates adapter script from metadata in $<
	python3 tools/run_creator.py --folder $< --runscript $@

docker-compose-meta.yml: $(metatada_dir) $(metadata_files)
	# Injects metadata from $< as labels
	python3 tools/update_compose_labels.py --compose $@ --input $<

docker-compose.yml: docker-compose-base.yml docker-compose-meta.yml
	# Resolving $@ configuration
	docker-compose $(foreach c,$^,-f $(c)) --log-level=ERROR config > $@

build build-devel: docker-compose.yml service.cli/do_run ## builds images
	# building image local/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
	@DOCKER_REGISTRY=local; \
	docker-compose -f $< $(if $(subst build,,$@),-f docker-compose-devel.yml,) build --parallel
	# built local/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}


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

tests-unit tests-integration:
	pytest -vv \
		--exitfirst \
		--failed-first \
		--pdb \
		--junitxml=pytest_$(subst tests-,,$@)test.xml \
		$(CURDIR)/tests/$(subst tests-,,$@)

tests: tests-unit tests-integration ## runs unit and integration tests

#-----------------------------------
.PHONY: version-patch version-minor version-major
version-patch version-minor version-major: ## commits integration version as patch (bug fixes not affecting the API), minor/minor (backwards-compatible/INcompatible API addition or changes)
	# upgrades integration version as $(subst version-,,$@) version, commits and tags
	@bump2version --verbose  --list $(subst version-,,$@)




## TODO: Review ----------------------------------------

.PHONY: down up up-devel

down: docker-compose.yml
	@docker-compose -f $< down

up up-devel: docker-compose.yml down ## Starts/stops service
	@docker-compose -f $< $(if $(subst build,,$@),-f docker-compose-devel.yml,) up


.PHONY: push-release push
# target: push-release, push: – Pushes services to the registry if service not available in registry. push overwrites.
push-release: check-release check-pull push

check-pull:
	# check if the service is already online
	@${DOCKER} login ${DOCKER_REGISTRY};\
	SERVICE_VERSION=$$(cat VERSION);\
	${DOCKER} pull \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:$$SERVICE_VERSION; \
	if [ $$? -eq 0 ] ; then \
		echo "image already in registry ${DOCKER_REGISTRY}";\
		false;\
	else \
		echo "no image available"; \
	fi;

check-release:
	# check if this is a releasable version number. Major shall be > 0
	@MAJOR_VERSION=$$(cut -f 1 -d '.' VERSION);\
	echo $$MAJOR_VERSION;\
	if [ $$MAJOR_VERSION -eq 0 ] ; then \
		echo "Service major is below 1!!"; \
		false; \
	else\
		echo "Service is releasable";\
	fi

push:
	# push both latest and :$$SERVICE_VERSION tags
	${DOCKER} login ${DOCKER_REGISTRY};\
	SERVICE_VERSION=$$(cat VERSION);\
	${DOCKER} tag \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:latest \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:$$SERVICE_VERSION;\
	${DOCKER} push \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:$$SERVICE_VERSION;\
	${DOCKER} push \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:latest;

pull:
	# pull latest service version if available
	${DOCKER} pull \
		${DOCKER_REGISTRY}/simcore/services/{%- if cookiecutter.project_type == "computational" -%}comp{%- elif cookiecutter.project_type == "dynamic" -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:latest || true;

## TODO: Review above



#-----------------------------------
.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## this colorful help
	@echo "Recipes for '$(notdir $(CURDIR))':"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_ -]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

git_clean_args = -dxf -e .vscode/ -e TODO.md -e .venv

.PHONY: clean clean-force
clean: ## cleans all unversioned files in project and temp files create by this makefile
	# Cleaning unversioned
	@git clean -n $(git_clean_args)
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo -n "$(shell whoami), are you REALLY sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@git clean $(git_clean_args)
