#
# CONVENTIONS:
#
# - targets shall be ordered such that help list rensembles a typical workflow, e.g. 'make devenv tests'
# - add doc to relevant targets
# - internal targets shall start with '.'
# - KISS
#
SHELL = /bin/bash
.DEFAULT_GOAL := help



OUTPUT_DIR = $(CURDIR)/output
TEMPLATE = $(CURDIR)

#-----------------------------------
.PHONY: devenv
.venv:
	python3 -m venv $@
	$@/bin/pip3 install --upgrade \
		pip \
		wheel \
		setuptools

requirements.txt: requirements.in # Pip compile requirements.in
	$@/bin/pip3 install pip-tools
	pip-compile -v --output-file requirements.txt requirements.in

devenv: .venv requirements.txt ## create a python virtual environment with tools to dev, run and tests cookie-cutter
	# installing extra tools
	$</bin/pip3 install -r requirements.txt
	@echo "To activate the venv, execute 'source .venv/bin/activate'"


.PHONE: tests
tests: ## tests backed cookie
	@pytest -vv \
		-c $(CURDIR)/pytest.ini \
		--exitfirst \
		--failed-first \
		--durations=0 \
		--pdb \
		$(CURDIR)/tests

#-----------------------------------
.PHONY: play

$(OUTPUT_DIR):
	# creating $@
	@mkdir -p $@/packages
	@mkdir -p $@/services

define cookiecutterrc =
$(shell find $(OUTPUT_DIR) -name ".cookiecutterrc" | tail -n 1)
endef

play: $(OUTPUT_DIR) ## runs cookiecutter into output folder
ifeq (,$(cookiecutterrc))
	# baking cookie $(TEMPLATE) onto $</services
	@cookiecutter --output-dir "$</services" "$(TEMPLATE)"
else
	# replaying cookie-cutter using $(cookiecutterrc)
	@cookiecutter --no-input -f \
		--config-file="$(cookiecutterrc)"  \
		--output-dir="$</services" "$(TEMPLATE)"
endif


#-----------------------------------
.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## this colorful help
	@echo "Recipes for '$(notdir $(CURDIR))':"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

git_clean_args = -dxf -e .vscode/ -e TODO.md -e .venv

.PHONY: clean clean-force
clean: ## cleans all unversioned files in project and temp files create by this makefile
	# Cleaning unversioned
	@git clean -n $(git_clean_args)
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo -n "$(shell whoami), are you REALLY sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@git clean $(git_clean_args)

clean-force: clean
	# removing .venv
	-@rm -rf .venv